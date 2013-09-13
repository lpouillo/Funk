#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    
#    Funk: (F)ind (U)r (N)odes on G5(K)
#     Created by L. Pouilloux and M. Imbert (INRIA, 2013)
#
import logging

from pprint import pprint, pformat
from socket import getfqdn
from optparse import OptionParser, OptionGroup
from execo import logger
from execo.log import set_style
from execo_g5k.oar import oar_date_to_unixts, format_oar_date, oar_duration_to_seconds
import execo_g5k.api_utils as API
from execo_g5k.planning import *



logger = logging.getLogger('execo')
usage = "usage: %prog [-w WALLTIME] [-m MODE] [-r element1:n_nodes1,element2:n_nodes2]  "
description = '''This tool determine when the resources you need are available on '''+\
'''Grid'5000 platform thanks to the analysis of Gantt diagram obtained from API and '''+\
'''can (optionally) make the oargrid reservation.
                                                                                
                                                                    
                                                                        
Three modes (-m):                                                                                                                          
- '''+set_style('now', 'emph')+'''  = give you the number of nodes available                                                    
- '''+set_style('free', 'emph')+''' = find the slots for a combination of resources                                
- '''+set_style('max', 'emph')+'''  = find the maximum number of nodes for the period specified.
                             
                             
Require execo 2.2, http://execo.gforge.inria.fr/doc/
'''
epilog = """Examples :                        
                                  
    Finding the number of available nodes from now to now + walltime                    
    funk.py -w 1:00:00 -m now -r grid5000                        
                                  
    Finding the first free slots for a resource combination               
                                                              
    funk.py -w 2:00:00 -m free -r lille:10,lyon:10,sophia:10                          
                                  
    Finding the maximum number of nodes available for the resource and with a KaVLAN                        
                                              
    funk.py -w 10:00:00 -m max -r lyon,sophia,edel -k  
"""

parser = OptionParser(usage = usage, description = description, epilog = epilog)

optinout= OptionGroup(parser, "General options", "Define mode and controls I/O.")
optinout.add_option("-m", "--mode",
                dest = "mode", 
                default = 'now',
                help = "Setup the mode: now, free or max (%default)")
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
optreservation.add_option("-o", "--oargridsub_options", 
                dest = "oargridsub_opts", 
                default = "-t deploy",    
                help = "Extra options to pass to the oargridsub command line (%default)")

parser.add_option_group(optreservation)

opttime= OptionGroup(parser, "Time", "Define options related to date and time.")
opttime.add_option("-w", "--walltime", 
                dest = "walltime", 
                default = '1:00:00',    
                help = "reservation walltime (%default)")
opttime.add_option("-s", "--startdate", 
                dest = "startdate", 
                default = format_oar_date(int(time()+timedelta_to_seconds(timedelta(minutes = 0.5)))),    
                help = "Starting date in OAR date format (%default)")
opttime.add_option("-e", "--enddate", 
                dest = "enddate", 
                default = format_oar_date(int(time()+timedelta_to_seconds(timedelta(days = 3, minutes = 1)))),    
                help = "End date in OAR date format (%default)")

parser.add_option_group(opttime)
(options, args) = parser.parse_args()



        

if options.verbose:
    logger.setLevel(logging.DEBUG)
elif options.quiet:
    logger.setLevel(logging.WARN)
else:
    logger.setLevel(logging.INFO)

logger.debug(pformat(options))

if len(args) == 1:
    prog = args[0]
else:
    prog = None



logger.info('%s', set_style('-- Find yoUr Nodes on g5K --', 'log_header'))
logger.info('From %s to %s', set_style(options.startdate, 'emph'), 
            set_style(options.enddate, 'emph'))
if options.resources is None:
    options.resources = 'suno:2,sol:2,griffon:10,rennes:20'
    logger.warning('No resources given, will use demo values ')

logger.info('Resources: %s', set_style(options.resources, 'emph'))
logger.info('Walltime: %s', set_style(options.walltime, 'emph'))
logger.info('Mode: %s', set_style(options.mode, 'emph'))
if prog is not None:
    logger.info('Program: %s', set_style(prog, 'emph'))
    
if options.plots:
    if 'grid5000.fr' in getfqdn():
        options.plots = False
        logger.warning('Plots are disabled on Grid5000 frontend until the migration to Wheezy')
    

resources = {}
for element in options.resources.split(','):
    if ':' in element:
        element_uid, n_nodes = element.split(':')
    elif options.mode != 'free': 
        element_uid, n_nodes = element, 0
    else:
        logger.error('You must specify the number of host element:n_nodes when using free mode')
        exit()
    resources[element_uid] = int(n_nodes)


planning = Planning(resources, 
                    oar_date_to_unixts(options.startdate), 
                    oar_date_to_unixts(options.enddate), 
                    options.kavlan_global)

planning.compute()


if options.plots:
    draw_gantt(planning.planning)


planning.compute_slots(options.walltime)

logger.debug(planning.slots)

if options.plots:
    draw_slots(planning.slots, oar_date_to_unixts(options.enddate))

if options.mode == 'now':
    resources = planning.slots[0][2]
    startdate = planning.slots[0][0]
    
elif options.mode == 'max':
    max_slot = planning.find_max_slot(options.walltime, resources)
    resources = max_slot[2]
    startdate = format_oar_date(max_slot[0])
elif options.mode == 'free':
    free_slots = planning.find_free_slots(options.walltime, resources)
    if len(free_slots) ==0:
        logger.error('Unable to find a slot for your resources:\n%s', pformat(resources))
        exit()
    startdate = format_oar_date(free_slots[0][0])
    distribute_hosts(free_slots[0], resources)
else:
    logger.error('Mode '+options.mode+' is not supported, funk -h for help')

log = set_style('Resources', 'log_header')
for site in get_g5k_sites():
    if site in resources.keys():
        log += '\n'+set_style(site, 'log_header').ljust(20)+' '+str(resources[site])+'\n'
        for cluster in get_site_clusters(site):
            if cluster in resources.keys():
                log += set_style(cluster, 'emph')+': '+str(resources[cluster])+'  '
logger.info(log)

oargrid_job_id = create_reservation(startdate, resources, options.walltime, auto_reservation = options.yes, prog = prog)


if oargrid_job_id is not None:
    log = set_style('Jobs', 'log_header')
    jobs = get_oargrid_job_oar_jobs(oargrid_job_id)
    for job_id, site in jobs:
        log += '\n'+set_style(site, 'emph').ljust(25)+str(job_id).rjust(9)
    logger.info(log)



    
    
