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

import sys

import rsbbs
from rsbbs.commands import Commands
from rsbbs.config import Config
from rsbbs.controller import Base, Controller, Message
from rsbbs.parser import Parser


# Main UI console class

class Console():

    def __init__(self, config: Config, controller: Controller):
        self.config = config
        self.controller = controller

        self.commands = Commands(self)
        self.parser = Parser(self.commands)

    #
    # Input and output
    #

    def _write_output(self, output):
        """Write something to stdout."""
        sys.stdout.write(output + '\r\n')

    def print_greeting(self):
        # Show greeting
        greeting = []
        greeting.append(f"[RSBBS-{rsbbs.__version__}] listening on "
                        f"{self.config.config['callsign']} ")

        greeting.append(f"Welcome to {self.config.config['bbs_name']}, "
                        f"{self.config.config['args'].calling_station}")

        greeting.append(self.config.config['banner_message'])

        greeting.append("For help, enter 'h'")

        self._write_output('\r\n'.join(greeting))

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

    #
    # Command functions
    #

    def bye(self, args):
        self._write_output("Bye!")
        exit(0)

    def delete(self, args):
        self.controller.delete(args)

    def delete_mine(self, args):
        """Delete all messages addressed to the calling station's callsign."""
        self._write_output("Delete all messages addressed to you? Y/N:")
        response = sys.stdin.readline().strip()
        if response.lower() != "y":
            return
        else:
            try:
                result = self.controller.delete_mine(args)
                if result['count'] > 0:
                    self._write_output(f"Deleted {result['count']} messages")
                else:
                    self._write_output(f"No messages to delete.")
            except Exception as e:
                self._write_output(f"Unable to delete messages: {e}")

    def heard(self, args):
        """Show a log of stations that have been heard by this station,
        also known as the 'mheard' (linux) or 'jheard' (KPC, etc.) log.
        """
        self._write_output(f"Heard stations:")
        result = self.controller.heard(args)
        self._write_output(result.stdout)

    def help(self, args):
        self.parser.parser.print_help()

    def list(self, args):
        """List all messages."""
        result = self.controller.list(args)
        self.print_message_list(result['result'])

    def list_mine(self, args):
        """List only messages addressed to the calling station's callsign,
        including public and private messages.
        """
        result = self.controller.list_mine(args)
        self.print_message_list(result)

    def read(self, args):
        """Read a message.

        Arguments:
        number -- the message number to read
        """
        result = self.controller.read(args)
        self.print_message(result)

    def read_mine(self, args):
        """Read all messages addressed to the calling station's callsign,
        in sequence."""
        result = self.controller.list_mine(args)
        if result['count'] > 0:
            self._write_output(f"Reading {result['count']} messages:")
            for message in result['result'].all():
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
        # with Session(self.engine) as session:
        #     session.add(Message(
        #         sender=self.calling_station.upper(),
        #         recipient=args.callsign.upper(),
        #         subject=args.subject,
        #         message=args.message,
        #         is_private=is_private
        #     ))
            # try:
            #     session.commit()
            #     self._write_output("Message saved!")
            # except Exception as e:
            #     session.rollback()
            #     self._write_output("Error saving message."
            #                           "Contact the sysop for assistance.")

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
    # Main run method
    #

    def run(self):

        # Show greeting
        self.print_greeting()

        # Show initial prompt to the calling user
        self._write_output(self.config.config['command_prompt'])

        # Parse the BBS interactive commands for the rest of time
        for line in sys.stdin:
            try:
                args = self.parser.parser.parse_args(line.split())
                args.func(args)
            except Exception:
                if self.config.config['debug']:
                    raise
                else:
                    pass

            # Show our prompt to the calling user again
            self._write_output(self.config.config['command_prompt'])
