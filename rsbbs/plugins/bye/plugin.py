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

import logging

from rsbbs.console import Console
from rsbbs.parser import Parser


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        logging.info(f"Plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='bye',
            aliases=['b', 'q'],
            help='Sign off and disconnect')
        subparser.set_defaults(func=self.run)

    def run(self, args) -> None:
        """Disconnect and exit."""
        self.api.write_output("Bye!")
        logging.info(f"{__name__} exiting")
        self.api.disconnect()
