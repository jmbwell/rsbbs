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
from rsbbs.models import Message
from rsbbs.parser import Parser


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        logging.info("plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='listm',
            aliases=['lm'],
            help='List only messages addressed to you')
        subparser.set_defaults(func=self.run)

    def list_mine(self, args) -> sqlalchemy.ChunkedIteratorResult:
        with self.api.controller.session() as session:
            try:
                statement = sqlalchemy.select(Message).where(
                    Message.recipient == self.api.config.calling_station)
                result = session.execute(
                    statement,
                    execution_options={"prebuffer_rows": True})
                logging.info("list my messages")
                return result
            except Exception:
                raise

    def run(self, args):
        """List only messages addressed to the calling station's callsign,
        including public and private messages.
        """
        result = self.list_mine(args)
        self.api.print_message_list(result)
