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
import re
import sqlalchemy
import sqlalchemy.orm
import subprocess

from rsbbs import __version__
from rsbbs import Console, Parser
from rsbbs.models import Message, User


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        logging.info(f"Plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='stats',
            aliases=['st'],
            help='Report some statistics about this BBS.')
        subparser.set_defaults(func=self.run)

    def get_message_count(self) -> int:
        with self.api.controller.session() as session:
            try:
                count = session.execute(sqlalchemy.select(
                    sqlalchemy.func.count(Message.id))).scalar_one()
                return int(count)
            except Exception as e:
                logging.error(e)

    def get_user_count(self) -> int:
        with self.api.controller.session() as session:
            try:
                count = session.execute(sqlalchemy.select(
                    sqlalchemy.func.count(User.id))).scalar_one()
                return int(count)
            except Exception as e:
                logging.error(e)

    def get_uptime(self) -> str:
        result = subprocess.run(
            ['uptime'], capture_output=True, text=True)
        uptime = result.stdout
        find = r'.*up\s(.+?),\s*?(\d+?):(\d+?).*'
        replace = r'\1, \2 hour(s), \3 minutes'
        response = re.sub(find, replace, uptime)
        return response

    def run(self, args) -> None:
        """Show some stats."""
        response = []
        response.append(f"[RSBBS-{__version__}] listening on "
                        f"{self.api.config.callsign} ")
        response.append(f"Users: {self.get_user_count()}")
        response.append(f"Messages: {self.get_message_count()}")
        response.append(f"Uptime: {self.get_uptime()}")
        self.api.write_output('\r\n'.join(response))
        logging.info("report stats")
