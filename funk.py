#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    
#    Funk: (F)ind (U)r (N)odes on G5(K)
#     Created by L. Pouilloux and M. Imbert (INRIA, 2013)
#
import logging
from pprint import pprint, pformat
from time import time, localtime, mktime
from datetime import timedelta
from optparse import OptionParser, OptionGroup
from execo import logger
from execo.log import set_style
from execo.time_utils import timedelta_to_seconds, format_seconds, format_date, get_seconds
from execo_g5k.oar import oar_date_to_unixts, format_oar_date, oar_duration_to_seconds
from execo_g5k.planning import Planning


logger = logging.getLogger('execo.FUNK')
usage = "usage: %prog"
description = '''This tool determine when the resources you need are available on '''+\
'''Grid5000 platform thanks to the analysis of Gantt diagram obtained from API and '''+\
'''can (optionally) make the oargrid reservation.
                                                                                
                                                                    
                                                                        
Two modes:                                                                                                                          
- find the slots for a combination of resources (free_slots)                               
- find the maximum number of nodes (max_nodes)                         
                             for the period specified.
                             
                             
Require execo 2.2, http://execo.gforge.inria.fr/doc/
'''
epilog = """Examples :                    
                                                              
    funk.py -m free_slots -r lille:10,lyon:10,sophia:10 -w 2:00:00
    
    funk.py -m max_nodes -r lyon:0,sophia:0,grenoble:0 -w 10:00:00 
"""

parser = OptionParser(usage = usage, description = description, epilog = epilog)

optinout= OptionGroup(parser, "General options", "Define mode and controls I/O.")
optinout.add_option("-m", "--mode",
                dest = "mode", 
                default = 'free',
                help = "Setup the mode: free or max (%default)")
optinout.add_option("-y", "--yes",
                action = "store_true", 
                dest = "yes", 
                default = False,
                help = "Run without prompting user for slot selection (%default)")
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
optinout.add_option("-p", 
                "--plots",
                action="store_true", 
                dest="plots", 
                default=False,
                help="Draw Gantt chart/max nodes over time")
                
parser.add_option_group(optinout)

opttime= OptionGroup(parser, "Time options", "Define options related to time")
opttime.add_option("-w", "--walltime", 
                dest = "walltime", 
                default = '2:00:00',    
                help = "reservation walltime (%default)")
opttime.add_option("-s", "--startdate", 
                dest = "startdate", 
                default = format_oar_date(int(time()+timedelta_to_seconds(timedelta(minutes = 1)))),    
                help = "Starting date in OAR date format (%default)")
opttime.add_option("-e", "--enddate", 
                dest = "enddate", 
                default = format_oar_date(int(time()+timedelta_to_seconds(timedelta(days = 2, minutes = 1)))),    
                help = "End date in OAR date format (%default)")

parser.add_option_group(opttime)


optreservation = OptionGroup(parser, "Resource options", "Customize your grid5000 deployment and choose environment.")
optreservation.add_option("-r", "--resources", 
                dest="resources", 
                default = None,
                help = "comma separated list of 'element1:n_nodes1,element2:n_nodes2', element can be a cluster, site or grid5000.fr")
optreservation.add_option("-l", "--vlan", 
                dest = "vlan", 
                default = None,    
                help="Ask for a vlan (%default)")
optreservation.add_option("-k", "--kavlan", 
                dest = "kavlan", 
                default = False,    
                help="Ask for a Global KaVLAN (%default)")
optreservation.add_option("-o", "--oargridsub_options", 
                dest = "oargridsub_opts", 
                default = "-t deploy",    
                help = "Extra options to pass to the oargridsub command line (%default)")

parser.add_option_group(optreservation)
(options, args) = parser.parse_args()
pprint(options)
if options.verbose:
    logger.setLevel(logging.DEBUG)
elif options.quiet:
    logger.setLevel(logging.WARN)
else:
    logger.setLevel(logging.INFO)


logger.info('%s', set_style('-- Find yoUr Nodes on g5K --', 'emph'))
logger.info('From %s to %s', set_style(options.startdate, 'emph'), 
            set_style(options.enddate, 'emph'))
if options.resources is None:
    options.resources = 'suno:2,sol:2,griffon:10,rennes:20'
    logger.warning('No resources given, will use demo values ')

logger.info('Resources: %s', set_style(options.resources, 'emph'))
logger.info('Walltime: %s', set_style(options.walltime, 'emph'))
logger.info('Mode: %s', set_style(options.mode, 'emph'))

elements = options.resources.split(',')
resources = {}
for element in elements:
    element_uid, n_nodes = element.split(':')
    resources[element_uid]=int(n_nodes)
    
planning = Planning(resources, 
                    oar_date_to_unixts(options.startdate), 
                    oar_date_to_unixts(options.enddate))
logger.info('Gathering resources planning from API')    
planning.compute_slots()
planning.find_slots(options.mode, options.walltime, resources)

slots_ok = [ [ slot[0], slot[1]] for slot in planning.slots_ok ]
for i in range(len(slots_ok)):
    j = i+1
    if j == len(slots_ok)-1:
        break
    while True:
        if slots_ok[i][1] == slots_ok[j][0]:
            slots_ok[i] = [slots_ok[i][0], slots_ok[j][1] ]
            slots_ok.pop(j)
            if j == len(slots_ok)-1:
                break    
        else:
            break
    if j == len(slots_ok)-1:
        break

for slot in slots_ok:
    if slot[1]-slot[0] < oar_duration_to_seconds(options.walltime):
        slots_ok.remove(slot)
        
    


    
    
