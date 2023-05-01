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
from rsbbs.models import Message, User


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        logging.info(f"plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='readnew',
            aliases=['rn'],
            help='Read all unread messages addressed to you')
        subparser.set_defaults(func=self.run)

    def list_mine(self, args) -> sqlalchemy.ChunkedIteratorResult:
        with self.api.controller.session() as session:
            try:
                callsign = self.api.config.calling_station
                statement = sqlalchemy.select(Message).where(
                    Message.recipient == callsign).where(
                    ~Message.read_by.any(User.id == self.api.user.id)
                    )
                result = session.execute(
                    statement,
                    execution_options={"prebuffer_rows": True})
                logging.info(f"read message")
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
                with self.api.controller.session() as session:
                    user = session.get(User, self.api.user.id)
                    user.messages.append(message[0])
                    session.commit()
                    logging.info(f"User {self.api.user.id} "
                                 f"read message {message[0].id }")
                self.api.read_enter("Enter to continue...")
        else:
            self.api.write_output(f"No messages to read.")