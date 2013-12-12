#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    
#    Funk: (F)ind (U)r (N)odes on G5(K)
#     Created by L. Pouilloux and M. Imbert (INRIA, 2013)
#
from argparse import ArgumentParser, RawTextHelpFormatter
from time import time
from datetime import timedelta
from execo import logger
from execo.log import style
from execo_g5k.api_utils import get_g5k_sites, get_site_clusters
from execo_g5k.planning import show_resources, get_planning, compute_slots, draw_gantt, \
    find_first_slot, find_max_slot, find_free_slot, get_jobs_specs, distribute_hosts
from execo_g5k.oargrid import get_oargridsub_commandline, get_oargrid_job_oar_jobs, get_oargrid_job_key, oargridsub
from execo_g5k.oar import oar_duration_to_seconds, format_oar_date, oar_date_to_unixts, get_oarsub_commandline, oarsub
from execo.time_utils import timedelta_to_seconds

# Defining and anlyzing program options 
prog = 'funk'
description = 'This tool helps you to find resources on '+\
    style.log_header("Grid'5000")+' platform. It has three modes: \n - '+\
    style.host('date')+' = give you the number of nodes available at a given date, \n - '+\
    style.host('free')+' = find the next free slot for a combination of resources, \n - '+\
    style.host('max')+'  = find the maximum number of nodes for the period specified.\n\n'+\
    """If no arguments is given, compile the planning of the whole platform and generate an 
    oargridsub command line with all available resources for 1 hour. 
    Based on execo 2.2, """+style.emph('http://execo.gforge.inria.fr/doc/')+""", 
    oar 2.5, """+style.emph('http://oar.imag.fr')+""" 
    and the Grid'5000 Job API, """+style.emph('https://api.grid5000.fr')+'.'
    
epilog = style.host('Examples:')+\
    '\nNumber of available nodes on stremi cluster from date to date + walltime \n'+\
    style.command('  %(prog)s -m date -s "'+\
    format_oar_date(int(time()+timedelta_to_seconds(timedelta( minutes = 1))))+'" -r stremi\n')+\
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
optinout.add_argument("--plots",
                dest = "plots",
                action = "store_true",
                help = "Draw a Gantt plot and the slots")

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
                dest = "submission_opts", 
                help = "Extra options to pass to the oarsub/oargridsub command line")
optreservation.add_argument("-k", "--kavlan", 
                dest = "kavlan", 
                action = "store_true",
                default = False,    
                help="Ask for a KaVLAN")
optreservation.add_argument("-n", "--subnet", 
                dest = "subnet",    
                help="Ask for subnets. slash_22=1 will retrieve a /22 subnet on every site of your requests, "+\
                "but you can specify site1:slash_22=2,site2:slash_19=1")
#optreservation.add_argument("-d", "--storage", 
#                dest = "storage",    
#                help="Ask for storage")
# Subnet and storage computation not implemented
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
logger.info('%s', style.log_header('-- Find yoUr Nodes on g5K --'))
# Checking options valuers
logger.debug('Options\n %s', '\n'.join( [ style.emph(option.ljust(20))+\
                '= '+str(value).ljust(10) for option, value in vars(args).iteritems() if value is not None ]))

if args.prog is not None:
    logger.info('Program: %s', style.emph(args.prog))
# Creating resources dict from command line options resources (-r)
resources_wanted = {}
for element in args.resources.split(','):
    if args.mode == 'free':
        if not ':' in element:
            logger.error('You must specify the number of host element:n_nodes when using free mode')
            exit()
        else:
            element_uid, n_nodes = element.split(':')
            
    else:
        if ':' in element:
            logger.warning('You give a resource element:n_nodes corresponding to a '+style.emph('free')+' mode ! ')
            switch_mode = raw_input('Do you want to switch to free mode (y/[N]): ')
            if switch_mode == 'y':
                args.mode = 'free'
                element_uid, n_nodes = element.split(':')
            else:
                logger.warning('The number of nodes specified will be ignored ...')
                element_uid, n_nodes = element.split(':')[0], 0
        else:
            element_uid, n_nodes = element, 0
    resources_wanted[element_uid] = int(n_nodes)
    
blacklisted = []    
if args.blacklist is not None:
    for element in args.blacklist.split(','):    
        blacklisted.append(element)

# Adding network elements
if args.kavlan:
    resources_wanted['kavlan'] = 1
    
#if args.subnet:
#    resources_wanted['subnets'] = args.subnet
#    logger.warning('subnet is not implemented in execo_g5k.planning, '+\
#                   'we cannot assure that the requested resources will be availables')
#    subnet = True
#else:
#    subnet = False
#if args.storage:
#    resources_wanted['storage'] = args.storage
#    logger.warning('storage is not implemented in execo_g5k.planning, '+\
#                   'we cannot assure that the requested resources will be availables')
#    storage = True
#else:
#    storage = False
    

logger.info('From %s to %s', style.emph(args.startdate), style.emph(args.enddate))
logger.info('Walltime: %s', style.emph(args.walltime))
logger.info('Mode: %s', style.emph(args.mode))
show_resources({ resource: n_nodes for resource, n_nodes in resources_wanted.iteritems() },
                 'Wanted resources')

# Computing the planning of the ressources wanted
logger.info('Compiling planning')
planning = get_planning(elements = resources_wanted.keys(), 
            vlan = args.kavlan, 
            subnet = False, 
            storage = False, 
            out_of_chart = args.charter, 
            starttime = int(oar_date_to_unixts(args.startdate)), 
            endtime = int(oar_date_to_unixts(args.enddate)))
# Determing the slots for the given walltime, i.e. finding the slice of time with constant resources
logger.info('Calculating slots of %s ', args.walltime)

slots = compute_slots(planning, args.walltime, excluded_resources = blacklisted)


if args.plots:
    logger.info('Drawing plots ')
    draw_gantt(planning, outfile = "funk_gantt.png")
    
# Determine the slot to use
if args.mode == 'date':
    # In date mode, funk take the first slot available for the wanted walltime
    startdate, enddate, resources = find_first_slot( slots, resources_wanted )

elif args.mode == 'max':
    # In max mode, funk take the slot available with the maximum number of resources 
    startdate, enddate, resources = find_max_slot( slots, resources_wanted )
    
elif args.mode == 'free':
    # In free mode, funk take the first slot that match your resources    
    startdate, enddate, resources = find_free_slot( slots, resources_wanted )

if startdate is None:
    logger.error('Unable to find a slot for your requests.')
    exit()
else:
    logger.info('A slot has been found at %s', format_oar_date(startdate))


show_resources(resources, 'Resources available')


resources = distribute_hosts(resources, resources_wanted, blacklisted)
show_resources(resources, 'Resources distributed')


logger.info(style.log_header('Chosen slot ')+format_oar_date(startdate)+' -> '+format_oar_date(enddate))

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
    show_resources(resources)

jobs_specs = get_jobs_specs(resources, excluded_elements = blacklisted, name = args.job_name)

if args.subnet:
    subnets = {}
    sites_nets = args.subnet.split(',')
    if len(sites_nets) == 1:
        subnet_param = args.subnet.split(':')
        if len(subnet_param) == 1:
            subnets = {site: subnet_param[0] for site in get_g5k_sites()}
        else:
            subnets = {subnet_param[0]: subnet_param[1]}
    else:
        for site_param in sites_nets:
            site, param = site_param.split(':')
            subnets[site] = param
    # ADDING THE subnet to resources
    for OarSubmission, frontend in jobs_specs:

        if subnets.has_key(frontend):
            OarSubmission.resources = subnets[frontend]+'+'+OarSubmission.resources

if args.prog is not None:
    args.submission_opts += ' -p '+args.prog

if len(jobs_specs) == 1:
    # If there's only one site, we performe an OAR submission
    frontend = jobs_specs[0][1]
    sub = jobs_specs[0][0]
# FIX A BUG WITH SQL ESCAPE
    
    _list = sub.resources.split('\\')
    tmp = _list[:]
    i_char = 0
    for char in tmp:
        if char == '':
            _list.pop(i_char)
        else:
            i_char += 1

    sub.resources = ''.join(_list)
    
    sub.walltime = args.walltime
    sub.additional_options = args.submission_opts
    sub.reservation_date = format_oar_date(startdate)
    cmd = get_oarsub_commandline(sub)
    job_specs = (sub, frontend)

elif len(jobs_specs) > 1:
    cmd = get_oargridsub_commandline(jobs_specs, walltime = args.walltime, 
         additional_options = args.submission_opts, reservation_date = format_oar_date(startdate))
    oar_grid_job_id = None


logger.info('Reservation command: \n\033[1m%s\033[0m', cmd)

if args.yes:            
    reservation = 'y'
else:            
    reservation = raw_input('Do you want me to do the reservation (y/[N]): ')


oar_job_id, oar_grid_job_id = None, None
if reservation in [ 'y', 'Y', 'yes'] :
    if len(jobs_specs) == 1:
        (oar_job_id, frontend) = oarsub([job_specs])[0]
    else:
        (oargrid_job_id, _) = oargridsub(jobs_specs, walltime = args.walltime, 
         additional_options = args.submission_opts, reservation_date = format_oar_date(startdate)) 
    if oar_job_id is not None:
        logger.info('Reservation done on %s, oar_job_id = %s', style.emph(frontend), oar_job_id)
    elif oargrid_job_id is not None:
        logger.info('Grid reservation done, oargrid_job_id = %s',oargrid_job_id)
        log = style.log_header('Jobs')
        jobs = get_oargrid_job_oar_jobs(oargrid_job_id)
        for job_id, site in jobs:
            log += '\n'+style.emph(site).ljust(25)+str(job_id).rjust(9)
        log += '\n'+style.emph('Key file: ')+get_oargrid_job_key(oargrid_job_id)
        logger.info(log)
        exit(oargrid_job_id)
    else:
        logger.error('Error in performing the reservation ')
        exit(1)
else:
    logger.info('Aborting reservation ...')





    
    
