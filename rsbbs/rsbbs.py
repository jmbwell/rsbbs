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
import logging
import sys

from rsbbs import __version__
from rsbbs.config import Config
from rsbbs.console import Console
from rsbbs.controller import Controller
from rsbbs.logging import Formatter


def parse_args():
    # Parse and handle the system invocation arguments
    argv_parser = argparse.ArgumentParser(
        description=("The BBS for ax.25 and packet radio "
                     "that is really simple."))

    # Configure args:
    args_list = [
        # [ short, long, action, default, dest, help, required ]
        ['-d', '--debug', 'store_true', None, 'debug',
            'Enable debugging output to stdout', False],
        # ['-s', '--calling-station', 'store', 'N0CALL', 'calling_station',
        #     'Callsign of the calling station', True],
        ['-f', '--config-file', 'store', None, 'config_file',
            'Path to config.yaml file', False],
    ]
    for arg in args_list:
        argv_parser.add_argument(
            arg[0], arg[1], action=arg[2], default=arg[3], dest=arg[4],
            help=arg[5], required=arg[6])

    group = argv_parser.add_mutually_exclusive_group(required=True)

    # Log level:
    group.add_argument(
        '--log-level',
        action='store',
        default='ERROR',
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


def main():

    # Grab the invocation arguments
    args = parse_args()

    # Start logging
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = getattr(logging, args.log_level.upper())

    logging.basicConfig(format='%(asctime)s %(message)s',
                        level=log_level)
    logging.info(f"{__name__} started")

    # Load configuration
    config = Config(
           app_name='rsbbs',
           args=args)

    # Add the calling station to the logs
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(Formatter(config.calling_station))
    logger.addHandler(handler)

    logger.info("connected")

    # Init the controller
    controller = Controller(config)

    # Init the UI console
    console = Console(config, controller)

    # Start the app
    console.run()

    logging.info(f"{__name__} exiting")


if __name__ == "__main__":
    main()
