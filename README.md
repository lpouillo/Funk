Funk
====
A Python tool to help you to find ressources on the Grid5000 platform.

Version 1.0 is installed on Grid'5000 frontends. See https://www.grid5000.fr/mediawiki/index.php/Funk
    
    usage: funk [-h] [-m MODE] [-y] [-q | -v] [-p PROG] [-r RESOURCES]
                [-b BLACKLIST] [-R RATIO] [-o OARGRIDSUB_OPTS] [-k] [-j JOB_NAME]
                [-w WALLTIME] [-s STARTDATE] [-e ENDDATE] [-c]
    
    This tool helps you to find resources on Grid'5000 platform. It has three modes: 
     - date = give you the number of nodes available at a given date, 
     - free = find the next free slot for a combination of resources, 
     - max  = find the maximum number of nodes for the period specified.
    
    If no arguments is given, compile the planning of the whole platform and generate an 
    oargridsub command line with all available resources for 1 hour. 
    Based on execo 2.2, http://execo.gforge.inria.fr/doc/, oar 2.5, http://oar.imag.fr 
    and the Grid'5000 Job API, https://api.grid5000.fr.
    
    General options:
      Define mode and controls I/O.
    
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -m MODE, --mode MODE  Setup the mode: date, free or max 
                            default = date
      -y, --yes             Perform the reservation automatically
      -q, --quiet           Run without printing anything
      -v, --verbose         Run in verbose mode
      -p PROG, --prog PROG  The program to be run when the reservation start
    
    Reservation:
      Customize your Grid'5000 reservation.
    
      -r RESOURCES, --resources RESOURCES
                            Comma separated list of Grid'5000 elements (grid5000, site or cluster)
                            -r element1,element2 for date and max modes
                            -r element1:n_nodes1,element2:n_nodes2 for free mode
                            default = grid5000
      -b BLACKLIST, --blacklist BLACKLIST
                            Remove clusters from planning computation
      -R RATIO, --ratio RATIO
                            Apply a given ratio to the resources found, works only for mode date and max
      -o OARGRIDSUB_OPTS, --oargridsub_opts OARGRIDSUB_OPTS
                            Extra options to pass to the oargridsub command line
      -k, --kavlan          Ask for a KaVLAN
      -j JOB_NAME, --job_name JOB_NAME
                            The job name passed to the OAR subjobs
                            default = FUNK
    
    Time:
      Define options related to date and time.
    
      -w WALLTIME, --walltime WALLTIME
                            Reservation walltime in OAR format
                            default = 1:00:00
      -s STARTDATE, --startdate STARTDATE
                            Starting date in OAR format
                            default = 2013-11-28 13:41:30
      -e ENDDATE, --enddate ENDDATE
                            End date in OAR format
                            default = 2013-12-19 13:41:30
      -c, --charter         Avoid charter periods
    
    Examples:
    Number of available nodes on stremi cluster from date to date + walltime 
      funk -m date -s "2013-11-28 13:41:30" -r stremi
    First free slots for a resource combination with deploy job type and a KaVLAN
      funk -m free -w 2:00:00 -r grid5000:100,taurus:4 -o "-t deploy" -k
    Maximum number of nodes available for the resources, avoiding charter periods
      funk -m max -w 10:00:00 -r nancy,paradent,edel -c 
    Issues/features requests can be reported to https://github.com/lpouillo/Funk
