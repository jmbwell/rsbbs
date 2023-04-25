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

from rsbbs import __version__
from rsbbs.parser import Parser


# UI

class UI():

    def __init__(self, bbs):
        # Get the BBS
        self.bbs = bbs
        self.parser = self._init_parser()

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
                self.bbs.bye,
                {}),

            ('delete',
                ['d', 'k'],
                'Delete a message',
                self.bbs.delete,
                {'number':
                    {'help':
                        'The numeric index of the message to delete'}},),

            ('deletem',
                ['dm', 'km'],
                'Delete all your messages',
                self.bbs.delete_mine,
                {}),

            ('help',
                ['h', '?'],
                'Show help',
                self.bbs.help,
                {}),

            ('heard',
                ['j'],
                'Show heard stations log',
                self.bbs.heard,
                {}),

            ('list',
                ['l'],
                'List all messages',
                self.bbs.list,
                {}),

            ('listm',
                ['lm'],
                'List only messages addressed to you',
                self.bbs.list_mine,
                {}),

            ('read',
                ['r'],
                'Read messages',
                self.bbs.read,
                {'number': {'help': 'Message number to read'}}),

            ('readm',
                ['rm'],
                'Read only messages addressed to you',
                self.bbs.read_mine,
                {}),

            ('send',
                ['s'],
                'Send a new message to a user',
                self.bbs.send,
                {
                    'callsign': {'help': 'Message recipient callsign'},
                    '--subject': {'help': 'Message subject'},
                    '--message': {'help': 'Message'},
                },),

            ('sendp',
                ['sp'],
                'Send a private message to a user',
                self.bbs.send_private,
                {
                    'callsign': {'help': 'Message recipient callsign'},
                    '--subject': {'help': 'Message subject'},
                    '--message': {'help': 'Message'},
                },),]

        # Send all the commands defined above to the parser
        return Parser(commands).parser

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
                        f"{self.bbs.config['callsign']} ")

        greeting.append(f"Welcome to {self.bbs.config['bbs_name']}, "
                        f"{self.bbs.calling_station}")

        greeting.append(self.bbs.config['banner_message'])

        greeting.append("For help, enter 'h'")

        self._write_output('\r\n'.join(greeting))
