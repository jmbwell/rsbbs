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

import importlib
import os


class PluginLoader():

    def __init__(self, api) -> None:
        self.api = api
        self.plugins = []

    def load_plugins(self) -> None:
        # Path to command plugin directory
        plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')

        # Discover all subdirectories in the plugins directory
        plugin_dirs = [d
                       for d in os.listdir(plugins_dir)
                       if os.path.isdir(os.path.join(plugins_dir, d)) 
                       and not d.startswith('__')]

        if self.api.config.debug:
            print(f"Plugin dirs: {plugin_dirs}")

        # Loop over each plugin directory
        for plugin_dir in plugin_dirs:
            try:
                # Import the module containing the plugin class
                if self.api.config.debug:
                    print(f"Import rsbbs.plugins.{plugin_dir}.plugin")

                plugin_module = importlib.import_module(
                    f"rsbbs.plugins.{plugin_dir}.plugin")

                # Get a reference to the plugin class
                plugin_class = plugin_module.Plugin

                # Initialize an instance of the plugin class, passing api as an
                # argument
                plugin = plugin_class(self.api)

                # Add the loaded plugin to the list of plugins
                self.plugins.append(plugin)
            except Exception as e:
                if self.api.config.debug:
                    print(f"{e}")
                    raise
                else:
                    continue
