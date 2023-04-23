import argparse
import sys

from rsbbs.bbs import BBS

def main():

    # Parse and handle the system invocation arguments
    sysv_parser = argparse.ArgumentParser(
        description="A Really Simple BBS.")

    sysv_parser.add_argument('-d', '--debug', 
                             action='store_true', 
                             default=None,
                             dest="debug",
                             help="Enable debugging output to stdout", 
                             required=False)
    
    sysv_parser.add_argument('-s', '--calling-station', 
                             action='store', 
                             default='N0CALL',
                             dest="calling_station",
                             help="The callsign of the calling station", 
                             required=True)
    
    sysv_parser.add_argument('-f', '--config-file', 
                             action='store', 
                             default='config.yaml',
                             dest="config_file",
                             help="specify path to config.yaml file", 
                             required=False)
    
    sysv_parser.add_argument('-v', '--version', 
                             action='version', 
                             version=f"{sysv_parser.prog} version zero point aitch point negative purple")
    
    sysv_args = sysv_parser.parse_args(sys.argv[1:])

    # Instantiate the BBS object
    bbs = BBS(sysv_args)

    # Start the main BBS loop
    bbs.main()

if __name__ == "__main__":
    main()
