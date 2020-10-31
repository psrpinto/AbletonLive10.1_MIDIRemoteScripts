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


class CompressorListener:
    __doc__ = "Listener class adding Simpler Listener for Live"

    compressor_available_input_routing_channels_listener = defaultdict(dict)
    compressor_available_input_routing_types_listener = defaultdict(dict)
    compressor_input_routing_channel_listener = defaultdict(dict)
    compressor_input_routing_type_listener = defaultdict(dict)

    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
        else:
            return

    def add_listener_for_compressor(self, device, track, tid, did, type, num, number_of_steps, indices):
        cb1 = lambda :self.update_available_input_routing_channels(device, track, tid, did, type , number_of_steps, indices)
    
        cb2 = lambda :self.update_available_input_routing_types(device, track, tid, did, type , number_of_steps, indices)
    
        cb3 = lambda :self.update_input_routing_channel(device, track, tid, did, type , number_of_steps, indices)
        
        cb4 = lambda :self.update_input_routing_type(device, track, tid, did, type , number_of_steps, indices)
        key = '%s.%s' % (type, tid)

        compressor_available_input_routing_channels_listener  = self.compressor_available_input_routing_channels_listener[key]
        compressor_available_input_routing_types_listener = self.compressor_available_input_routing_types_listener[key]
        compressor_input_routing_channel_listener = self.compressor_input_routing_channel_listener[key]
        compressor_input_routing_type_listener  = self.compressor_input_routing_type_listener[key]

        if compressor_available_input_routing_channels_listener.has_key(device) != 1:
            #self.update_available_input_routing_channels(device, track, tid, did, type , number_of_steps, indices)
            device.add_available_input_routing_channels_listener(cb1)
            compressor_available_input_routing_channels_listener[device] = cb1

                    
        if compressor_available_input_routing_types_listener.has_key(device) != 1:
            #self.oscServer.sendOSC("/NSLOG_REPLACE", "add av. in. rout. types")
            #self.update_available_input_routing_types(device, track, tid, did, type , number_of_steps, indices)
            device.add_available_input_routing_types_listener(cb2)
            compressor_available_input_routing_types_listener[device] = cb2

            #self.oscServer.sendOSC("/NSLOG_REPLACE", "end add av. in. rout. types")


        if compressor_input_routing_channel_listener.has_key(device) != 1:
            #self.update_input_routing_channel(device, track, tid, did, type , number_of_steps, indices)
            device.add_input_routing_channel_listener(cb3)
            compressor_input_routing_channel_listener[device] = cb3
        
        if compressor_input_routing_type_listener.has_key(device) != 1:
            #self.update_input_routing_type(device, track, tid, did, type , number_of_steps, indices)
            device.add_input_routing_type_listener(cb4)
            compressor_input_routing_type_listener[device] = cb4

    def remove_compressor_listeners_of_track(self, track, tid, type):
        key = '%s.%s' % (type, tid)

        if self.compressor_available_input_routing_channels_listener.has_key(key) == 1:
            compressor_available_input_routing_channels_listener = self.compressor_available_input_routing_channels_listener[key]
            for pr in compressor_available_input_routing_channels_listener:
                if pr != None:
                    ocb = compressor_available_input_routing_channels_listener[pr]
                    if pr.available_input_routing_channels_has_listener(ocb) == 1:
                        pr.remove_available_input_routing_channels_listener(ocb)

            del self.compressor_available_input_routing_channels_listener[key]
            self.oscServer.sendOSC("/NSLOG_REPLACE", "removed available input listener")

        
        if self.compressor_available_input_routing_types_listener.has_key(key) == 1:
            compressor_available_input_routing_types_listener = self.compressor_available_input_routing_types_listener[key]
            for pr in compressor_available_input_routing_types_listener:
                if pr != None:
                    ocb = compressor_available_input_routing_types_listener[pr]
                    if pr.available_input_routing_types_has_listener(ocb) == 1:
                        pr.remove_available_input_routing_types_listener(ocb)
            del self.compressor_available_input_routing_types_listener[key]
            self.oscServer.sendOSC("/NSLOG_REPLACE", "removed available routing types listener")

    
        if self.compressor_input_routing_channel_listener.has_key(key) == 1:
            compressor_input_routing_channel_listener = self.compressor_input_routing_channel_listener[key]
            for pr in compressor_input_routing_channel_listener:
                if pr != None:
                    ocb = compressor_input_routing_channel_listener[pr]
                    if pr.input_routing_channel_has_listener(ocb) == 1:
                        pr.remove_input_routing_channel_listener(ocb)
            del self.compressor_input_routing_channel_listener[key]
            self.oscServer.sendOSC("/NSLOG_REPLACE", "removed input routing channel listener")

    
    
        if self.compressor_input_routing_type_listener.has_key(key) == 1:
            compressor_input_routing_type_listener = self.compressor_input_routing_type_listener[key]
            for pr in compressor_input_routing_type_listener:
                if pr != None:
                    ocb = compressor_input_routing_type_listener[pr]
                    if pr.input_routing_type_has_listener(ocb) == 1:
                        pr.remove_input_routing_type_listener(ocb)
            del self.compressor_input_routing_type_listener[key]
            self.oscServer.sendOSC("/NSLOG_REPLACE", "removed input routing types listener")              

    
    def update_compressor_parameters(self,device, track, tid, did, type , number_of_steps, indices):


        if device.class_name == 'Compressor2':
            #self.oscServer.sendOSC("/device/compressor/update_available_input_routing_channels0", 1)

            self.update_available_input_routing_channels(device, track, tid, did, type , number_of_steps, indices)
            self.update_available_input_routing_types(device, track, tid, did, type , number_of_steps, indices)
            self.update_input_routing_channel(device, track, tid, did, type , number_of_steps, indices)
            self.update_input_routing_type(device, track, tid, did, type , number_of_steps, indices)


    def update_available_input_routing_channels(self, device, track, tid, did, type , number_of_steps, indices):

        data = [int(type)]
        data.append(int(tid))
        data.append(int(did))
        data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            data.append(int(indices[index]))

        input_routings = device.available_input_routing_channels
        length = len(input_routings)

        data.append(length)
        for index in range(length):
            input_routing = input_routings[index]
            data.append(touchAbleUtils.repr3(input_routing.display_name))

        self.oscServer.sendOSC("/device/compressor/update_available_input_routing_channels", data)
   

    def update_available_input_routing_types(self, device, track, tid, did, type , number_of_steps, indices):
       
        data = [int(type)]
        data.append(int(tid))
        data.append(int(did))
        data.append(int(number_of_steps))
       
        for index in range(number_of_steps * 2):
            data.append(int(indices[index]))
    
        input_routing_types = device.available_input_routing_types
        length = len(input_routing_types)
        data.append(length)

        for index in range(length):
            input_type = input_routing_types[index]
            data.append(touchAbleUtils.repr3(input_type.display_name))
                       
        self.oscServer.sendOSC("/device/compressor/update_available_input_routing_types", data)
            
            
   
    def update_input_routing_channel(self,device, track, tid, did, type , number_of_steps, indices):
        
        data = [int(type)]
        data.append(int(tid))
        data.append(int(did))
        data.append(int(number_of_steps))
            
        for index in range(number_of_steps * 2):
            data.append(int(indices[index]))
        
        number = 0
        
        
        
        input_routing_channels = device.available_input_routing_channels
        length = len(input_routing_channels)
        input_channel = device.input_routing_channel
        
        for index in range(length):
            input_type = input_routing_channels[index]
            if input_type == input_channel:
                number = index
        
        data.append(int(number))
            
        self.oscServer.sendOSC("/device/compressor/update_input_routing_channel", data)

        
    def update_input_routing_type(self, device, track, tid, did, type , number_of_steps, indices):

        data = [int(type)]
        data.append(int(tid))
        data.append(int(did))
        data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            data.append(int(indices[index]))

        number = 0
        
        input_routing_types = device.available_input_routing_types
        length = len(input_routing_types)
        input_typ = device.input_routing_type
        
    
        for index in range(length):
            input_type = input_routing_types[index]
            if input_type == input_typ:
                number = index
        
        data.append(int(number))
        
        self.oscServer.sendOSC("/device/compressor/update_input_routing_type", data)

