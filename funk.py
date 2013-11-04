#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    
#    Funk: (F)ind (U)r (N)odes on G5(K)
#     Created by L. Pouilloux and M. Imbert (INRIA, 2013)
#
import logging, os
from pprint import pprint, pformat
from socket import getfqdn
from optparse import OptionParser, OptionGroup
from execo import logger, Local
from execo.time_utils import sleep
from execo.log import style
from execo_g5k.oar import oar_date_to_unixts, format_oar_date, oar_duration_to_seconds
import execo_g5k.api_utils as API
from execo_g5k.planning import *



usage = "usage: %prog [-w WALLTIME] [-m MODE] [-r element1:n_nodes1,element2:n_nodes2]  "
description = '''This tool determine when the resources you need are available on '''.ljust(100)+\
    '''Grid'5000 platform thanks to the analysis of Gantt diagram obtained  '''.ljust(100)+\
    '''from API and can make the oargrid reservation. It has three modes'''.ljust(100)+\
    ''' - '''+style.emph('date')+'''  = give you the number of nodes available (default)                                                    
  - '''+style.emph('free')+''' = find the slots for a combination of resources                                
  - '''+style.emph('max')+'''  = find the maximum number of nodes for the period specified.'''.ljust(100)+\
 '''                             
 Require execo 2.2, http://execo.gforge.inria.fr/doc/
 '''
epilog = """Examples :                        
                                  
    Finding the number of available nodes from date to date + walltime                    
    funk.py -w 1:00:00 -m date -r grid5000                        
                                  
    Finding the first free slots for a resource combination               
                                                              
    funk.py -w 2:00:00 -m free -r lille:10,lyon:10,sophia:10                          
                                  
    Finding the maximum number of nodes available for the resource and with a KaVLAN                        
                                              
    funk.py -w 10:00:00 -m max -r lyon,sophia,edel -k  
"""

parser = OptionParser(usage = usage, description = description, epilog = epilog)

optinout= OptionGroup(parser, "General options", "Define mode and controls I/O.")
optinout.add_option("-m", "--mode",
                dest = "mode", 
                default = 'date',
                help = "Setup the mode: date, free or max (%default)")
optinout.add_option("-y", "--yes",
                action = "store_true", 
                dest = "yes", 
                default = False,
                help = "Perform the reservation automatically (%default)")
optinout.add_option("-q", "--quiet", 
                dest = "quiet",
                action = "store_true", 
                default = False,    
                help = "Run without printing anything (%default)")
optinout.add_option("-v", "--verbose", 
                dest = "verbose",
                action = "store_true", 
                default = False,    
                help = "Run in verbose mode (%default)")
optinout.add_option("-p", "--plots", 
                dest = "plots",
                action = "store_true", 
                default = False,    
                help = "Draw plots (gantt, free, max) (%default)")
optinout.add_option("-R", "--ratio",
                dest = "ratio",
                type = "float",
                default = None,
                help = "reserve the given ratio of the resources")
optinout.add_option("-c", "--charter",
                dest = "charter",
                default = False,
                action = "store_true",
                help = "avoid charter periods")

parser.add_option_group(optinout)

optreservation = OptionGroup(parser, "Resources", "Customize your Grid'5000 topology.")
optreservation.add_option("-r", "--resources", 
                dest="resources", 
                default = "grid5000",
                help = "comma separated list of 'element1:n_nodes1,element2:n_nodes2', element can be a cluster, site or grid5000")
#optreservation.add_option("-n", "--subnet", 
#                dest = "subnet", 
#                default = None,    
#                help="Ask for a vlan (%default)")
optreservation.add_option("-k", "--kavlan", 
                dest = "kavlan_global", 
                action = "store_true",
                default = False,    
                help="Ask for a KaVLAN global (%default)")
optreservation.add_option("-o", "--oargridsub_opts", 
                dest = "oargridsub_opts", 
                help = "Extra options to pass to the oargridsub command line (%default)")
optreservation.add_option("--blacklist", 
                dest = "blacklist", 
                help = "Blacklist some clusters")

parser.add_option_group(optreservation)

opttime= OptionGroup(parser, "Time", "Define options related to date and time.")
opttime.add_option("-w", "--walltime", 
                dest = "walltime", 
                default = '1:00:00',    
                help = "reservation walltime (%default)")
opttime.add_option("-s", "--startdate", 
                dest = "startdate", 
                default = format_oar_date(int(time()+timedelta_to_seconds(timedelta(minutes = 1)))),    
                help = "Starting date in OAR date format (%default)")
opttime.add_option("-e", "--enddate", 
                dest = "enddate", 
                default = format_oar_date(int(time()+timedelta_to_seconds(timedelta(days = 3, minutes = 1)))),    
                help = "End date in OAR date format (%default)")

parser.add_option_group(opttime)
(options, args) = parser.parse_args()

logger.debug('Options\n'+'\n'.join( [ style.emph(option.ljust(20))+\
                    '= '+str(value).ljust(10) for option, value in vars(options).iteritems() if value is not None ]))

# The first arugment of the script is the program to launch after the oargridsub command 
prog = args[0] if len(args) == 1 else None

if options.verbose:
    logger.setLevel(logging.DEBUG)
elif options.quiet:
    logger.setLevel(logging.WARN)
else:
    logger.setLevel(logging.INFO)

logger.debug('Options\n'+'\n'.join( [ style.emph(option.ljust(20))+\
                    '= '+str(value).ljust(10) for option, value in vars(options).iteritems() if value is not None ]))





logger.info('%s', style.log_header('-- Find yoUr Nodes on g5K --'))
logger.info('From %s to %s', style.emph(options.startdate), 
            style.emph(options.enddate))

if options.resources is None:
    options.resources = 'suno:2,sol:2,griffon:10,rennes:20'
    logger.warning('No resources given, will use demo values ')

logger.info('Resources: %s', style.emph(options.resources))
logger.info('Walltime: %s', style.emph(options.walltime))
logger.info('Mode: %s', style.emph(options.mode))
if prog is not None:
    logger.info('Program: %s', style.emph(prog))
    
if options.plots:
    if 'grid5000.fr' in getfqdn():
        options.plots = False
        logger.warning('Plots are disabled on Grid5000 frontend until the migration to Wheezy')
    

resources_wanted = {}
for element in options.resources.split(','):
    if ':' in element:
        element_uid, n_nodes = element.split(':')
    elif options.mode != 'free': 
        element_uid, n_nodes = element, 0
    else:
        logger.error('You must specify the number of host element:n_nodes when using free mode')
        exit()
    resources_wanted[element_uid] = int(n_nodes)

planning = Planning(resources_wanted, 
                    oar_date_to_unixts(options.startdate), 
                    oar_date_to_unixts(options.enddate), 
                    options.kavlan_global)

planning.compute(out_of_chart = options.charter)



if options.plots:
    draw_gantt(planning.planning)

planning.compute_slots(options.walltime)

logger.debug(planning.slots)


if options.plots:
    draw_slots(planning.slots, oar_date_to_unixts(options.enddate))

if options.mode == 'date':
    resources = planning.slots[0][2]
    startdate = planning.slots[0][0]
    
elif options.mode == 'max':
    max_slot = planning.find_max_slot(options.walltime, resources_wanted)
    resources = max_slot[2]
    startdate = format_oar_date(max_slot[0])
elif options.mode == 'free':
    free_slots = planning.find_free_slots(options.walltime, resources_wanted)
    if len(free_slots) == 0:
        logger.error('Unable to find a slot for your resources:\n%s', pformat(resources_wanted))
        exit()
    startdate = format_oar_date(free_slots[0][0])
    resources = distribute_hosts(free_slots[0], resources_wanted)
    
else:
    logger.error('Mode '+options.mode+' is not supported, funk -h for help')
    exit()

def show_resources(resources):
    total_hosts = 0
    log = style.log_header('Resources')
    for site in get_g5k_sites():
        if site in resources.keys():
            total_hosts += resources[site]
            log += '\n'+style.log_header(site).ljust(20)+' '+str(resources[site])+'\n'
            for cluster in get_site_clusters(site):
                if cluster in resources.keys():
                    total_hosts += resources[cluster]
                    log += style.emph(cluster)+': '+str(resources[cluster])+'  '
    logger.info(log)
    logger.info(style.log_header('total hosts: ') + str(total_hosts))


show_resources(resources)

if options.blacklist is not None:
    remove_nodes = 0
    for element in options.blacklist.split(','):
        if element in resources:
            if element in get_g5k_clusters():
                remove_nodes += resources[element]
                resources[get_cluster_site(element)] -= resources[element]
                del resources[element]
            if element in get_g5k_sites():
                for cluster in get_site_clusters(element):
                    remove_nodes += resources[cluster]
                    del resources[cluster]
                
                del resources[element]
    if 'grid5000' in resources:
        resources['grid5000'] -= remove_nodes
    logger.info("after removing blacklisted elements %s, actual resources reserved:" % (options.blacklist,))
    show_resources(resources)

if options.ratio:
    for site in get_g5k_sites():
        if site in resources.keys():
            tmp_total_site_nodes = 0
            for cluster in get_site_clusters(site):
                if cluster in resources.keys():
                    resources[cluster] = int(resources[cluster] * options.ratio)
                    tmp_total_site_nodes += resources[cluster]
            if resources_wanted.has_key(site):
                resources[site] = int(resources_wanted[site] * options.ratio)
            else:
                resources[site] = tmp_total_site_nodes
    logger.info("after applying ratio %f, actual resources reserved:" % (options.ratio,))
    show_resources(resources)

oargrid_job_id = create_reservation(startdate,
                                    resources,
                                    options.walltime,
                                    oargridsub_opts = options.oargridsub_opts,
                                    auto_reservation = options.yes,
                                    prog = prog)

if oargrid_job_id is None:
    exit(1)
else:
    log = style.log_header('Jobs')
    jobs = get_oargrid_job_oar_jobs(oargrid_job_id)
    for job_id, site in jobs:
        log += '\n'+style.emph(site).ljust(25)+str(job_id).rjust(9)
    logger.info(log)
    exit(oargrid_job_id)



    
    
