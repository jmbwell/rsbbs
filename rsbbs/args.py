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

from rsbbs import __version__


def parse_args():
    # Parse and handle the system invocation arguments
    argv_parser = argparse.ArgumentParser(
        description=("The BBS for ax.25 and packet radio "
                     "that is really simple."))

    # Configure args:
    args_list = [
        # [ short, long, action, default, dest, help, required ]
        # Debug flag:
        ['-d', '--debug', 'store_true', None, 'debug',
            'Enable debugging output to stdout', False],
        # Config file path:
        ['-f', '--config-file', 'store', None, 'config_file',
            'Path to config.yaml file', False],
    ]
    for arg in args_list:
        argv_parser.add_argument(
            arg[0], arg[1], action=arg[2], default=arg[3], dest=arg[4],
            help=arg[5], required=arg[6])

    group = argv_parser.add_mutually_exclusive_group(required=True)

    # Log level:
    argv_parser.add_argument(
        '--log-level',
        action='store',
        default='INFO',
        dest='log_level',
        help="Logging level")

    # Show config option:
    group.add_argument(
        '--show-config',
        action='store_true',
        default=None,
        dest='show_config',
        help="Show the configuration and exit")

    # Calling station:
    group.add_argument(
        '-s',
        '--calling-station',
        action='store',
        default='N0CALL',
        dest='calling_station',
        help="Callsign of the calling station")

    # Version arg is special:
    argv_parser.add_argument(
        '-v', '--version',
        action='version',
        version=f"{argv_parser.prog} version {__version__}")

    # Parse the args from the system
    return argv_parser.parse_args(sys.argv[1:])
