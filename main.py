import argparse
import sys

from rsbbs.bbs import BBS

def main():

    # Parse and handle the system invocation arguments
    sysv_parser = argparse.ArgumentParser(
        description="A Really Simple BBS.")

    # Configure args:
    args_list = [
        #[ short, long, action, default, dest, help, required ]
        ['-d', '--debug', 'store_true', None, 'debug', 'Enable debugging output to stdout', False],
        ['-s', '--calling-station', 'store', 'N0CALL', 'calling_station', 'The callsign of the calling station', True],
        ['-f', '--config-file', 'store', 'config.yaml', 'config_file', 'specify path to config.yaml file', False],
    ]
    for arg in args_list:
        sysv_parser.add_argument(arg[0], arg[1], action=arg[2], default=arg[3], dest=arg[4], help=arg[5], required=arg[6])

    # Version arg is special:
    sysv_parser.add_argument('-v', '--version', 
                             action='version', 
                             version=f"{sysv_parser.prog} version zero point aitch point negative purple")

    # Parse the args from the system
    sysv_args = sysv_parser.parse_args(sys.argv[1:])

    # Instantiate the BBS object
    bbs = BBS(sysv_args)

    # Start the main BBS loop
    bbs.main()

if __name__ == "__main__":
    main()
