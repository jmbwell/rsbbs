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

from rsbbs import __version__
from rsbbs import Config, Console, Controller, Logger

from rsbbs.args import parse_args

from rsbbs.user import User


def main():

    # Grab the invocation arguments
    args = parse_args()

    # Load configuration
    config = Config(
           app_name='rsbbs',
           args=args)

    # Start logging
    logger = Logger(config)
    logging.info(f"caller connected")

    # Init the controller
    controller = Controller(config)

    # Init the user:
    user = User(config, controller)
    user.record_login()

    # Init the UI console
    console = Console(config, controller, user)

    # Start the app
    console.run()


if __name__ == "__main__":
    main()
