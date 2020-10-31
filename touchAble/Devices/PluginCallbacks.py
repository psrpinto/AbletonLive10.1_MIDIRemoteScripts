"""
# Copyright (C) 2019 Zerodebug
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

2.3. Implement a set of parameters for controlling all tracks.
The example plug-in will consist of 10 mixer channels. Each channel will contain: volume, pan, sends, solo, mute, track name, record arm, automation state.

"""

import touchAble.Utils.touchAbleUtils as touchAbleUtils
import struct
import Live
import touchAble.Utils.LiveUtils as LiveUtils
import time
import unicodedata
import thread
from threading import Timer
from collections import defaultdict
from touchAble.Utils.Logger import Logger as Logger
from time import sleep

class PluginCallbacks:
    # LMH
    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble


        else:
            return


        self.callbackManager.add(self.set_plugin_preset, "/device/plugin/set_preset_index")

    def get_device_for_message(self,msg):

        type = msg[2]
        tid = msg[3]
        did = msg[4]
        
        number_of_steps = msg[5]
        
        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track

        device = track.devices[did]
        
        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]
        

        return device

    def set_plugin_preset(self, msg):

        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        preset_index = msg[new_index]
        a_version = Live.Application.get_application().get_major_version()
        minor_version = Live.Application.get_application().get_minor_version()

        if (device.class_name == 'PluginDevice' or device.class_name == 'AuPluginDevice') and (a_version >= 10 or (a_version > 9 and minor_version >= 5)):
            plugin = device
            device.selected_preset_index = preset_index
