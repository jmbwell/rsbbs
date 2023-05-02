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

import io
import sys
import unittest
import unittest.mock

from argparse import Namespace
from rsbbs.args import parse_args


class TestParseArgs(unittest.TestCase):

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_parse_args_no_args(self, mock_stdout):
        sys.argv = ['']
        with self.assertRaises(SystemExit):
            parse_args()

    def test_parse_args_invalid_arg(self):
        sys.argv = ['', '--invalid-arg']
        with self.assertRaises(SystemExit):
            parse_args()

    def test_parse_args_with_callsign(self):
        sys.argv = ['', '-s', 'TESCALL']
        args = parse_args()
        self.assertTrue(args.calling_station is 'TESCALL')

    def test_parse_args_with_debug(self):
        sys.argv = ['', '-s', 'TESCALL', '-d']
        args = parse_args()
        self.assertTrue(args.calling_station is 'TESCALL')
        self.assertTrue(args.debug)

    def test_parse_args_with_configfile(self):
        sys.argv = ['', '-s', 'TESCALL', '-f', 'configfilepath']
        args = parse_args()
        self.assertTrue(args.calling_station is 'TESCALL')
        self.assertTrue(args.config_file is 'configfilepath')

    def test_parse_args_with_loglevel(self):
        sys.argv = ['', '-s', 'TESCALL', '--log-level', 'DEBUG']
        args = parse_args()
        self.assertTrue(args.calling_station is 'TESCALL')
        self.assertTrue(args.log_level is 'DEBUG')
