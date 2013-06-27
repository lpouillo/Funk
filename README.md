Funk
====

A Python tool that help you to find ressources for multisites experiments on the Grid5000 platform.

BASIC HELP :
    Usage: funk.py

    This tool determine when the resources you need are available on Grid5000
    platform thanks to the analysis of Gantt diagram obtained from API and can
    (optionally) make the oargrid reservation.
    Two modes:
    - find the slots for a combination of resources (free_slots)
    - find the maximum number of nodes (max_nodes)
    for the period specified.
    Require execo 2.2, http://execo.gforge.inria.fr/doc/
    
    Options:
      -h, --help            show this help message and exit
    
      General options:
        Define mode and controls I/O.
    
        -m MODE, --mode=MODE
                            Setup the mode: free or max (free)
        -y, --yes           Run without prompting user for slot selection (False)
        -q, --quiet         Run without printing anything (False)
        -v, --verbose       Run in verbose mode (False)
        -p, --plots         Draw Gantt chart/max nodes over time
    
      Time options:
        Define options related to time
    
        -w WALLTIME, --walltime=WALLTIME
                            reservation walltime (0:30:00)
        -s STARTDATE, --startdate=STARTDATE
                            Starting date in OAR date format (2013-06-27 17:31:33)
        -e ENDDATE, --enddate=ENDDATE
                            End date in OAR date format (2013-06-29 17:32:03)
    
      Resource options:
        Customize your grid5000 deployment and choose environment.
    
        -r RESOURCES, --resources=RESOURCES
                            comma separated list of
                            'element1:n_nodes1,element2:n_nodes2', element can be
                            a cluster, site or grid5000.fr
        -l VLAN, --vlan=VLAN
                            Ask for a vlan (none)
        -k KAVLAN, --kavlan=KAVLAN
                            Ask for a Global KaVLAN (False)
        -o OARGRIDSUB_OPTS, --oargridsub_options=OARGRIDSUB_OPTS
                            Extra options to pass to the oargridsub command line
                            (-t deploy)
    
    Examples :
    funk.py -m free -r lille:10,lyon:10,sophia:10 -w 2:00:00
    funk.py -m max -r lyon:0,sophia:0,grenoble:0 -w 10:00:00
