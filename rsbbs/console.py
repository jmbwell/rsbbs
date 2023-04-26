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

import sqlalchemy.exc

import rsbbs
from rsbbs.commands import Commands
from rsbbs.config import Config
from rsbbs.controller import Controller
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

    def print_configuration(self):
        self._write_output(repr(self.config))

    def print_greeting(self):
        # Show greeting
        greeting = []
        greeting.append(f"[RSBBS-{rsbbs.__version__}] listening on "
                        f"{self.config.callsign} ")

        greeting.append(f"Welcome to {self.config.bbs_name}, "
                        f"{self.config.calling_station}")

        greeting.append(self.config.banner_message)

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
        """Disconnect and exit."""
        self._write_output("Bye!")
        exit(0)

    def delete(self, args):
        """Delete a message specified by ID number."""
        if args.number:
            try:
                self.controller.delete(args)
                self._write_output(f"Deleted message #{args.number}")
            except Exception as e:
                self._write_output(f"Message not found.")

    def delete_mine(self, args):
        """Delete all messages addressed to the calling station's callsign."""
        self._write_output("Delete all messages addressed to you? Y/N:")
        response = sys.stdin.readline().strip()
        if response.lower() != "y":
            return
        else:
            try:
                result = self.controller.delete_mine(args)
                messages = result.all()
                count = len(messages)
                if count > 0:
                    self._write_output(f"Deleted {count} messages")
                else:
                    self._write_output(f"No messages to delete.")
            except Exception as e:
                self._write_output(f"Unable to delete messages: {e}")

    def heard(self, args):
        """Show a log of stations that have been heard by this station,
        also known as the 'mheard' (linux) or 'jheard' (KPC, etc.) log.
        """
        self._write_output(f"Heard stations:")
        try:
            result = self.controller.heard(args)
            self._write_output(result.stdout)
        except FileNotFoundError:
            self._write_output(f"mheard utility not found.")
        except Exception as e:
            if self.config.debug:
                raise
            else:
                self._write_output(f"Heard stations not available.")

    def help(self, args):
        self.parser.print_help()

    def list(self, args):
        """List all public messages and private messages to the caller."""
        result = self.controller.list(args)
        self.print_message_list(result)

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
        if args.number:
            try:
                result = self.controller.read(args)
                self.print_message(result)
            except sqlalchemy.exc.NoResultFound:
                self._write_output(f"Message not found.")
            except Exception as e:
                print(e)

    def read_mine(self, args):
        """Read all messages addressed to the calling station's callsign,
        in sequence."""
        result = self.controller.list_mine(args)
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
        try:
            self.controller.send(args, is_private=is_private)
        except Exception as e:
            print(e)

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
    # Main input loop
    #

    def run(self):

        # If asked to show the config, show the config;
        if self.config.args.show_config:
            self.print_configuration()
            exit(0)

        # Show greeting
        self.print_greeting()

        # Show initial prompt to the calling user
        self._write_output(self.config.command_prompt)

        # Parse the BBS interactive commands for the rest of time
        for line in sys.stdin:
            try:
                args = self.parser.parse_args(line.split())
                args.func(args)
            except Exception:
                if self.config.debug:
                    raise
                else:
                    pass

            # Show our prompt to the calling user again
            self._write_output(self.config.command_prompt)
