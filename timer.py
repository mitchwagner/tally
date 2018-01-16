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

    parser.add_argument('activity', help='Activity being timed')
    parser.add_argument('project', help='Project activity belongs to')
    parser.add_argument('--log-file', default="log.txt", help='File to log to')

    return parser


def getArgs():
    args = getParser().parse_args()
    return args


def main():
    start = getNow()
    args = getArgs()

    print("Timing started!")
    print("Activity: %s" % args.activity)
    print("Project: %s" % args.project)

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
            f.write("Duration\t")
            f.write("Activity\t")
            f.write("Project\n")

        f.write(start.strftime("%Y-%m-%d %H:%M:%S") + "\t")
        f.write(stop.strftime("%Y-%m-%d %H:%M:%S") + "\t")

        # Chopping off microseconds. I'm not that efficient..
        f.write(str((stop - start)).split(".")[0] + "\t")
        f.write(args.activity + "\t")
        f.write(args.project + "\n")

    os.remove(".timer.lock")


if __name__ == "__main__":
    main()
