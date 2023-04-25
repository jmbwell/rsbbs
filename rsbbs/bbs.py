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

import logging.config
import os
import subprocess
import sys
import yaml
import pkg_resources
import platformdirs

from sqlalchemy import create_engine, delete, select, or_
from sqlalchemy.orm import Session

from rsbbs import __version__
from rsbbs.message import Message, Base
from rsbbs.parser import Parser


# Main BBS class

class BBS():

    def __init__(self, sysv_args):

        self._sysv_args = sysv_args

        self.config = self._load_config(sysv_args.config_file)

        self.calling_station = sysv_args.calling_station.upper()

        self.engine = self._init_engine()
        self.parser = self._init_parser()

        logging.config.dictConfig(self.config['logging'])

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    #
    # Config file
    #

    def _load_config(self, config_file):
        """Load configuration file.

        If a config file is specified, attempt to use that. Otherwise, use a
        file in the location appropriate to the host system. Create the file
        if it does not exist, using the config_default.yaml as a default.
        """
        # Use either the specified file or a file in a system config location
        config_path = config_file or os.path.join(
            platformdirs.user_config_dir(appname='rsbbs', ensure_exists=True),
            'config.yaml'
        )
        if self._sysv_args.debug:
            print(config_path)
        # If the file doesn't exist there, create it
        if not os.path.exists(config_path):
            config_template_path = pkg_resources.resource_filename(
                __name__, 'config_default.yaml')
            try:
                with open(config_template_path, 'r') as f:
                    config_template = yaml.load(f, Loader=yaml.FullLoader)
                with open(config_path, 'w') as f:
                    yaml.dump(config_template, f)
            except Exception as e:
                print(f"Error creating configuration file: {e}")
                exit(1)
        # Load it
        try:
            with open(config_path, 'r') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            exit(1)

        logging.info(f"Configuration file was successfully loaded."
                     f"File name: {config_path}")

        return config

    #
    # BBS command parser
    #

    def _init_parser(self):
        """Define BBS command names, aliases, help messages, action (function),
        and any arguments.

        This configures argparser's internal help and maps user commands to BBS
        functions.
        """
        commands = [
            # (name,
            #   aliases,
            #   helpmsg,
            #   function,
            #   {arg:
            #       {arg attributes},
            #   ...})
            ('bye',
                ['b', 'q'],
                'Sign off and disconnect',
                self.bye,
                {}),

            ('delete',
                ['d', 'k'],
                'Delete a message',
                self.delete,
                {'number':
                    {'help':
                        'The numeric index of the message to delete'}},),

            ('deletem',
                ['dm', 'km'],
                'Delete all your messages',
                self.delete_mine,
                {}),

            ('help',
                ['h', '?'],
                'Show help',
                self.help,
                {}),

            ('heard',
                ['j'],
                'Show heard stations log',
                self.heard,
                {}),

            ('list',
                ['l'],
                'List all messages',
                self.list,
                {}),

            ('listm',
                ['lm'],
                'List only messages addressed to you',
                self.list_mine,
                {}),

            ('read',
                ['r'],
                'Read messages',
                self.read,
                {'number': {'help': 'Message number to read'}}),

            ('readm',
                ['rm'],
                'Read only messages addressed to you',
                self.read_mine,
                {}),

            ('send',
                ['s'],
                'Send a new message to a user',
                self.send,
                {
                    'callsign': {'help': 'Message recipient callsign'},
                    '--subject': {'help': 'Message subject'},
                    '--message': {'help': 'Message'},
                },),

            ('sendp',
                ['sp'],
                'Send a private message to a user',
                self.send_private,
                {
                    'callsign': {'help': 'Message recipient callsign'},
                    '--subject': {'help': 'Message subject'},
                    '--message': {'help': 'Message'},
                },),]

        # Send all the commands defined above to the parser
        return Parser(commands).parser

    #
    # Database
    #

    def _init_engine(self):
        """Create a connection to the sqlite3 database.

        The default location is the system-specific user-level data directory.
        """
        db_path = os.path.join(
            platformdirs.user_data_dir(appname='rsbbs', ensure_exists=True),
            'messages.db')
        engine = create_engine(
            'sqlite:///' + db_path,
            echo=self._sysv_args.debug)  # Echo SQL output if -d is turned on
        # Create the database schema if none exists
        Base.metadata.create_all(engine)
        return engine

    #
    # Input and output
    #

    def _read_line(self, prompt):
        """Read a single line of input, with an optional prompt,
        until we get something.
        """
        output = None
        while not output:
            if prompt:
                self._write_output(prompt)
            input = sys.stdin.readline().strip()
            if input != "":
                output = input
        return output

    def _read_multiline(self, prompt):
        """Read multiple lines of input, with an optional prompt,
        until the user enters '/ex' by itself on a line.
        """
        output = []
        if prompt:
            self._write_output(prompt)
        while True:
            line = sys.stdin.readline()
            if line.lower().strip() == "/ex":
                break
            else:
                output.append(line)
        return ''.join(output)

    def _write_output(self, output):
        """Write something to stdout."""
        sys.stdout.write(output + '\r\n')

    def print_message_list(self, messages):
        """Print a list of messages."""
        # Print the column headers
        self._write_output(f"{'MSG#': <{5}} "
                           f"{'TO': <{9}} "
                           f"{'FROM': <{9}} "
                           f"{'DATE': <{11}} "
                           f"SUBJECT")
        # Print the messages
        for message in messages:
            datetime_ = message.Message.datetime.strftime('%Y-%m-%d')
            self._write_output(f"{message.Message.id: <{5}} "
                               f"{message.Message.recipient: <{9}} "
                               f"{message.Message.sender: <{9}} "
                               f"{datetime_: <{11}} "
                               f"{message.Message.subject}")

    def print_message(self, message):
        """Print an individual message."""
        # Format the big ol' date and time string
        datetime = message.Message.datetime.strftime(
            '%A, %B %-d, %Y at %-H:%M %p UTC')
        # Print the message
        self._write_output(f"")
        self._write_output(f"Message: {message.Message.id}")
        self._write_output(f"Date:    {datetime}")
        self._write_output(f"From:    {message.Message.sender}")
        self._write_output(f"To:      {message.Message.recipient}")
        self._write_output(f"Subject: {message.Message.subject}")
        self._write_output(f"")
        self._write_output(f"{message.Message.message}")

    def print_greeting(self):
        # Show greeting
        greeting = []
        greeting.append(f"[RSBBS-{__version__}] listening on "
                        f"{self.config['callsign']} ")

        greeting.append(f"Welcome to {self.config['bbs_name']}, "
                        f"{self.calling_station}")

        greeting.append(self.config['banner_message'])

        greeting.append("For help, enter 'h'")

        self._write_output('\r\n'.join(greeting))

    #
    # BBS command functions
    #

    def bye(self, args):
        """Close the connection and exit."""
        self._write_output("Bye!")
        exit(0)

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
                self._write_output(f"Deleted message #{args.number}")
            except Exception as e:
                self._write_output(f"Unable to delete message #{args.number}")

    def delete_mine(self, args):
        """Delete all messages addressed to the calling station's callsign."""
        self._write_output("Delete all messages addressed to you? Y/N:")
        response = sys.stdin.readline().strip()
        if response.lower() != "y":
            return
        else:
            with Session(self.engine) as session:
                try:
                    statement = delete(Message).where(
                        Message.recipient == self.calling_station
                        ).returning(Message)
                    results = session.execute(statement)
                    count = len(results.all())
                    if count > 0:
                        self._write_output(f"Deleted {count} messages")
                        session.commit()
                    else:
                        self._write_output(f"No messages to delete.")
                except Exception as e:
                    self._write_output(f"Unable to delete messages: {e}")

    def heard(self, args):
        """Show a log of stations that have been heard by this station,
        also known as the 'mheard' (linux) or 'jheard' (KPC, etc.) log.
        """
        self._write_output(f"Heard stations:")
        result = subprocess.run(['mheard'], capture_output=True, text=True)
        self._write_output(result.stdout)

    def help(self, args):
        """Show help."""
        self.parser.print_help()

    def list(self, args):
        """List all messages."""
        with Session(self.engine) as session:
            statement = select(Message).where(or_(
                (Message.is_private.is_not(False)),
                (Message.recipient.__eq__(self.calling_station)))
                )
            results = session.execute(statement)
            self.print_message_list(results)

    def list_mine(self, args):
        """List only messages addressed to the calling station's callsign,
        including public and private messages.
        """
        with Session(self.engine) as session:
            statement = select(Message).where(
                Message.recipient == self.calling_station)
            results = session.execute(statement)
            self.print_message_list(results)

    def read(self, args):
        """Read a message.

        Arguments:
        number -- the message number to read
        """
        with Session(self.engine) as session:
            statement = select(Message).where(Message.id == args.number)
            result = session.execute(statement).one()
            self.print_message(result)

    def read_mine(self, args):
        """Read all messages addressed to the calling station's callsign,
        in sequence."""
        with Session(self.engine) as session:
            statement = select(Message).where(
                Message.recipient == self.calling_station)
            result = session.execute(statement)
            messages = result.all()
            count = len(messages)
            if count > 0:
                self._write_output(f"Reading {count} messages:")
                for message in messages:
                    self.print_message(message)
                    self._write_output("Enter to continue...")
                    sys.stdin.readline()
            else:
                self._write_output(f"No messages to read.")

    def send(self, args, is_private=False):
        """Create a new message addressed to another callsign.

        Required arguments:
        callsign -- the recipient's callsign

        Optional arguments:
        subject -- message subject
        message -- the message itself
        """
        if not args.callsign:
            args.callsign = self._read_line("Callsign:")
        if not args.subject:
            args.subject = self._read_line("Subject:")
        if not args.message:
            args.message = self._read_multiline(
                "Message - end with /ex on a single line:")
        with Session(self.engine) as session:
            session.add(Message(
                sender=self.calling_station.upper(),
                recipient=args.callsign.upper(),
                subject=args.subject,
                message=args.message,
                is_private=is_private
            ))
            try:
                session.commit()
                self._write_output("Message saved!")
            except Exception as e:
                session.rollback()
                self._write_output("Error saving message."
                                   "Contact the sysop for assistance.")

    def send_private(self, args):
        self.send(args, is_private=True)
        """Send a message visible only to the recipient callsign.

        Required arguments:
        callsign -- the recipient's callsign

        Optional arguments:
        subject -- message subject
        message -- the message itself
        """

    #
    # Main loop
    #

    def run(self):

        # Show greeting
        self.print_greeting()

        # Show initial prompt to the calling user
        self._write_output(self.config['command_prompt'])

        # Parse the BBS interactive commands for the rest of time
        for line in sys.stdin:
            try:
                args = self.parser.parse_args(line.split())
                args.func(args)
            except Exception as e:
                pass

            # Show our prompt to the calling user again
            self._write_output(self.config['command_prompt'])
