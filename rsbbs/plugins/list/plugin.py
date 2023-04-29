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

from rsbbs import Console, Parser
from rsbbs.models import Message


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        logging.info(f"plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='list',
            aliases=['l'],
            help='List all available messages')
        subparser.set_defaults(func=self.run)

    def list(self, args) -> sqlalchemy.ChunkedIteratorResult:
        """List all messages."""
        with self.api.controller.session() as session:
            try:
                # Using or_ and is_ etc. to distinguish from python operators
                statement = sqlalchemy.select(Message).where(
                    sqlalchemy.or_(
                        (Message.is_private.is_(False)),
                        (Message.recipient.__eq__(
                            self.api.config.calling_station)))
                    )
                result = session.execute(
                    statement,
                    execution_options={"prebuffer_rows": True})
                logging.info("list messages")
            except Exception:
                raise
        return result

    def run(self, args) -> None:
        """List all public messages and messages private to the caller."""
        result = self.list(args)
        self.api.print_message_list(result)
