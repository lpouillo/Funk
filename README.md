Funk
====

A Python tool that help you to find ressources for multisites experiments on the Grid5000 platform.

    Usage: funk.py [-w WALLTIME] [-m MODE] [-r element1:n_nodes1,element2:n_nodes2]  
    
    This tool determine when the resources you need are available on Grid'5000
    platform thanks to the analysis of Gantt diagram obtained from API and can
    (optionally) make the oargrid reservation.
    Three modes (-m):
    - now  = give you the number of nodes available
    - free = find the slots for a combination of resources
    - max  = find the maximum number of nodes for the period specified.
    Require execo 2.2, http://execo.gforge.inria.fr/doc/
    
    Options:
      -h, --help            show this help message and exit
    
      General options:
        Define mode and controls I/O.
    
        -m MODE, --mode=MODE
                            Setup the mode: now, free or max (now)
        -y, --yes           Perform the reservation automatically (False)
        -q, --quiet         Run without printing anything (False)
        -v, --verbose       Run in verbose mode (False)
        -p, --plots         Draw plots (gantt, free, max) (False)
    
      Resources:
        Customize your Grid'5000 topology.
    
        -r RESOURCES, --resources=RESOURCES
                            comma separated list of
                            'element1:n_nodes1,element2:n_nodes2', element can be
                            a cluster, site or grid5000
        -k, --kavlan        Ask for a KaVLAN global (False)
        -o OARGRIDSUB_OPTS, --oargridsub_options=OARGRIDSUB_OPTS
                            Extra options to pass to the oargridsub command line
                            (-t deploy)
    
      Time:
        Define options related to date and time.
    
        -w WALLTIME, --walltime=WALLTIME
                            reservation walltime (1:00:00)
        -s STARTDATE, --startdate=STARTDATE
                            Starting date in OAR date format (2013-07-12 09:21:29)
        -e ENDDATE, --enddate=ENDDATE
                            End date in OAR date format (2013-07-14 09:21:59)
    
    Examples :
    Finding the number of available nodes from now to now + walltime
    funk.py -w 1:00:00 -m now -r grid5000
    Finding the first free slots for a resource combination
    funk.py -w 2:00:00 -m free -r lille:10,lyon:10,sophia:10
    Finding the maximum number of nodes available for the resource and with a
    KaVLAN
    funk.py -w 10:00:00 -m max -r lyon,sophia,edel -k

