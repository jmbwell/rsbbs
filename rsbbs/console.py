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
import sys

import rsbbs
from rsbbs.config import Config
from rsbbs.controller import Controller
from rsbbs.parser import Parser
from rsbbs.pluginloader import PluginLoader


# Main UI console class

class Console():

    def __init__(self, config: Config, controller: Controller):
        self.config = config
        self.controller = controller

        self.parser = Parser()

        self.pluginloader = PluginLoader(self)
        self.pluginloader.load_plugins()

    #
    # Input and output
    #

    def disconnect(self) -> None:
        logging.info("caller disconnected")
        exit(0)

    def read_enter(self, prompt) -> None:
        """Wait for the user to press enter.
        """
        if prompt:
            self.write_output(prompt)
        sys.stdin.readline().strip()

    def read_line(self, prompt) -> str:
        """Read a single line of input, with an optional prompt,
        until we get something.
        """
        output = None
        while not output:
            if prompt:
                self.write_output(prompt)
            input = sys.stdin.readline().strip()
            if input != "":
                output = input
        return output

    def read_multiline(self, prompt) -> str:
        """Read multiple lines of input, with an optional prompt,
        until the user enters '/ex' by itself on a line.
        """
        output = []
        if prompt:
            self.write_output(prompt)
        while True:
            line = sys.stdin.readline()
            if line.lower().strip() == "/ex":
                break
            else:
                output.append(line)
        return ''.join(output)

    def write_output(self, output) -> None:
        """Write something to stdout."""
        sys.stdout.write(output + '\r\n')

    def print_configuration(self) -> None:
        self.write_output(repr(self.config))

    def print_greeting(self) -> None:
        # Show greeting
        greeting = []
        greeting.append(f"[RSBBS-{rsbbs.__version__}] listening on "
                        f"{self.config.callsign} ")

        greeting.append(f"Welcome to {self.config.bbs_name}, "
                        f"{self.config.calling_station}")

        greeting.append(self.config.banner_message)

        greeting.append("For help, enter 'h'")

        self.write_output('\r\n'.join(greeting))

    def print_message(self, message):
        """Print an individual message."""
        # Format the big ol' date and time string
        datetime = message.Message.datetime.strftime(
            '%A, %B %-d, %Y at %-H:%M %p UTC')
        # Print the message
        self.write_output(f"")
        self.write_output(f"Message: {message.Message.id}")
        self.write_output(f"Date:    {datetime}")
        self.write_output(f"From:    {message.Message.sender}")
        self.write_output(f"To:      {message.Message.recipient}")
        self.write_output(f"Subject: {message.Message.subject}")
        self.write_output(f"")
        self.write_output(f"{message.Message.message}")

    def print_message_list(self, messages) -> None:
        """Print a list of messages."""
        # Print the column headers
        self.write_output(f"{'MSG#': <{5}} "
                          f"{'TO': <{9}} "
                          f"{'FROM': <{9}} "
                          f"{'DATE': <{11}} "
                          f"SUBJECT")
        # Print the messages
        for message in messages:
            datetime_ = message.Message.datetime.strftime('%Y-%m-%d')
            self.write_output(f"{message.Message.id: <{5}} "
                              f"{message.Message.recipient: <{9}} "
                              f"{message.Message.sender: <{9}} "
                              f"{datetime_: <{11}} "
                              f"{message.Message.subject}")

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
        self.write_output(self.config.command_prompt)

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
            self.write_output(self.config.command_prompt)
