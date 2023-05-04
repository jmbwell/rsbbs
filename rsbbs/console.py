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
from rsbbs.models import User


# Main UI console class

class Console():
    """Class for user input and output."""

    def __init__(self, config: Config, controller: Controller, user: User):
        self.config = config
        self.controller = controller
        self.user = user

        self.parser = Parser()

        self.pluginloader = PluginLoader(self)
        self.pluginloader.load_plugins()

    #
    # Input and output
    #

    def disconnect(self) -> None:
        """End the program, disconnecting the user
        """
        logging.info("caller disconnected")
        sys.exit(0)

    def read_enter(self, prompt: str) -> None:
        """Wait for the user to press enter.

        :param prompt: an optional prompt to show the user

        """
        if prompt:
            self.write_output(prompt)
        sys.stdin.readline().strip()

    def read_line(self, prompt: str) -> str:
        """Read a single line of input, with an optional prompt,
        until we get something.

        :param prompt: an optional prompt to show the user

        """
        valid_input = None
        while not valid_input:
            if prompt:
                self.write_output(prompt)
            input_line = sys.stdin.readline().strip()
            if input_line != "":
                valid_input = input_line
        return valid_input

    def read_multiline(self, prompt: str) -> str:
        """Read multiple lines of input, with an optional prompt,
        until the user enters '/ex' by itself on a line.

        :param prompt: an optional prompt to show the user

        """
        input_lines = []
        if prompt:
            self.write_output(prompt)
        while True:
            input_line = sys.stdin.readline()
            if input_line.lower().strip() != "/ex":
                break
            input_lines.append(input_line)
        return ''.join(input_lines)

    def write_output(self, output: str) -> None:
        """Write something to stdout.

        :param output: the string to write to stdout

        """
        sys.stdout.write(output + '\r\n')

    def print_configuration(self) -> None:
        """Print the current running configuration.

        """
        self.write_output(repr(self.config))

    def print_greeting(self) -> None:
        """Show a greeting to welcome the user upon connection.

        """
        # Show greeting
        greeting = []
        greeting.append(f"[RSBBS-{rsbbs.__version__}] listening on "
                        f"{self.config.callsign} ")

        greeting.append(f"Welcome to {self.config.bbs_name}, "
                        f"{self.user.callsign}")

        greeting.append(f"Last login: {self.user.login_last}")

        greeting.append(self.config.banner_message)

        greeting.append("For help, enter 'h'")

        self.write_output('\r\n'.join(greeting))

    def print_message(self, message: str):
        """Print an individual message.

        :param message: the message to print

        """
        # Format the big ol' date and time string
        datetime = message.Message.datetime.strftime(
            '%A, %B %-d, %Y at %-H:%M %p UTC')
        # Print the message
        self.write_output("")
        self.write_output(f"Message: {message.Message.id}")
        self.write_output(f"Date:    {datetime}")
        self.write_output(f"From:    {message.Message.sender}")
        self.write_output(f"To:      {message.Message.recipient}")
        self.write_output(f"Subject: {message.Message.subject}")
        self.write_output("")
        self.write_output(f"{message.Message.message}")

    def print_message_list(self, messages: list) -> None:
        """Print a list of messages.

        :param messages: a list of Message objects to print

        """
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
        """Main UI loop.

        """
        # If asked to show the config, show the config;
        if self.config.args.show_config:
            self.print_configuration()
            sys.exit(0)

        # Show greeting
        self.print_greeting()

        # Show initial prompt to the calling user
        self.write_output(self.config.command_prompt)

        # Parse the BBS interactive commands for the rest of time
        for input_line in sys.stdin:
            try:
                args = self.parser.parse_args(input_line.split())
                args.func(args)
            except Exception:
                if self.config.debug:
                    raise
                pass

            # Show our prompt to the calling user again
            self.write_output(self.config.command_prompt)
