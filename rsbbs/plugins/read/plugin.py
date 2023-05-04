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
import sqlalchemy.exc

from rsbbs.console import Console
from rsbbs.parser import Parser
from rsbbs.models import Message, User


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        logging.info(f"plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='read',
            aliases=['r'],
            help='Read a message')
        subparser.add_argument('number', help='Message number to read')
        subparser.set_defaults(func=self.run)

    def read_message(self, number) -> None:
        with self.api.controller.session() as session:
            try:
                statement = sqlalchemy.select(Message).where(
                    sqlalchemy.or_(
                        sqlalchemy.and_(
                            Message.id == number,
                            Message.recipient == self.api.user.callsign),
                        sqlalchemy.and_(
                            Message.id == number,
                            sqlalchemy.not_(Message.is_private))))
                result = session.execute(statement).one()
                self.api.print_message(result)
                logging.info("read message")
                session.commit()
                user = session.get(User, self.api.user.id)
                user.messages.append(result[0])
                logging.info(f"User {user.id} read message {result[0].id}")
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                self.api.write_output("Message not found.")
            except Exception as e:
                logging.error(e)

    def run(self, args) -> None:
        """Read a message.

        Arguments:
        number -- the message number to read
        """
        if args.number:
            self.read_message(args.number)
