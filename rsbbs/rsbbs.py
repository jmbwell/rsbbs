#!/usr/bin/env python
#
# Really Simple BBS - a really simple BBS for ax.25 packet radio.
# Copyright (C) 2023 John Burwell <john@atatdotdot.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import sys

from rsbbs.bbs import BBS


def main():

    # Parse and handle the system invocation arguments
    sysv_parser = argparse.ArgumentParser(
        description="A Really Simple BBS.")

    # Configure args:
    args_list = [
        # [ short, long, action, default, dest, help, required ]
        ['-d', '--debug', 'store_true', None, 'debug',
            'Enable debugging output to stdout', False],
        ['-s', '--calling-station', 'store', 'N0CALL', 'calling_station',
            'The callsign of the calling station', True],
        ['-f', '--config-file', 'store', 'config.yaml', 'config_file',
            'specify path to config.yaml file', False],
    ]
    for arg in args_list:
        sysv_parser.add_argument(
            arg[0], arg[1], action=arg[2], default=arg[3], dest=arg[4], 
            help=arg[5], required=arg[6])

    # Version arg is special:
    sysv_parser.add_argument('-v', '--version', 
                             action='version', 
                             version=f"{sysv_parser.prog} version 0.h.-p")

    # Parse the args from the system
    sysv_args = sysv_parser.parse_args(sys.argv[1:])

    # Instantiate the BBS object
    bbs = BBS(sysv_args)

    # Start the main BBS loop
    bbs.run()


if __name__ == "__main__":
    main()
