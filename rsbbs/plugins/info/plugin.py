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
import os
import pkg_resources
import platformdirs

from pathlib import Path

from rsbbs.console import Console
from rsbbs.parser import Parser


class Plugin():

    def __init__(self, api: Console) -> None:
        self.api = api
        self.init_parser(api.parser)
        self.init_file()
        logging.info(f"Plugin {__name__} loaded")

    def init_parser(self, parser: Parser) -> None:
        subparser = parser.subparsers.add_parser(
            name='info',
            aliases=['i'],
            help='Show info about this BBS')
        subparser.set_defaults(func=self.run)

    @property
    def file(self) -> Path:
        file_dir = platformdirs.user_config_dir(
            appname=self.api.config.app_name)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        self._file = Path().joinpath(
            file_dir,
            'info.txt'
            )
        return self._file

    def init_file(self) -> None:
        # If the file doesn't exist there, create it from the default file
        # included in the package
        if not self.file.exists():
            default_file = Path(
                pkg_resources.resource_filename(
                    __name__,
                    'info_default.txt'))
            try:
                default_text = default_file.read_text()
                self.file.write_text(default_text)
            except Exception as e:
                logging.error(f"Error creating file {self.file}: {e}")
                exit(1)

    @property
    def file_text(self) -> str:
        """Load data from the file."""
        # Load it
        try:
            self._file_data = self.file.read_text()
            return self._file_data
        except Exception as e:
            logging.error(f"Error reading info file: {e}")
            exit(1)

    def run(self, args) -> None:
        """Read the info file and send it to the caller."""
        self.api.write_output(self.file_text)
        logging.info(f"read info file {self.file}")
