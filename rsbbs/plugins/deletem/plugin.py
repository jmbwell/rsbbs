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

from rsbbs.console import Console
from rsbbs.parser import Parser


class Plugin():

    def __init__(self, api: Console):
        self.api = api
        self.init_parser(api.parser)
        if api.config.debug:
            print(f"Plugin {__name__} loaded")

    def init_parser(self, parser: Parser):
        subparser = parser.subparsers.add_parser(
            name='deletem',
            aliases=['dm', 'km'],
            help='Delete all messages addressed to you')
        subparser.set_defaults(func=self.run)

    def run(self, args):
        """Delete all messages addressed to the calling station's callsign."""
        response = self.api.read_line(
            "Delete all messages addressed to you? Y/N:")
        if response.lower() != "y":
            return
        else:
            try:
                result = self.api.controller.delete_mine(args)
                messages = result.all()
                count = len(messages)
                if count > 0:
                    self.api.write_output(f"Deleted {count} messages")
                else:
                    self.api.write_output(f"No messages to delete.")
            except Exception as e:
                self.api.write_output(f"Unable to delete messages: {e}")
