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
import sqlalchemy.exc

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
            name='delete',
            aliases=['d', 'k'],
            help='Delete a message')
        subparser.add_argument('number',
                               help='The number of the message to delete')
        subparser.set_defaults(func=self.run)

    def delete(self, number) -> None:
        with self.api.controller.session() as session:
            try:
                message = session.get(Message, number)
                session.delete(message)
                session.commit()
                self.api.write_output(f"Deleted message #{number}")
            except sqlalchemy.exc.NoResultFound:
                self.api.write_output(f"Message not found.")
            except Exception as e:
                print(e)

    def run(self, args) -> None:
        """Delete a message.

        Arguments:
        number -- the message number to delete
        """
        if args.number:
            self.delete(args.number)
