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

import subprocess

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import create_engine, delete, select, or_

from sqlalchemy.orm import DeclarativeBase, Mapped, Session
from sqlalchemy.orm import mapped_column

from rsbbs.config import Config


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = 'message'
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(String)
    recipient: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    datetime: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc))
    is_private: Mapped[bool] = mapped_column(Boolean)


class Controller():

    def __init__(self, config: Config):
        self.config = config
        self._init_datastore()

    def _init_datastore(self):
        """Create a connection to the sqlite3 database.

        The default location is the system-specific user-level data directory.
        """
        db_path = self.config.db_path
        self.engine = create_engine(
            'sqlite:///' + db_path,
            echo=self.config.debug)

        # Create the database schema if none exists
        Base.metadata.create_all(self.engine)

    def delete(self, args):
        """Delete a message.

        Arguments:
        number -- the message number to delete
        """
        with Session(self.engine) as session:
            try:
                message = session.get(Message, args.number)
                session.delete(message)
                session.commit()
            except Exception:
                raise

    def delete_mine(self, args):
        """Delete all messages addressed to the calling station's callsign."""
        with Session(self.engine) as session:
            try:
                statement = delete(Message).where(
                    Message.recipient == self.config.calling_station
                    ).returning(Message)
                result = session.execute(statement)
                count = len(result.all())
                session.commit()
                return {'count': count, 'result': result}
            except Exception:
                raise

    def heard(self, args):
        """Show a log of stations that have been heard by this station,
        also known as the 'mheard' (linux) or 'jheard' (KPC, etc.) log.
        """
        try:
            return subprocess.run(['mheard'], capture_output=True, text=True)
        except FileNotFoundError:
            raise
        except Exception:
            raise

    def list(self, args):
        """List all messages."""
        with Session(self.engine) as session:
            try:
                # Using or_ and is_ etc. to distinguish from python operators
                statement = select(Message).where(
                    or_(
                        (Message.is_private.is_(False)),
                        (Message.recipient.__eq__(
                            self.config.calling_station)))
                    )
                result = session.execute(
                    statement,
                    execution_options={"prebuffer_rows": True})
            except Exception:
                raise
        return result

    def list_mine(self, args):
        """List only messages addressed to the calling station's callsign,
        including public and private messages.
        """
        with Session(self.engine) as session:
            try:
                statement = select(Message).where(
                    Message.recipient == self.config.calling_station)
                result = session.execute(
                    statement,
                    execution_options={"prebuffer_rows": True})
                return result
            except Exception:
                raise

    def read(self, args):
        """Read a message.

        Arguments:
        number -- the message number to read
        """
        with Session(self.engine) as session:
            try:
                statement = select(Message).where(Message.id == args.number)
                result = session.execute(statement).one()
                return result
            except Exception:
                raise

    def send(self, args, is_private=False):
        """Create a new message addressed to another callsign.

        Required arguments:
        callsign -- the recipient's callsign

        Optional arguments:
        subject -- message subject
        message -- the message itself
        """
        with Session(self.engine) as session:
            try:
                session.add(Message(
                    sender=self.config.calling_station.upper(),
                    recipient=args.callsign.upper(),
                    subject=args.subject,
                    message=args.message,
                    is_private=is_private
                ))
                session.commit()
                return {}
            except Exception:
                session.rollback()
                raise
