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

import sqlalchemy

from rsbbs.console import Console
from rsbbs.models import Message
from rsbbs.parser import Parser


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        if api.config.debug:
            print(f"Plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='readm',
            aliases=['rm'],
            help='Read all messages addressed to you')
        subparser.set_defaults(func=self.run)

    def list_mine(self, args) -> sqlalchemy.ChunkedIteratorResult:
        with self.api.controller.session() as session:
            try:
                statement = sqlalchemy.select(Message).where(
                    Message.recipient == self.api.config.calling_station)
                result = session.execute(
                    statement,
                    execution_options={"prebuffer_rows": True})
                return result
            except Exception:
                raise

    def run(self, args) -> None:
        """Read all messages addressed to the calling station's callsign,
        in sequence."""
        result = self.list_mine(args)
        messages = result.all()
        count = len(messages)
        if count > 0:
            self.api.write_output(f"Reading {count} messages:")
            for message in messages:
                self.api.print_message(message)
                self.api.read_enter("Enter to continue...")
        else:
            self.api.write_output(f"No messages to read.")
