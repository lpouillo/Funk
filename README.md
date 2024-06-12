Funk
====
A Python tool to help you to find ressources on the Grid5000 platform.
Requires execo 2.6.7

Developped by the Inria Hemera initiative 2010-2014

   pip install execo==2.6.7


https://www.grid5000.fr/mediawiki/index.php/Hemera

	usage: funk [-h] [--version] [-m {date,free,max}] [-y] [--quiet | -v] [-p PROGRAM] [--plots] [--json] [--json-file JSON_FILE]
				[-r RESOURCES] [-b BLACKLIST] [-R RATIO] [-o SUBMISSION_OPTS] [-k] [-n SUBNET] [-j JOB_NAME] [-q QUEUE] [--virtual]
				[--infiniband] [--green] [-w WALLTIME] [-s STARTDATE] [-e ENDDATE] [-c]

	This tool helps you to find resources on Grid'5000 platform. It has three modes: 
	- date = give you the number of nodes available at a given date, 
	- free = find the next free slot for a combination of resources, 
	- max  = find the time slot where the maximum number of nodes are available.

	If no arguments is given, compile the planning of the whole platform and generate 
			a oarsub command line with all available resources for 1 hour, on every site.
			Based on execo 2.6.7, https://mimbert.gitlabpages.inria.fr/execo/oar 2.5, http://oar.imag.fr.

	General options:
	Define mode and controls I/O.

	-h, --help            show this help message and exit
	--version             show program's version number and exit
	-m {date,free,max}, --mode {date,free,max}
							Setup the mode: date, free or max 
							default = date
	-y, --yes             Perform the reservation automatically
	--quiet               Run without printing anything
	-v, --verbose         Run in verbose mode
	-p PROGRAM, --program PROGRAM
							The program to be run when the reservation start
	--plots               Draw a Gantt plot and the slots
	--json                Output the computed data to standard output
	--json-file JSON_FILE
							Output the computed data to a json file

	Reservation:
	Customize your Grid'5000 reservation.

	-r RESOURCES, --resources RESOURCES
							Comma separated list of Grid'5000 elements  (grid5000, site or cluster)
							-r element1,element2 for date and max modes
							-r element1:n_nodes1,element2:n_nodes2 for free mode
							default = grid5000
	-b BLACKLIST, --blacklist BLACKLIST
							Remove clusters from planning computation
	-R RATIO, --ratio RATIO
							Apply a given ratio to the host resources
	-o SUBMISSION_OPTS, --submission_opts SUBMISSION_OPTS
							Extra options to pass to the oarsub command line
	-k, --kavlan          Ask for a KaVLAN
	-n SUBNET, --subnet SUBNET
							Ask for subnets. slash_22=1 will retrieve a /22 subnet on every site of your requests, 
							but you can specify site1:slash_22=2,site2:slash_19=1
	-j JOB_NAME, --job_name JOB_NAME
							The job name passed to the OAR subjobs
							default = FUNK
	-q QUEUE, --queue QUEUE
							The OAR queue to use
							default = default
	--virtual             Use only clusters with hardware virtualization
	--infiniband          Use only clusters with infiniband or myrinet interfaces
	--green               Use only clusters that have energetical power measurements

	Time:
	Define options related to date and time.

	-w WALLTIME, --walltime WALLTIME
							Reservation walltime in OAR format
							default = 1:00:00
	-s STARTDATE, --startdate STARTDATE
							Starting date in OAR format
							default = now
	-e ENDDATE, --enddate ENDDATE
							End date in OAR format
							default = three weeks after the startdate
	-c, --charter         Avoid charter periods

	Examples:
	Number of available nodes on stremi cluster from date to date + walltime 
	funk -m date -s "2024-06-12 14:57:43" -r stremi
	First free slots for a resource combination with deploy job type and a KaVLAN
	funk -m free -w 2:00:00 -r grid5000:100,taurus:4 -o "-t deploy" -k
	Maximum number of nodes available for the resources, avoiding charter periods
	funk -m max -w 10:00:00 -r nancy,paradent,edel -c 
	Issues/features requests can be reported to https://github.com/lpouillo/Funk
