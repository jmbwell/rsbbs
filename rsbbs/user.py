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

from typing import Any

from datetime import datetime, timezone

from rsbbs import Config, Controller
from rsbbs.models import User as SAUser


class User():
    def __init__(self, config: Config, controller: Controller):
        self.controller = controller
        self.callsign = config.args.calling_station.upper()
        self._user = self.get_or_create_user()

    def __getattr__(self, __name: str) -> Any:
        return getattr(self._user, __name)

    def get_or_create_user(self):
        with self.controller.session() as session:
            session.expire_on_commit = False
            try:
                statement = sqlalchemy.select(SAUser).where(
                    SAUser.callsign == self.callsign)
                exopts = {"prebuffer_rows": True}
                result = session.execute(statement,
                                         execution_options=exopts)
                result = result.one_or_none()
                if result:
                    user = result[0]
                    logging.info(f"User {result[0].callsign} found.")
                    session.commit()
                else:
                    logging.info("User not found.")
                    user = SAUser(
                        callsign=self.callsign,
                        login_count=1,
                    )
                    session.add(user)
                    session.commit()
                    logging.info("User added.")
                return user
            except Exception as e:
                logging.error(e)
                raise

    def record_login(self):
        with self.controller.session() as session:
            try:
                statement = sqlalchemy.select(SAUser).where(
                    SAUser.callsign == self.callsign)
                exopts = {"prebuffer_rows": True}
                result = session.execute(statement,
                                         execution_options=exopts)
                result = result.one_or_none()
                if result:
                    user = result[0]
                    self.login_last = user.login_last
                    user.login_count = user.login_count + 1
                    user.login_last = datetime.now(timezone.utc)
                    session.commit()
                    logging.info("User updated.")
                else:
                    logging.info("User not found.")
            except Exception as e:
                logging.error(e)
                raise
