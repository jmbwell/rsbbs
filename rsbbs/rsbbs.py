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
from rsbbs.commands import Commands
from rsbbs.config import Config
from rsbbs.console import Console
from rsbbs.controller import Controller
from rsbbs.parser import Parser


def main():

    # Parse and handle the system invocation arguments
    sysv_parser = argparse.ArgumentParser(
        description=("The BBS for ax.25 and packet radio "
                     "that is really simple."))

    # Configure args:
    args_list = [
        # [ short, long, action, default, dest, help, required ]
        ['-d', '--debug', 'store_true', None, 'debug',
            'Enable debugging output to stdout', False],
        ['-s', '--calling-station', 'store', 'N0CALL', 'calling_station',
            'Callsign of the calling station', True],
        ['-f', '--config-file', 'store', None, 'config_file',
            'Path to config.yaml file', False],
    ]
    for arg in args_list:
        sysv_parser.add_argument(
            arg[0], arg[1], action=arg[2], default=arg[3], dest=arg[4],
            help=arg[5], required=arg[6])

    # Version arg is special:
    sysv_parser.add_argument(
        '-v', '--version',
        action='version',
        version=f"{sysv_parser.prog} version {__version__}")

    # Parse the args from the system
    sysv_args = sysv_parser.parse_args(sys.argv[1:])

    # Load configuration
    config = Config(
           app_name='rsbbs',
           args=sysv_args)

    # Init the contoller
    controller = Controller(config)

    # Init the UI console
    console = Console(config, controller)

    # Start the app
    console.run()


if __name__ == "__main__":
    main()
