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


class Commands():

    def __init__(self, responder):
        self.responder = responder

    @property
    def commands(self):
        commands = [
            # (name,
            #   aliases,
            #   helpmsg,
            #   function,
            #   arg:
            #       arg attributes...,
            # )
            ('bye',
                ['b', 'q'],
                'Sign off and disconnect',
                self.responder.bye,
                {}),

            ('delete',
                ['d', 'k'],
                'Delete a message',
                self.responder.delete,
                {'number':
                    {'help':
                        'The numeric index of the message to delete'}},),

            ('deletem',
                ['dm', 'km'],
                'Delete all your messages',
                self.responder.delete_mine,
                {}),

            ('help',
                ['h', '?'],
                'Show help',
                self.responder.help,
                {}),

            ('heard',
                ['j'],
                'Show heard stations log',
                self.responder.heard,
                {}),

            ('list',
                ['l'],
                'List all messages',
                self.responder.list,
                {}),

            ('listm',
                ['lm'],
                'List only messages addressed to you',
                self.responder.list_mine,
                {}),

            ('read',
                ['r'],
                'Read messages',
                self.responder.read,
                {'number': {'help': 'Message number to read'}}),

            ('readm',
                ['rm'],
                'Read only messages addressed to you',
                self.responder.read_mine,
                {}),

            ('send',
                ['s'],
                'Send a new message to a user',
                self.responder.send,
                {
                    '--callsign': {'help': 'Message recipient callsign'},
                    '--subject': {'help': 'Message subject'},
                    '--message': {'help': 'Message'},
                },),

            ('sendp',
                ['sp'],
                'Send a private message to a user',
                self.responder.send_private,
                {
                    '--callsign': {'help': 'Message recipient callsign'},
                    '--subject': {'help': 'Message subject'},
                    '--message': {'help': 'Message'},
                },),]

        return commands
