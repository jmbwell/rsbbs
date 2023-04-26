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
        self._app_name = app_name
        self._config_file_path = args.config_file

        self._load_config()

        self.config['db_path'] = os.path.join(
            platformdirs.user_data_dir(appname=app_name, ensure_exists=True),
            'messages.db')

        self.config['debug'] = args.debug
        self.config['args'] = args

    @property
    def config_path(self):
        # Use either the specified file or a file in a system config location
        config_path = self._config_file_path or os.path.join(
            platformdirs.user_config_dir(
                appname=self._app_name,
                ensure_exists=True),
            'config.yaml'
        )
        return config_path

    def _init_config_file(self):
        # If the file doesn't exist there, create it from the default file
        # included in the package
        if not os.path.exists(self.config_path):
            config_default_file_path = pkg_resources.resource_filename(
                __name__,
                'config_default.yaml')
            try:
                with open(config_default_file_path, 'r') as f:
                    config_template = yaml.load(f, Loader=yaml.FullLoader)
                with open(self.config_path, 'w') as f:
                    yaml.dump(config_template, f)
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
            with open(self.config_path, 'r') as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            exit(1)
