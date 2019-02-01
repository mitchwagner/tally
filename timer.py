import datetime
import argparse 
import signal
import sys
import os

def signal_handler(signal, frame):
        print('\nCanceling...')
        os.remove(".timer.lock")
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def getNow():
    return datetime.datetime.now()


def getParser():
    parser = argparse.ArgumentParser(description='Time logging utility.')

    subparsers = parser.add_subparsers(dest='subparser_name')

    # Create parser for the "time" command
    time_parser = subparsers.add_parser("time")
    time_parser.add_argument('--activity', help='Activity being timed')
    time_parser.add_argument('--project', help='Project activity belongs to')

    now = getNow()

    # Create parser for the "tally" command
    tally_parser = subparsers.add_parser("tally")
    tally_parser.add_argument("-d1", "--start_day", default=now.day)
    tally_parser.add_argument("-m1", "--start_month", default=now.month)
    tally_parser.add_argument("-y1", "--start_year", default=now.year)

    tally_parser.add_argument("-d2", "--end_day", default=(now.day + 1))
    tally_parser.add_argument("-m2", "--end_month",default=now.month)
    tally_parser.add_argument("-y2", "--end_year",default=now.year)
    tally_parser.add_argument("-a", "--activity",default=None)
    tally_parser.add_argument("-p", "--project",default=None)

    #parser.add_argument('activity', help='Activity being timed')
    #parser.add_argument('project', help='Project activity belongs to')
    #parser.add_argument('--log-file', default="log.txt", help='File to log to')

    parser.add_argument('--log-file', default="log.txt", help='File to log to')

    return parser


def getArgs():
    args = getParser().parse_args()
    return args


def log_time(args):
    print("Timing started!")
    print("Activity: %s" % args.activity)
    print("Project: %s" % args.project)

    start = getNow()

    stop = None

    timing = True

    try:
        lock = open(".timer.lock", "x")
        lock.close()
    except IOError:
        print("Already timing something!")
        sys.exit(1)

    while(timing):
        cmd = input()
        if cmd == "stop" or "\n":
            timing = False
            stop = getNow()

    write_header = False

    # Append to results to log file
    if not (os.path.exists(args.log_file)):
        write_header = True

    with open(args.log_file, 'a+') as f:
        if (write_header):
            f.write("Start\t")
            f.write("Stop\t")
            f.write("Activity\t")
            f.write("Project\n")

        f.write(start.strftime("%Y-%m-%d %H:%M:%S") + "\t")
        f.write(stop.strftime("%Y-%m-%d %H:%M:%S") + "\t")

        # Chopping off microseconds. I'm not that efficient..
        #f.write(str((stop - start)).split(".")[0] + "\t")
        f.write(args.activity + "\t")
        f.write(args.project + "\n")

    os.remove(".timer.lock")


def tokenize(line):
    toks = line.split("\t")
    start = datetime.datetime.strptime(toks[0], "%Y-%m-%d %H:%M:%S")
    stop = datetime.datetime.strptime(toks[1], "%Y-%m-%d %H:%M:%S")
    return [start, stop, toks[2].strip(), toks[3].strip()]


def entry_in_range(start, stop, entry_start, entry_stop):
    '''
    Assumes starts are less than respective stops

    Asks the question: IS SOME COMPONENT of the entry overlapping with
    the specified time period?
    '''

    if entry_start > stop:
        return False

    if entry_stop < start:
        return False

    return True


def get_period_in_range(start, stop, entry_start, entry_stop):
    '''
    Assumes the entry is known to be in range already.
    '''
    if entry_start <= start:
        return entry_stop - start

    if entry_stop >= stop:
        return stop - entry_start

    return entry_stop - entry_start
    

def tally(args):
    
    # {project : dictionary {activity : sum}}
    tallies = {}

    start_time = datetime.datetime(
        int(args.start_year),
        int(args.start_month),
        int(args.start_day))

    stop_time = datetime.datetime(
        int(args.end_year),
        int(args.end_month),
        int(args.end_day))

    with open(args.log_file, 'r') as f:
        # Skip the header
        next(f)

        for line in f:
            toks = tokenize(line)

            if entry_in_range(start_time, stop_time, toks[0], toks[1]):
                activity = toks[2]
                project = toks[3]

                if args.project == None or args.project == project : 

                    if args.activity == None or args.activity == activity: 

                        # Make sure there is space for entry here
                        if project not in tallies:
                            tallies[project] = {}

                        if activity not in tallies[project]:
                            tallies[project][activity] = 0
                        
                        # Calculate the period the entry is in range
                        duration = get_period_in_range(
                            start_time, stop_time, toks[0], toks[1])

                        tallies[project][activity] += duration.total_seconds()

    for project in tallies:
        for activity in tallies[project]:
            sec = datetime.timedelta(seconds=tallies[project][activity])
            d = datetime.datetime(1, 1, 1) + sec

            print(
                "Project: " + project, 
                "\tActivity: " + activity, 
                "\tTime(s): " + "%02d:%02d:%02d:%02d" % (d.day-1, d.hour, d.minute, d.second)) #str(tallies[project][activity]))


def main():
    args = getArgs()

    if args.subparser_name == 'time':
        log_time(args)

    elif args.subparser_name == "tally":
        tally(args)


if __name__ == "__main__":
    main()
