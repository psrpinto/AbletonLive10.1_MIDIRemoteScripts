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

import IOListener

class MixerListener:
    __doc__ = "Listener class adding Simpler Listener for Live"


    ablisten = {}
    Rablisten = {}

    mlisten = { "solo": {}, "mute": {}, "arm": {}, "current_monitoring_state": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "oml": {}, "omr": {}, "color": {}, "available_input_routing_channels": {}, "available_input_routing_types": {}, "available_output_routing_channels": {}, "available_output_routing_types": {}, "input_routing_type": {}, "input_routing_channel": {}, "output_routing_channel": {}, "output_routing_type": {}    }
    rlisten = { "solo": {}, "mute": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "color": {}, "available_output_routing_channels": {}, "available_output_routing_types": {}, "output_routing_channel": {}, "output_routing_type": {}   }
    masterlisten = { "panning": {}, "volume": {}, "crossfader": {} }
    
    ioListener = 0

    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
            self.tA_log = touchAble.tA_log
            self.ta_logger = touchAble.ta_logger
            self.error_logger = touchAble.error_logger
        else:
            return

        self.ioListener = IOListener.IOListener(self.c_instance, self.oscServer, self.touchAble)


    def rem_mixer_listeners(self):

        # Master Track
        for type in ("volume", "panning", "crossfader"):
            for tr in self.masterlisten[type]:
                if tr != None:
                    cb = self.masterlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")

        # Normal Tracks
        #for type in ("arm", "solo", "mute", "current_monitoring_state", "available_input_routing_channels", "available_input_routing_types", "available_output_routing_channels", "available_output_routing_types", "input_routing_channel", "input_routing_type", "output_routing_channel", "output_routing_type"):
        for type in ("arm", "solo", "mute", "current_monitoring_state"):

            for tr in self.mlisten[type]:
                if tr != None:
                    cb = self.mlisten[type][tr]
                    
                    if type == "arm":
                        if tr.can_be_armed == 1:
                            if tr.arm_has_listener(cb) == 1:
                                tr.remove_arm_listener(cb)
                    elif type == "current_monitoring_state":
                            if tr.can_be_armed == 1:
                                if tr.current_monitoring_state_has_listener(cb) == 1:
                                    tr.remove_current_monitoring_state_listener(cb)    
                    else:
                        test = eval("tr." + type+ "_has_listener(cb)")
                
                        if test == 1:
                            eval("tr.remove_" + type + "_listener(cb)")
                
        for type in ("volume", "panning"):
            for tr in self.mlisten[type]:
                if tr != None:
                    cb = self.mlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")
         
        for tr in self.mlisten["sends"]:
            if tr != None:
                for send in self.mlisten["sends"][tr]:
                    if send != None:
                        cb = self.mlisten["sends"][tr][send]

                        if send.value_has_listener(cb) == 1:
                            send.remove_value_listener(cb)
                        
                        
        for tr in self.mlisten["name"]:
            if tr != None:
                cb = self.mlisten["name"][tr]

                if tr.name_has_listener(cb) == 1:
                    tr.remove_name_listener(cb)

        for tr in self.mlisten["color"]:
            if tr != None:
                cb = self.mlisten["color"][tr]

                try:
                    if tr.color_has_listener(cb) == 1:
                        tr.remove_color_listener(cb)
                except:
                    pass
                    

        for tr in self.mlisten["oml"]:
            if tr != None:
                cb = self.mlisten["oml"][tr]

                if tr.output_meter_left_has_listener(cb) == 1:
                    tr.remove_output_meter_left_listener(cb)                    

        for tr in self.mlisten["omr"]:
            if tr != None:
                cb = self.mlisten["omr"][tr]

                if tr.output_meter_right_has_listener(cb) == 1:
                    tr.remove_output_meter_right_listener(cb)
                    
        # Return Tracks                
        #for type in ("solo", "mute", "available_output_routing_channels", "available_output_routing_types", "output_routing_channel", "output_routing_type"):
        for type in ("solo", "mute"):

            for tr in self.rlisten[type]:
                if tr != None:
                    cb = self.rlisten[type][tr]
                
                    test = eval("tr." + type+ "_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.remove_" + type + "_listener(cb)")
                
        for type in ("volume", "panning"):
            for tr in self.rlisten[type]:
                if tr != None:
                    cb = self.rlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")
         
        for tr in self.rlisten["sends"]:
            if tr != None:
                for send in self.rlisten["sends"][tr]:
                    if send != None:
                        cb = self.rlisten["sends"][tr][send]
                
                        if send.value_has_listener(cb) == 1:
                            send.remove_value_listener(cb)

        for tr in self.rlisten["name"]:
            if tr != None:
                cb = self.rlisten["name"][tr]

                if tr.name_has_listener(cb) == 1:
                    tr.remove_name_listener(cb)

        for tr in self.rlisten["color"]:
            if tr != None:
                cb = self.rlisten["color"][tr]
                try:
                    if tr.color_has_listener(cb) == 1:
                        tr.remove_color_listener(cb)
                except:
                    pass
        #self.mlisten = { "solo": {}, "mute": {}, "arm": {}, "current_monitoring_state": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "oml": {}, "omr": {}, "color": {}, "available_input_routing_channels": {}, "available_input_routing_types": {}, "available_output_routing_channels": {}, "available_output_routing_types": {}, "input_routing_type": {}, "input_routing_channel": {}, "output_routing_channel": {}, "output_routing_type": {}    }
        self.mlisten = { "solo": {}, "mute": {}, "arm": {}, "current_monitoring_state": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "oml": {}, "omr": {}, "color": {}    }

        #self.rlisten = { "solo": {}, "mute": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "color": {}, "available_output_routing_channels": {}, "available_output_routing_types": {}, "output_routing_channel": {}, "output_routing_type": {}   }
        self.rlisten = { "solo": {}, "mute": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "color": {} }

        self.masterlisten = { "panning": {}, "volume": {}, "crossfader": {} }

    
    def add_mixer_listeners(self):

        try:
            self.rem_mixer_listeners()
        except:
            self.tA_log("failed removing mixer listener")

        # Master Track
        tr = LiveUtils.getSong().master_track
        for type in ("volume", "panning", "crossfader"):
            self.add_master_listener(0, type, tr)
        
        #self.add_meter_listener(0, tr, 2)
        
        # Normal Tracks
        tracks = LiveUtils.getSong().tracks
        length_tracks = len(tracks)
        for track in range(length_tracks):
            tr = tracks[track]

            self.add_trname_listener(track, tr, 0)
            
            #if tr.has_audio_output:
                #self.add_meter_listener(track, tr)                
            
            for type in ("arm", "solo", "mute", "current_monitoring_state"):
                if type == "arm":
                    if tr.can_be_armed == 1:
                        self.add_mixert_listener(track, type, tr)

                elif type == "current_monitoring_state":
                    if tr.can_be_armed == 1:          
                        self.add_mixert_listener(track, type, tr)
                        
                else:
                    self.add_mixert_listener(track, type, tr)
            
            for type in ("volume", "panning"):
                self.add_mixerv_listener(track, type, tr)
            
            length_mixer_sends = len(tr.mixer_device.sends)
            for sid in range(length_mixer_sends):
                self.add_send_listener(track, tr, sid, tr.mixer_device.sends[sid])
        
        # Return Tracks
        tracks = LiveUtils.getSong().return_tracks
        length_tracks = len(tracks)
        for track in range(length_tracks):
            tr = tracks[track]

            self.add_trname_listener(track, tr, 1)
            
            for type in ("solo", "mute"):
                self.add_retmixert_listener(track, type, tr)
                
            for type in ("volume", "panning"):
                self.add_retmixerv_listener(track, type, tr)
            
            length_mixer_sends = len(tr.mixer_device.sends)
            for sid in range(length_mixer_sends):
                self.add_retsend_listener(track, tr, sid, tr.mixer_device.sends[sid])


    def mixert_changestate(self, type, tid, track, r = 0):
        val = eval("track." + type)
        #self.oscServer.sendOSC("/NSLOG_REPLACE", ("mixert_changestate"))

        if r == 1:
            self.oscServer.sendOSC('/return/' + type, (tid, int(val)))
        else:
            self.oscServer.sendOSC('/track/' + type, (tid, int(val)))
            if type == "arm":
                if val == 0:
                    if LiveUtils.getTrack(tid).playing_slot_index != -2:
                        cid = LiveUtils.getTrack(tid).playing_slot_index
                        self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 1))
                    else:
                        pass
                    
                elif val == 1:
                    if LiveUtils.getTrack(tid).playing_slot_index != -2:
                        cid = LiveUtils.getTrack(tid).playing_slot_index
                        if LiveUtils.getSong().overdub == 1 or LiveUtils.getTrack(tid).has_midi_input == 0:
                            self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))

                        else:
                            self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 1))

                    else:
                        pass
            else:
                pass


                    
    
    def send_changestate(self, tid, track, sid, send, r = 0):
        val = send.value
        
        if r == 1:
            self.oscServer.sendOSC('/return/send', (tid, sid, float(val)))   
        else:
            self.oscServer.sendOSC('/track/send', (tid, sid, float(val)))   


    # Mixer Callbacks
    def mixerv_changestate(self, type, tid, track, r = 0):
        val = eval("track.mixer_device." + type + ".value")
        types = { "panning": "pan", "volume": "volume", "crossfader": "crossfader" }
        
        if r == 2:
            self.oscServer.sendOSC('/master/' + types[type], (float(val)))
            if val == 0:
                self.oscServer.sendOSC('/master/' + types[type], (float(0.00000001)))

        elif r == 1:
            self.oscServer.sendOSC('/return/' + types[type], (tid, float(val)))
        else:
            self.oscServer.sendOSC('/track/' + types[type], (tid, val))    


   # Add track listeners
    def add_send_listener(self, tid, track, sid, send):
        if self.mlisten["sends"].has_key(track) != 1:
            self.mlisten["sends"][track] = {}
                    
        if self.mlisten["sends"][track].has_key(send) != 1:
            cb = lambda :self.send_changestate(tid, track, sid, send)
            
            self.mlisten["sends"][track][send] = cb
            send.add_value_listener(cb)
    
    def add_mixert_listener(self, tid, type, track):
        if self.mlisten[type].has_key(track) != 1:
            cb = lambda :self.mixert_changestate(type, tid, track)
            
            self.mlisten[type][track] = cb
            eval("track.add_" + type + "_listener(cb)")

    def add_routing_listener(self, tid, type, track_type, track, r = 0):
        if self.mlisten[type].has_key(track) != 1:
            cb = lambda :self.routing_stuff_changed(type, track_type, tid, track, r)
            
            self.mlisten[type][track] = cb
            eval("track.add_" + type + "_listener(cb)")

    def add_routing_lists_listener(self, tid, type, track_type, track, r = 0):
        if self.mlisten[type].has_key(track) != 1:
            cb = lambda :self.routing_lists_changed(type, track_type, tid, track, r)
        
            self.mlisten[type][track] = cb
            eval("track.add_" + type + "_listener(cb)")


            
    def add_mixerv_listener(self, tid, type, track):
        if self.mlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track)
            
            self.mlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")

    # Add master listeners
    def add_master_listener(self, tid, type, track):
        if self.masterlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track, 2)
            
            self.masterlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")
            
            
    # Add return listeners
    def add_retsend_listener(self, tid, track, sid, send):
        if self.rlisten["sends"].has_key(track) != 1:
            self.rlisten["sends"][track] = {}
                    
        if self.rlisten["sends"][track].has_key(send) != 1:
            cb = lambda :self.send_changestate(tid, track, sid, send, 1)
            
            self.rlisten["sends"][track][send] = cb
            send.add_value_listener(cb)
    
    def add_retmixert_listener(self, tid, type, track):
        if self.rlisten[type].has_key(track) != 1:
            cb = lambda :self.mixert_changestate(type, tid, track, 1)
            
            self.rlisten[type][track] = cb
            eval("track.add_" + type + "_listener(cb)")
            
    def add_retmixerv_listener(self, tid, type, track):
        if self.rlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track, 1)
            
            self.rlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")      


    def add_xFader_listeners(self):
        self.rem_xFader_listeners()
        tracks = LiveUtils.getSong().tracks
        for tr in range (len(tracks)):
            track = tracks[tr]
            self.add_xfade_listener(track, tr)
    
    def add_xfade_listener(self, track, tr):
        cb = lambda :self.xfade_assign_changed(track, tr)
        if self.ablisten.has_key(track) != 1:
            track.mixer_device.add_crossfade_assign_listener(cb)
            self.ablisten[track] = cb
        else:
            pass
    
    def rem_xFader_listeners(self):
        for track in self.ablisten:
            if track != None:
                if track.mixer_device.crossfade_assign_has_listener(self.ablisten[track]) == 1:
                    track.mixer_device.remove_crossfade_assign_listener(self.ablisten[track])
            else:
                pass
        self.ablisten = {}


    def xfade_assign_changed(self, track, tr):
        assign = 0
        assign = track.mixer_device.crossfade_assign
        self.oscServer.sendOSC("/track/crossfade_assign", (int(tr), int(assign)))
                
    
    
    def add_RxFader_listeners(self):
        self.rem_RxFader_listeners()
        tracks = LiveUtils.getSong().return_tracks
        for tr in range (len(tracks)):
            track = tracks[tr]
            self.add_Rxfade_listener(track, tr)
    
    def add_Rxfade_listener(self, track, tr):
        cb = lambda :self.Rxfade_assign_changed(track, tr)
        if self.Rablisten.has_key(track) != 1:
            track.mixer_device.add_crossfade_assign_listener(cb)
            self.Rablisten[track] = cb
        else:
            pass
    
    def rem_RxFader_listeners(self):
        for track in self.Rablisten:
            if track != None:
                if track.mixer_device.crossfade_assign_has_listener(self.Rablisten[track]) == 1:
                    track.mixer_device.remove_crossfade_assign_listener(self.Rablisten[track])
            else:
                pass
        self.Rablisten = {}
    
    
    def Rxfade_assign_changed(self, track, tr):
        assign = 0
        assign = track.mixer_device.crossfade_assign
        self.oscServer.sendOSC("/return/crossfade_assign", (int(tr), int(assign)))  

    # Track name changestate
    def trname_changestate(self, tid, track, r = 0):
        #trackTotal = len(LiveUtils.getTracks())
        #sceneTotal = len(LiveUtils.getScenes())
        #returnsTotal = len(LiveUtils.getSong().return_tracks)
        #self.oscServer.sendOSC("/set/size", (trackTotal, sceneTotal, returnsTotal))
        if r == 1:
            nm = track.name
            col = 0
            grouptrack = 0
            try:
                col = track.color
            except:
                pass
            #ascnm = (nm.encode('ascii', 'replace'))
            self.oscServer.sendOSC('/return', (tid, touchAbleUtils.repr3(nm), col))
        else:
            nm = track.name
            col = 0
            is_midi_track = track.has_midi_input
            
            try:
                col = track.color
            except:
                pass
            if track.is_foldable == 1:
                grouptrack = 1
            else:
                grouptrack = 0
            #ascnm = (nm.encode('ascii', 'replace'))

            live_pointer = ""

            self.oscServer.sendOSC('/track', (tid, touchAbleUtils.repr3(nm), col, grouptrack, int(is_midi_track),live_pointer))
            #self.devices_changed(track, tid, r)
            
    # Meter Changestate


    # Track name listener
    def add_trname_listener(self, tid, track, ret = 0):
        cb = lambda :self.trname_changestate(tid, track, ret)

        if ret == 1:
            if self.rlisten["name"].has_key(track) != 1:
                self.rlisten["name"][track] = cb
            if self.rlisten["color"].has_key(track) != 1:
                self.rlisten["color"][track] = cb

        else:
            if self.mlisten["name"].has_key(track) != 1:
                self.mlisten["name"][track] = cb
            if self.mlisten["color"].has_key(track) != 1:
                self.mlisten["color"][track] = cb

        
        track.add_name_listener(cb)
        try:
            track.add_color_listener(cb)
        except:
            pass
 

