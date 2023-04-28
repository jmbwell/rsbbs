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
from rsbbs.models import Message
from rsbbs.parser import Parser


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        logging.info(f"plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='sendp',
            aliases=['sp'],
            help='Send a private message to a user')
        subparser.add_argument('--callsign', help='Message recipient callsign')
        subparser.add_argument('--subject', help='Message subject')
        subparser.add_argument('--message', help='Message')
        subparser.set_defaults(func=self.run)

    def send(self, args, is_private=False) -> None:
        with self.api.controller.session() as session:
            try:
                session.add(Message(
                    sender=self.api.config.calling_station.upper(),
                    recipient=args.callsign.upper(),
                    subject=args.subject,
                    message=args.message,
                    is_private=is_private
                ))
                session.commit()
                logging.info(f"sent message to {args.callsign.upper()}")
            except Exception as e:
                logging.error(f"error sending message: {e}")
                session.rollback()
                raise

    def run(self, args) -> None:
        """Create a new message addressed to another callsign.

        Required arguments:
        callsign -- the recipient's callsign

        Optional arguments:
        subject -- message subject
        message -- the message itself
        """
        if not args.callsign:
            args.callsign = self.api.read_line("Callsign:")
        if not args.subject:
            args.subject = self.api.read_line("Subject:")
        if not args.message:
            args.message = self.api.read_multiline(
                "Message - end with /ex on a single line:")
        try:
            self.send(args, is_private=True)
        except Exception as e:
            print(e)
