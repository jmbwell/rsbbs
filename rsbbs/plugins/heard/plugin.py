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

import subprocess

from rsbbs.console import Console
from rsbbs.parser import Parser


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        if api.config.debug:
            print(f"Plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='heard',
            aliases=['j'],
            help='Show heard stations log')
        subparser.set_defaults(func=self.run)

    def run(self, args) -> None:
        """Show a log of stations that have been heard by this station,
        also known as the 'mheard' (linux) or 'jheard' (KPC, etc.) log.
        """
        self.api.write_output(f"Heard stations:")
        try:
            result = subprocess.run(['mheard'], capture_output=True, text=True)
            self.api.write_output(result.stdout)
        except FileNotFoundError:
            self.api.write_output(f"mheard utility not found.")
        except Exception as e:
            if self.api.config.debug:
                raise
            else:
                self.api.write_output(f"Heard stations not available.")
