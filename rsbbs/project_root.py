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

'''
This is a placeholder to be able to access the location of project root directory.
This is needed to be able to read config.yaml from this package, when it is distributed with setuptools and installed.
'''

import os

def path():
    return os.path.dirname(__file__)
