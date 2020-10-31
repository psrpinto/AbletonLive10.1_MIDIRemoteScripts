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

class IOCallbacks:
    # LMH
    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
            self.ta_logger = touchAble.ta_logger
            self.error_logger = touchAble.error_logger

        else:
            return

        self.callbackManager.add(self.track_input_type, "/live/track/input_type")
        self.callbackManager.add(self.track_input_channel, "/live/track/input_channel")
        self.callbackManager.add(self.track_output_type, "/live/track/output_type")
        self.callbackManager.add(self.track_output_channel, "/live/track/output_channel")
        self.callbackManager.add(self.update_io, "/update_io")


    def update_io(self, msg):
        i = 0
        for track in LiveUtils.getSong().tracks:
            sendTrackIOLists(i, track)
            sendTrackIO(i, track)
            i = i + 1
    
    
    def track_input_type(self, msg):

        tid = msg[2]
        type = msg[3]
        
        
        track = LiveUtils.getSong().tracks[int(tid)]
        
        track.input_routing_type = track.available_input_routing_types[int(type)]
        
        self.sendTrackIO(tid, track, "input_routing_type")


    def track_input_channel(self, msg):
    
        tid = msg[2]
        type = msg[3]
    
        track = LiveUtils.getSong().tracks[int(tid)]
        track.input_routing_channel = track.available_input_routing_channels[type]
        
        self.sendTrackIO(tid, track, "input_routing_channel")

    def track_output_type(self, msg):
    
        tid = msg[2]
        type = msg[3]
    
        track = LiveUtils.getSong().tracks[int(tid)]
        track.output_routing_type = track.available_output_routing_types[type]
        self.sendTrackIO(tid, track, "output_routing_type")


    def track_output_channel(self, msg):
    
        tid = msg[2]
        type = msg[3]
    
        track = LiveUtils.getSong().tracks[int(tid)]
        track.output_routing_channel = track.available_output_routing_channels[type]
        self.sendTrackIO(tid, track, "output_routing_channel")


    def sendTrackIOLists(self, trackNumber, track, type = "", track_type = 0):
        name = touchAbleUtils.repr3(track.name)

        self.oscServer.sendOSC("/NSLOG_REPLACE", ("start sendtrackioLISTS", name, type, track_type))

        if type == "":
            io_data = [track_type, trackNumber, name, type]
    

        if type == "available_input_routing_channels" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            channels = track.available_input_routing_channels
            length = len(channels)
            io_data.append(length)
            for i in range(length):
                rout_type = channels[i]
                route_name = rout_type.display_name
                io_data.append(touchAbleUtils.repr3(route_name))
            if type != "":
                self.oscServer.sendOSC("/track/io/lists", io_data)
    
        
        
        if type == "available_input_routing_types" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            
            types = track.available_input_routing_types
            length = len(types)
            io_data.append(length)
            for i in range(length):
                rout_type = types[i]
                route_name = rout_type.display_name
                io_data.append(touchAbleUtils.repr3(route_name))
            if type != "":
                self.oscServer.sendOSC("/track/io/lists", io_data)



        if type == "available_output_routing_channels" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            channels = track.available_output_routing_channels
            length = len(channels)
            io_data.append(length)
            for i in range(length):
                rout_type = channels[i]
                route_name = rout_type.display_name
                io_data.append(touchAbleUtils.repr3(route_name))
            if type != "":
                self.oscServer.sendOSC("/track/io/lists", io_data)


        
        
        if type == "available_output_routing_types" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            types = track.available_output_routing_types
            length = len(types)
            io_data.append(length)
            for i in range(length):
                rout_type = types[i]
                route_name = rout_type.display_name
                io_data.append(touchAbleUtils.repr3(route_name))
            if type != "":
                self.oscServer.sendOSC("/track/io/lists", io_data)




        if type == "":
            self.oscServer.sendOSC("/track/io/lists", io_data)
                
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "end sendtrackioLISTS")

                
    
    def sendTrackIO(self, trackNumber, track, type = "", track_type = 0):
        #for current_type in ("available_input_routing_channels", "available_input_routing_types", "available_output_routing_channels", "available_output_routing_types", "input_routing_channel", "input_routing_type", "output_routing_channel", "output_routing_type"):
        name = touchAbleUtils.repr3(track.name)

        self.oscServer.sendOSC("/NSLOG_REPLACE", ("start sendtrackio", name, type, track_type))

        if type == "":
            io_data = [track_type, trackNumber, name, type]
            

        if type == "input_routing_type" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            track_input_route_type = track.input_routing_type
            track_input_route_type_name = track_input_route_type.display_name
            io_data.append(touchAbleUtils.repr3(track_input_route_type_name))
            found_port = 0
            
            types = track.available_input_routing_types
            length = len(types)
            input_type = track.input_routing_type
            
            for i in range(length):
                rout_type = types[i]
                if rout_type == input_type:
                    input_routing_type_number = i
                    io_data.append(input_routing_type_number)
                    found_port = 1
                    break
            if found_port == 0:
                io_data.append(0)
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)



        if type == "input_routing_channel" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            track_input_routing_channel = track.input_routing_channel
            track_input_routing_channel_name = track_input_routing_channel.display_name
            io_data.append(touchAbleUtils.repr3(track_input_routing_channel_name))
            found_port = 0
            
            
            channels = track.available_input_routing_channels
            length = len(channels)
            input_channel = track.input_routing_channel
            
            for i in range(length):
                rout_type = channels[i]
                if rout_type == input_channel:
                    input_routing_channel_number = i
                    io_data.append(input_routing_channel_number)
                    found_port = 1
                    break
            if found_port == 0:
                io_data.append(0)
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)



        if type == "output_routing_type" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            track_output_route_type = track.output_routing_type
            track_output_route_type_name = track_output_route_type.display_name
            io_data.append(touchAbleUtils.repr3(track_output_route_type_name))
            found_port = 0


            types = track.available_output_routing_types
            length = len(types)
            output_type = track.output_routing_type

        
            for i in range(length):
                rout_type = types[i]
                if rout_type == output_type:
                    output_routing_type_number = i
                    io_data.append(output_routing_type_number)
                    found_port = 1
                    break
            if found_port == 0:
                io_data.append(0)
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)



        if type == "output_routing_channel" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            track_output_routing_channel = track.output_routing_channel
            track_output_routing_channel_name = track_output_routing_channel.display_name
            io_data.append(touchAbleUtils.repr3(track_output_routing_channel_name))
            found_port = 0

            channels = track.available_output_routing_channels
            length = len(channels)
            output_channel = track.output_routing_channel

            for i in range(length):
                rout_type = channels[i]
                if rout_type == output_channel:
                    output_routing_channel_number = i
                    io_data.append(output_routing_channel_number)
                    found_port = 1
                    break
            if found_port == 0:
                io_data.append(0)
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)

