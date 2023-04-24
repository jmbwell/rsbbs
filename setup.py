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

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rsbbs',
    version='0.1.0',
    description='A BBS for ax25d and packet radio that is really simple',
    long_description=readme,
    author='John Burwell',
    author_email='john@atatdotdot.com',
    url='https://git.b-wells.us/jmbwell/rsbbs',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    data_files=[('config', ['config/config_default.yaml'])],
    entry_points="""
        [console_scripts]
        rsbbs=rsbbs.rsbbs:main
    """
)
