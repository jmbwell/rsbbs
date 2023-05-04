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

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from rsbbs.config import Config
from rsbbs.models import Base


class Controller():

    def __init__(self, config: Config) -> None:
        self.config = config
        self._init_datastore()
        self._session

    def _init_datastore(self) -> None:
        """Create a connection to the sqlite3 database.

        The default location is the system-specific user-level data directory.
        """
        db_path = self.config.db_path
        self.engine = create_engine(
            'sqlite:///' + db_path,
            echo=self.config.debug)

        # Create the database schema if none exists
        Base.metadata.create_all(self.engine)

        self._session = Session(self.engine, autoflush=True)

    def session(self) -> Session:
        return self._session
