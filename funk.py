#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    
#    Funk: (F)ind (U)r (N)odes on G5(K)
#     Created by L. Pouilloux and M. Imbert (INRIA, 2013)
#
from argparse import ArgumentParser, RawTextHelpFormatter
from pprint import pprint, pformat
from execo import logger
from execo.log import style
from execo_g5k.oargrid import get_oargrid_job_key, get_oargrid_job_oar_jobs
from execo_g5k.planning import *
from execo_g5k.oar import oar_duration_to_seconds, format_oar_date, oar_date_to_unixts

# Defining and anlyzing program options 
prog = 'funk'
description = 'This tool helps you to find resources on '+\
    style.log_header("Grid'5000")+' platform. It has three modes: \n - '+\
    style.host('date')+' = give you the number of nodes available at a given date, \n - '+\
    style.host('free')+' = find the next free slot for a combination of resources, \n - '+\
    style.host('max')+'  = find the maximum number of nodes for the period specified.\n\n'+\
    'If no arguments is given, compile the planning of the whole platform and generate an '+\
    'oargridsub command line with all available resources for 1 hour. \n'+\
    'Based on execo 2.2, '+style.emph('http://execo.gforge.inria.fr/doc/')+' and the Grid\'5000 Job API, '+\
    style.emph('https://api.grid5000.fr')+'.'
epilog = style.host('Examples:')+\
    '\nNumber of available nodes on stremi cluster from date to date + walltime \n'+\
    style.command('  %(prog)s -m date -s "'+\
    format_oar_date(int(time()+timedelta_to_seconds(timedelta(days = 3, minutes = 1))))+'" -r stremi\n')+\
    'First free slots for a resource combination with deploy job type and a KaVLAN\n'+\
    style.command('  %(prog)s -m free -w 2:00:00 -r grid5000:100,taurus:4 -o "-t deploy" -k\n')+\
    'Maximum number of nodes available for the resources, avoiding charter periods\n'+\
    style.command('  %(prog)s -m max -w 10:00:00 -r nancy,paradent,edel -c \n')+\
    'Issues/features requests can be reported to '+style.emph('https://github.com/lpouillo/Funk')

parser = ArgumentParser( prog = prog, 
                         description = description, 
                         epilog = epilog, 
                         formatter_class = RawTextHelpFormatter,
                         add_help = False)

optinout = parser.add_argument_group( style.host("General options"),
                "Define mode and controls I/O.")
optinout.add_argument("-h", "--help", 
                action = "help", 
                help = "show this help message and exit")
optinout.add_argument("-m", "--mode",
                dest = "mode", 
                default = 'date',
                help = "Setup the mode: date, free or max "+\
                    "\ndefault = %(default)s")
optinout.add_argument("-y", "--yes",
                action = "store_true", 
                dest = "yes", 
                default = False,
                help = "Perform the reservation automatically")
optio = optinout.add_mutually_exclusive_group()
optio.add_argument("-q", "--quiet", 
                dest = "quiet",
                action = "store_true", 
                default = False,    
                help = "Run without printing anything")
optio.add_argument("-v", "--verbose", 
                dest = "verbose",
                action = "store_true", 
                default = False,    
                help = "Run in verbose mode")
optinout.add_argument("-p", "--prog", 
                dest = "prog",     
                help = "The program to be run when the reservation start")

optreservation = parser.add_argument_group(style.host("Reservation"), 
                "Customize your Grid'5000 reservation.")
optreservation.add_argument("-r", "--resources", 
                dest="resources", 
                default = "grid5000",
                help = "Comma separated list of Grid'5000 elements (grid5000, site or cluster)"\
                    "\n-r element1,element2 for date and max modes"+\
                    "\n-r element1:n_nodes1,element2:n_nodes2 for free mode"+\
                    "\ndefault = %(default)s")
optreservation.add_argument("-b", "--blacklist", 
                dest = "blacklist", 
                help = "Remove clusters from planning computation")
optreservation.add_argument("-R", "--ratio",
                dest = "ratio",
                type = float,
                default = None,
                help = "Apply a given ratio to the resources found, works only for mode date and max")
optreservation.add_argument("-o", "--oargridsub_opts", 
                dest = "oargridsub_opts", 
                help = "Extra options to pass to the oargridsub command line")
optreservation.add_argument("-k", "--kavlan", 
                dest = "kavlan", 
                action = "store_true",
                default = False,    
                help="Ask for a KaVLAN")
# Subnet option not implemented in new execo_g5k.planning 
#optreservation.add_argument("-n", "--subnet", 
#                dest = "subnet",    
#                help="Ask for a subnet")
optreservation.add_argument("-j", "--job_name", 
                dest = "job_name", 
                default = "FUNK",    
                help="The job name passed to the OAR subjobs"+\
                    "\ndefault = %(default)s")

opttime= parser.add_argument_group(style.host("Time"), "Define options related to date and time.")
opttime.add_argument("-w", "--walltime", 
                dest = "walltime", 
                default = '1:00:00',    
                help = "Reservation walltime in OAR format"+\
                    "\ndefault = %(default)s")
opttime.add_argument("-s", "--startdate", 
                dest = "startdate", 
                default = format_oar_date(int(time()+timedelta_to_seconds(timedelta(minutes = 1)))),    
                help = "Starting date in OAR format"+\
                    "\ndefault = %(default)s")
opttime.add_argument("-e", "--enddate", 
                dest = "enddate", 
                default = format_oar_date(int(time()+timedelta_to_seconds(timedelta(weeks = 3, minutes = 1)))),    
                help = "End date in OAR format"+\
                    "\ndefault = %(default)s")
opttime.add_argument("-c", "--charter",
                dest = "charter",
                default = False,
                action = "store_true",
                help = "Avoid charter periods")

args = parser.parse_args()

if args.verbose:
    logger.setLevel('DEBUG')
elif args.quiet:
    logger.setLevel('WARN')
else:
    logger.setLevel('INFO')

# Printing welcome message
logger.debug('Options\n'+'\n'.join( [ style.emph(option.ljust(20))+\
                    '= '+str(value).ljust(10) for option, value in vars(args).iteritems() if value is not None ]))
log_endate = args.enddate if args.mode is not 'date' else format_oar_date( oar_date_to_unixts(args.startdate) + oar_duration_to_seconds(args.walltime))
logger.info('%s', style.log_header('-- Find yoUr Nodes on g5K --'))
logger.info('From %s to %s', style.emph(args.startdate), 
            style.emph(log_endate))
logger.info('Resources: %s', style.emph(args.resources))
logger.info('Walltime: %s', style.emph(args.walltime))
logger.info('Mode: %s', style.emph(args.mode))
if args.prog is not None:
    logger.info('Program: %s', style.emph(args.prog))
    
# Creating resources dict from command line options
if args.blacklist is not None:
    blacklisted = args.blacklist.split(',')
else:
    blacklisted = []
    
resources_wanted = {}
for element in args.resources.split(','):
    if ':' in element:
        element_uid, n_nodes = element.split(':')
    elif args.mode != 'free': 
        element_uid, n_nodes = element, 0
    else:
        logger.error('You must specify the number of host element:n_nodes when using free mode')
        exit()    
    if element_uid not in blacklisted:
        resources_wanted[element_uid] = int(n_nodes)

if args.kavlan:
    resources_wanted['kavlan'] = 1


# Computing the planning of the ressources wanted
planning = get_planning(elements = resources_wanted.keys(), vlan = args.kavlan, subnet = False, storage = False, 
            out_of_chart = args.charter, starttime = int(oar_date_to_unixts(args.startdate)), 
            endtime = int(oar_date_to_unixts(args.enddate)))


slots = compute_slots(planning, args.walltime)

print resources_wanted

# Determine the slot to use
if args.mode == 'date':
    # In date mode, funk take the first slot available for the wanted walltime
    slot = find_first_slot( slots, resources_wanted.keys())
    startdate = slot[0]
    resources = slot[2] 
    if resources_wanted.has_key('grid5000'):
        resources_wanted['grid5000'] = resources['grid5000']
        resources = distribute_hosts_grid5000(resources, resources_wanted)
    
elif args.mode == 'max':
    # In max mode, funk take the slot available with the maximum number of resources 
    max_slot = find_max_slot(slots, resources_wanted.keys())
    startdate = max_slot[0]
    resources = { element: n_nodes for element, n_nodes in max_slot[2].iteritems() 
                 if element in resources_wanted.keys() }
    
    if resources.has_key('grid5000'):
        resources = distribute_hosts_grid5000(max_slot[2], resources)
    
elif args.mode == 'free':
    # In free mode, funk take the first slot that match your resources    
    free_slots = find_free_slots(slots, resources_wanted)
    if len(free_slots) == 0:
        logger.error('Unable to find a slot for your resources:\n%s', 
                     pformat(resources_wanted))
        exit()
    startdate = free_slots[0][0]
    resources = resources_wanted

    if resources.has_key('grid5000'):
        resources = distribute_hosts_grid5000(free_slots[0][2], resources_wanted)
    
else:
    # No other modes supported
    logger.error('Mode '+args.mode+' is not supported, funk -h for help')
    exit()


# Showing the resources available
def show_resources(resources, mode):
    total_hosts = 0
    log = style.log_header('Resources')
    for site in get_g5k_sites():
        if site in resources.keys():
            total_hosts += resources[site]
            log += '\n'+style.log_header(site).ljust(20)+' '+str(resources[site])+'\n'
            for cluster in get_site_clusters(site):
                if cluster in resources.keys():
                    if mode == 'free':
                        total_hosts += resources[cluster]
                        log += style.emph(cluster)+': '+str(resources[cluster])+'  '
    logger.info(log)
    logger.info(style.log_header('total hosts: ') + str(total_hosts))

show_resources(resources, args.mode)

if args.blacklist is not None:
    remove_nodes = 0
    for element in args.blacklist.split(','):
        if element in resources:
            if element in get_g5k_clusters():
                remove_nodes += resources[element]
                resources[get_cluster_site(element)] -= resources[element]
                del resources[element]
            if element in get_g5k_sites():
                for cluster in get_site_clusters(element):
                    if cluster in resources:
                        remove_nodes += resources[cluster]
                        del resources[cluster]        
                del resources[element]
        if 'kavlan' in resources and element in resources['kavlan']:
            resources['kavlan'].remove(element)
    if 'grid5000' in resources:
        resources['grid5000'] -= remove_nodes
    logger.info("After removing blacklisted elements %s, actual resources reserved:" % (args.blacklist,))
    show_resources(resources, args.mode)

if args.ratio:
    for site in get_g5k_sites():
        if site in resources.keys():
            tmp_total_site_nodes = 0
            for cluster in get_site_clusters(site):
                if cluster in resources.keys(): 
                    resources[cluster] = int(resources[cluster] * args.ratio)
                    tmp_total_site_nodes += resources[cluster]
            if resources_wanted.has_key(site):
                resources[site] = int(resources_wanted[site] * args.ratio)
            else:
                resources[site] = tmp_total_site_nodes
    logger.info("After applying ratio %f, actual resources reserved:" % (args.ratio,))
    show_resources(resources, args.mode)




# Creating the reservation

    
oargrid_job_id = create_reservation(startdate,
                                    resources,
                                    args.walltime,
                                    oargridsub_opts = args.oargridsub_opts,
                                    auto_reservation = args.yes,
                                    prog = args.prog,
                                    name = args.job_name)

if oargrid_job_id is None:
    exit(1)
else:
    log = style.log_header('Jobs')
    jobs = get_oargrid_job_oar_jobs(oargrid_job_id)
    for job_id, site in jobs:
        log += '\n'+style.emph(site).ljust(25)+str(job_id).rjust(9)
    log += '\n'+style.emph('Key file: ')+get_oargrid_job_key(oargrid_job_id)
    logger.info(log)
    exit(oargrid_job_id)



    
    
