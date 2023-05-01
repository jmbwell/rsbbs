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

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, Integer,\
    Table, ForeignKey, Column

from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column, relationship, backref


class Base(DeclarativeBase):
    pass


# Define the association table that links users and messages
user_message_table = Table('user_message', Base.metadata,
                           Column('user_id',
                                  Integer, ForeignKey('user.id')),
                           Column('message_id',
                                  Integer, ForeignKey('message.id')))


# Messages

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


# Users

class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    callsign: Mapped[str] = mapped_column(String)
    given_name: Mapped[str] = mapped_column(String, nullable=True)
    family_name: Mapped[str] = mapped_column(String, nullable=True)
    login_count: Mapped[int] = mapped_column(Integer)
    login_last: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc))
    messages = relationship('Message',
                            secondary=user_message_table,
                            backref='read_by')
