# LMH
from __future__ import with_statement

"""
# Copyright (C) 2019 Pascal Kaap
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

2.4. Implement a set of parameters for that are global to the session. Global controls: play, record, stop, pause, tap tempo.

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

class PluginListener:
    __doc__ = "Listener class adding Plugin Listener for Live"


    plugin_presets_listener = defaultdict(dict)
    plugin_selected_preset_index_listener = defaultdict(dict)

    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
        else:
            return

    def add_listener_for_plugindevice(self, device, track, tid, did, type, num, number_of_steps, indices):
        #self._log( "start updatingplugin_listener", True )
        
        a_version = Live.Application.get_application().get_major_version()
        minor_version = Live.Application.get_application().get_minor_version()
        
        
        if a_version < 9 or (a_version == 9 and minor_version < 5):
            return
        
        
        cb1 = lambda :self.update_plugin_presets(device, track, tid, did, type , number_of_steps, indices)
        cb2 = lambda :self.update_plugin_selected_preset_index(device, track, tid, did, type , number_of_steps, indices)
        key = '%s.%s' % (type, tid)

        plugin_presets_listener  = self.plugin_presets_listener[key]
        plugin_selected_preset_index_listener  = self.plugin_selected_preset_index_listener[key]

        if plugin_presets_listener.has_key(device) != 1:
            #self.update_plugin_presets(device, track, tid, did, type , number_of_steps, indices)
            device.add_presets_listener(cb1)
            plugin_presets_listener[device] = cb1
                
        if plugin_selected_preset_index_listener.has_key(device) != 1:
            #self.update_plugin_selected_preset_index(device, track, tid, did, type , number_of_steps, indices)
            device.add_selected_preset_index_listener(cb2)
            plugin_selected_preset_index_listener[device] = cb2


    def remove_plugin_listeners_of_track(self, track, tid, type):
        key = '%s.%s' % (type, tid)
        a_version = Live.Application.get_application().get_major_version()
        minor_version = Live.Application.get_application().get_minor_version()


        if a_version < 9 or (a_version == 9 and minor_version < 5):
            return

        if self.plugin_presets_listener.has_key(key) == 1:
            plugin_presets_listener = self.plugin_presets_listener[key]
            for pr in plugin_presets_listener:
                if pr != None:
                    ocb = plugin_presets_listener[pr]
                    if pr.presets_has_listener(ocb) == 1:
                        pr.remove_presets_listener(ocb)

            del self.plugin_presets_listener[key]
        
        if self.plugin_selected_preset_index_listener.has_key(key) == 1:
            plugin_selected_preset_index_listener = self.plugin_selected_preset_index_listener[key]
            for pr in plugin_selected_preset_index_listener:
                if pr != None:
                    ocb = plugin_selected_preset_index_listener[pr]
                    if pr.selected_preset_index_has_listener(ocb) == 1:
                        pr.remove_selected_preset_index_listener(ocb)
            
            del self.plugin_selected_preset_index_listener[key]



    def update_plugin_parameters(self,device, track, tid, did, type , number_of_steps, indices):

        a_version = Live.Application.get_application().get_major_version()
        minor_version = Live.Application.get_application().get_minor_version()


        if a_version < 9 or (a_version == 9 and minor_version < 5):
            return

        if device.class_name == 'PluginDevice' or device.class_name == 'AuPluginDevice':
            self.update_plugin_presets(device, track, tid, did, type , number_of_steps, indices)
            self.update_plugin_selected_preset_index(device, track, tid, did, type , number_of_steps, indices)


    def update_plugin_presets(self, device, track, tid, did, type , number_of_steps, indices):

        a_version = Live.Application.get_application().get_major_version()
        minor_version = Live.Application.get_application().get_minor_version()


        if a_version < 9 or (a_version == 9 and minor_version < 5):
            return

        data = [int(type)]
        data.append(int(tid))
        data.append(int(did))
        data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            data.append(int(indices[index]))

        data.append(int(len(device.presets)))
        
        for index in range(len(device.presets)):
            preset = device.presets[index]
            data.append(touchAbleUtils.repr3(preset))
        
        self.oscServer.sendOSC("/device/plugin/update_plugin_presets", data)
        
    def update_plugin_selected_preset_index(self, device, track, tid, did, type , number_of_steps, indices):
    
        a_version = Live.Application.get_application().get_major_version()
        minor_version = Live.Application.get_application().get_minor_version()


        if a_version < 9 or (a_version == 9 and minor_version < 5):
            return

        data = [int(type)]
        data.append(int(tid))
        data.append(int(did))
        data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            data.append(int(indices[index]))
        
        number = device.selected_preset_index

        data.append(int(number))

        self.oscServer.sendOSC("/device/plugin/update_plugin_selected_preset_index", data)




