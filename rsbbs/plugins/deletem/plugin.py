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
import sqlalchemy

from rsbbs.console import Console
from rsbbs.parser import Parser
from rsbbs.models import Message


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        logging.info(f"plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='deletem',
            aliases=['dm', 'km'],
            help='Delete all messages addressed to you')
        subparser.set_defaults(func=self.run)

    def delete_mine(self) -> None:
        with self.api.controller.session() as session:
            try:
                statement = sqlalchemy.delete(Message).where(
                    Message.recipient == self.api.config.calling_station
                    ).returning(Message)
                result = session.execute(
                    statement,
                    execution_options={"prebuffer_rows": True})
                session.commit()
                messages = result.all()
                count = len(messages)
                if count > 0:
                    self.api.write_output(f"Deleted {count} messages")
                    logging.info(f"deleted {count} messages")
                else:
                    self.api.write_output("No messages to delete.")
            except Exception as e:
                self.api.write_output(f"Unable to delete messages: {e}")

    def run(self, args) -> None:
        """Delete all messages addressed to the calling station's callsign."""
        response = self.api.read_line(
            "Delete all messages addressed to you? Y/N:")
        if response.lower() == "y":
            self.delete_mine()
