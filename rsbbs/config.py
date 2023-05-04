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

import os
import pkg_resources
import platformdirs
import yaml


class Config():

    def __init__(self, app_name, args):
        self.app_name = app_name
        self._argv_config_file = args.config_file

        self._init_config_file()
        self._load_config()

        # Put the messages db file in the system's user data directory
        self._config['db_path'] = os.path.join(
            platformdirs.user_data_dir(
                appname=self.app_name,
                ensure_exists=True),
            'messages.db')

        # Grab some config from the command line for convenience
        self._config['args'] = args
        self._config['calling_station'] = args.calling_station.upper() or None
        self._config['debug'] = args.debug

    # The main thing people want from Config is config values, so let's pretend
    # everything anyone asks of Config that isn't otherwise defined is probably
    # a config value they want
    def __getattr__(self, __name: str):
        return self._config[__name]

    # Handle requests to access this thing as a dict:
    def __dict__(self):
        return self._config

    # Format the config as yaml for display
    def __repr__(self):
        repr = []
        repr.append(f"app_name: {self.app_name}\r\n")
        repr.append(f"config_file: {self.config_file}\r\n")
        repr.append(yaml.dump(self._config))
        return ''.join(repr)

    @property
    def config_file(self):
        # Use either the specified file or a file in a system config location
        config_file = self._argv_config_file or os.path.join(
            platformdirs.user_config_dir(
                appname=self.app_name,
                ensure_exists=True),
            'config.yaml'
        )
        return config_file

    def _init_config_file(self):
        # If the file doesn't exist there, create it from the default file
        # included in the package
        if not os.path.exists(self.config_file):
            config_default_file = pkg_resources.resource_filename(
                __name__,
                'config_default.yaml')
            try:
                with open(config_default_file, 'r') as f:
                    config_default = yaml.load(f, Loader=yaml.FullLoader)
                with open(self.config_file, 'w') as f:
                    yaml.dump(config_default, f)
            except Exception as e:
                print(f"Error creating configuration file: {e}")
                exit(1)

    def _load_config(self):
        """Load configuration file.

        If a config file is specified, attempt to use that. Otherwise, use a
        file in the location appropriate to the host system. Create the file
        if it does not exist, using the config_default.yaml as a default.
        """
        # Load it
        try:
            with open(self.config_file, 'r') as f:
                self._config = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            exit(1)
