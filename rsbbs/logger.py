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

import datetime
import logging
import logging.handlers
import os
import platformdirs


class Logger(logging.Logger):
    def __init__(self, config):
        super().__init__(name=config.app_name)
        self.config = config
        self.name = config.app_name
        self.caller = config.calling_station

        if self.config.args.debug:
            self.log_level = logging.DEBUG
        else:
            self.log_level = getattr(logging,
                                     self.config.args.log_level.upper())

        self._init_logger()

    def _init_logger(self):
        logger = logging.getLogger()
        logger.setLevel(self.level)

        # Remove the default StreamHandler that logs to the console
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                logger.removeHandler(handler)

        # Log to a file in the system user log directory
        log_dir = platformdirs.user_log_dir(appname=self.name,
                                            ensure_exists=True)
        log_filepath = os.path.join(log_dir, 'activity.log')

        handler = logging.FileHandler(filename=log_filepath)

        # Add the calling station to the log messages
        handler.setFormatter(Formatter(self.caller))

        # Add the handler!
        logger.addHandler(handler)


class Formatter(logging.Formatter):
    def __init__(self, var):
        super().__init__()
        self.var = var

    def format(self, record):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        record.msg = f"{now} {record.levelname} {self.var} {record.msg}"
        return super().format(record)
