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
        self.plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        self._prefix = 'rsbbs.plugins'
        self._identifier = 'plugin'

    @property
    def _plugin_dirs(self) -> list:
        # Discover all subdirectories in the plugins directory
        plugin_dirs = [d
                       for d in os.listdir(self.plugins_dir)
                       if os.path.isdir(os.path.join(self.plugins_dir, d))
                       and not d.startswith('__')]
        return plugin_dirs

    def load_plugin(self, plugin_dir) -> None:
        try:
            # Import the module containing the plugin class
            plugin_module = importlib.import_module(
                f"{self._prefix}.{plugin_dir}.{self._identifier}")

            # Get a reference to the plugin class
            plugin_class = plugin_module.Plugin

            # Initialize an instance of the plugin class, passing api as an
            # argument
            plugin = plugin_class(self.api)

            # Add the loaded plugin to the list of plugins
            self.plugins.append(plugin)
        except Exception as e:
            raise

    def load_plugins(self) -> None:
        # Loop over each plugin directory
        for plugin_dir in self._plugin_dirs:
            self.load_plugin(plugin_dir)
