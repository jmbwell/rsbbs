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

import argparse


class BBSArgumentParser(argparse.ArgumentParser):
    # Override the error handler to prevent spewing error cruft over the air
    # def error(self, message):
    #     print(message)

    # Override the exit handler to prevent disconnecting unexpectedly
    def exit(self, arg1, arg2):
        pass


class SortedHelpFormatter(argparse.HelpFormatter):
    def _iter_indented_subactions(self, action):

        if not hasattr(action, '_get_subactions'):
            return

        self._indent()

        subactions = action._get_subactions

        if isinstance(action, argparse._SubParsersAction):
            sorted_subactions = sorted(
                subactions(),
                key=lambda x: x.dest)
        else:
            sorted_subactions = subactions

        for subaction in sorted_subactions:
            yield subaction

        self._dedent()


class Parser(BBSArgumentParser):

    def __init__(self):
        self._init_parser()

    # The only thing anyone should ever access from Parser is its parser
    # attribute, so let's save everyone a step.
    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return getattr(self.parser, attr)

    def _init_parser(self):
        self.sort_actions = True

        # Root parser for BBS commands
        self.parser = BBSArgumentParser(
            description='BBS Main Menu',
            prog='',
            add_help=False,
            usage=argparse.SUPPRESS,
            formatter_class=SortedHelpFormatter,
        )

        # We will create a subparser for each individual command
        self.subparsers = self.parser.add_subparsers(
            title='Commands',
            dest='command')

        # Plugins will then add a subparser for each command, so we're done
        # here
