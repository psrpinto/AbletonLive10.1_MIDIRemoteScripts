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


class SetListener:
    __doc__ = "Listener class adding Simpler Listener for Live"
    log_message = 0
    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
            self.log_message = self.touchAble.log_message
            self.error_log = touchAble.error_log
            self.ta_logger = touchAble.ta_logger
            self.error_logger = touchAble.error_logger
        else:
            return

    def add_set_listeners(self):

        try:
            self.add_transport_listener()
        except:
            self.error_log("add_transport_listener failed")
        try:
            self.add_tempo_listener()
        except:
            self.error_log("add_tempo_listener failed")
        try:
            self.add_overdub_listener()
        except:
            self.error_log("add_overdub_listener failed")
        try:
            self.add_metronome_listener()
        except:
            self.error_log("add_metronome_listener failed")
        try:
            self.add_record_listener()
        except:
            self.error_log("add_record_listener failed")
        try:
            self.add_can_capture_midi_listener()
        except:
            self.error_log("add_can_capture_midi_listener failed")
        try:
            self.add_song_loop_length_listener()
        except:
            self.error_log("add_song_loop_length_listener failed")
        try:
            self.add_song_loop_start_listener()
        except:
            self.error_log("add_song_loop_start_listener failed")
        try:
            self.add_quant_listeners()
        except:
            self.error_log("add_quant_listeners failed")
    
        
        
        try:
            self.add_session_record_listener()
            self.add_session_record_status_listener()
            self.add_re_enable_automation_enabled_listener()
            self.add_session_automation_record_listener()
            self.add_arrangement_overdub_listener()
            self.oscServer.sendOSC('/remix/oscserver/startup', 2)
        except:
            self.oscServer.sendOSC("live/", 8)



    def rem_set_listeners(self):

        try:
            try:
                self.rem_tempo_listener()
            except:
                self.error_log("rem_tempo_listener failed")
            
            
            try:
                self.rem_overdub_listener()
            except:
                self.error_log("rem_overdub_listener failed")
            
            
            try:
                self.rem_metronome_listener()
            except:
                self.error_log("rem_metronome_listener failed")
            
            
           
            try:
                self.rem_session_record_listener()
                self.rem_session_record_status_listener()
                self.rem_re_enable_automation_enabled_listener()
                self.rem_session_automation_record_listener()
                self.rem_arrangement_overdub_listener()

            except:
                self.error_log("remove live 9 listeners failed")


            try:
                self.rem_record_listener()
            except:
                self.error_log("rem_record_listener failed")

            try:
                self.rem_transport_listener()
            except:
                self.error_log("rem_transport_listener failed")
            
            try:
                a_version = Live.Application.get_application().get_major_version()
                if a_version >= 10.0:
                    self.rem_can_capture_midi_listener()
            except:
                self.error_log("rem_can_caputre_midi_listener failed")
            
            try:
                self.rem_song_loop_length_listener()
            except:
                self.error_log("rem_loop_length_listener failed")
            
            try:
                self.rem_song_loop_start_listener()
            except:
                self.error_log("rem_loop_start_listener failed")

            try:
                self.rem_quant_listeners()
            except:
                self.error_log("rem_quant_listeners failed")
        
        except:
            self.error_log("failed to remove set listener")



    def add_tempo_listener(self):
        self.rem_tempo_listener()
        if LiveUtils.getSong().tempo_has_listener(self.tempo_change) != 1:
            LiveUtils.getSong().add_tempo_listener(self.tempo_change)
        
    def rem_tempo_listener(self):
        if LiveUtils.getSong().tempo_has_listener(self.tempo_change) == 1:
            LiveUtils.getSong().remove_tempo_listener(self.tempo_change)
    
    def tempo_change(self):
        tempo = LiveUtils.getTempo()
        self.oscServer.sendOSC("/set/tempo", (tempo))

    def add_quant_listeners(self):
        self.rem_quant_listeners()

        if LiveUtils.getSong().clip_trigger_quantization_has_listener(self.quant_change) != 1:
            LiveUtils.getSong().add_clip_trigger_quantization_listener(self.quant_change)
            
        if LiveUtils.getSong().midi_recording_quantization_has_listener(self.quant_change) != 1:
            LiveUtils.getSong().add_midi_recording_quantization_listener(self.quant_change)
        
    def rem_quant_listeners(self):
        if LiveUtils.getSong().clip_trigger_quantization_has_listener(self.quant_change) == 1:
            LiveUtils.getSong().remove_clip_trigger_quantization_listener(self.quant_change)
        if LiveUtils.getSong().midi_recording_quantization_has_listener(self.quant_change) == 1:
            LiveUtils.getSong().remove_midi_recording_quantization_listener(self.quant_change)

    def quant_change(self):
        tquant = LiveUtils.getSong().clip_trigger_quantization
        rquant = LiveUtils.getSong().midi_recording_quantization
        self.oscServer.sendOSC("/set/quantization", (int(LiveUtils.getSong().clip_trigger_quantization), int(LiveUtils.getSong().midi_recording_quantization)))   
    
    def add_song_loop_length_listener(self):
        self.looplength_change()
        if LiveUtils.getSong().loop_length_has_listener(self.looplength_change) != 1:
            LiveUtils.getSong().add_loop_length_listener(self.looplength_change)

    def add_song_loop_start_listener(self):
        self.loopstart_change()
        if LiveUtils.getSong().loop_start_has_listener(self.loopstart_change) != 1:
            LiveUtils.getSong().add_loop_start_listener(self.loopstart_change)

    def rem_song_loop_length_listener(self):
        if LiveUtils.getSong().loop_length_has_listener(self.looplength_change) == 1:
            LiveUtils.getSong().remove_loop_length_listener(self.looplength_change)

    def rem_song_loop_start_listener(self):
        if LiveUtils.getSong().loop_start_has_listener(self.loopstart_change) == 1:
            LiveUtils.getSong().remove_loop_start_listener(self.loopstart_change)
    
    def add_can_capture_midi_listener(self):
        a_version = Live.Application.get_application().get_major_version()
        if a_version >= 10.0:
            self.can_capture_midi_change()
            if LiveUtils.getSong().can_capture_midi_has_listener(self.can_capture_midi_change) != 1:
                LiveUtils.getSong().add_can_capture_midi_listener(self.can_capture_midi_change)

    def rem_can_capture_midi_listener(self):
        a_version = Live.Application.get_application().get_major_version()
        if a_version >= 10.0:
            if LiveUtils.getSong().can_capture_midi_has_listener(self.can_capture_midi_change) == 1:
                LiveUtils.getSong().remove_can_capture_midi_listener(self.can_capture_midi_change)
    
    def add_transport_listener(self):
        if LiveUtils.getSong().is_playing_has_listener(self.transport_change) != 1:
            LiveUtils.getSong().add_is_playing_listener(self.transport_change)
            
    def rem_transport_listener(self):
        if LiveUtils.getSong().is_playing_has_listener(self.transport_change) == 1:
            LiveUtils.getSong().remove_is_playing_listener(self.transport_change)
    
    def transport_change(self):
        self.oscServer.sendOSC("/set/playing_status", (LiveUtils.getSong().is_playing and 2 or 1))

    def can_capture_midi_change(self):
        a_version = Live.Application.get_application().get_major_version()
        if a_version >= 10.0:
            self.oscServer.sendOSC("/set/can_capture_midi", (int(LiveUtils.getSong().can_capture_midi + 1)))

    def looplength_change(self):
        self.oscServer.sendOSC("/set/loop_length", (LiveUtils.getSong().loop_length))
    
    def loopstart_change(self):
        self.oscServer.sendOSC("/set/loop_start", (LiveUtils.getSong().loop_start))

    def add_session_record_listener(self):
        self.rem_session_record_listener()
        
        if LiveUtils.getSong().session_record_has_listener(self.session_record_change) != 1:
            LiveUtils.getSong().add_session_record_listener(self.session_record_change)

    def rem_session_record_listener(self):
        if LiveUtils.getSong().session_record_has_listener(self.session_record_change) == 1:
            LiveUtils.getSong().remove_session_record_listener(self.session_record_change)


    def add_session_record_status_listener(self):
        self.rem_session_record_status_listener()
        
        if LiveUtils.getSong().session_record_status_has_listener(self.session_record_status_changed) != 1:
            LiveUtils.getSong().add_session_record_status_listener(self.session_record_status_changed)
    
    def rem_session_record_status_listener(self):
        if LiveUtils.getSong().session_record_status_has_listener(self.session_record_status_changed) == 1:
            LiveUtils.getSong().remove_session_record_status_listener(self.session_record_status_changed)


    def add_re_enable_automation_enabled_listener(self):
        self.rem_re_enable_automation_enabled_listener()
        
        if LiveUtils.getSong().re_enable_automation_enabled_has_listener(self.re_enable_automation_enabled_changed) != 1:
            LiveUtils.getSong().add_re_enable_automation_enabled_listener(self.re_enable_automation_enabled_changed)
    
    def rem_re_enable_automation_enabled_listener(self):
        if LiveUtils.getSong().re_enable_automation_enabled_has_listener(self.re_enable_automation_enabled_changed) == 1:
            LiveUtils.getSong().remove_re_enable_automation_enabled_listener(self.re_enable_automation_enabled_changed)



    def add_session_automation_record_listener(self):
        self.rem_session_automation_record_listener()
        
        if LiveUtils.getSong().session_automation_record_has_listener(self.session_automation_record_change) != 1:
            LiveUtils.getSong().add_session_automation_record_listener(self.session_automation_record_change)
    
    def rem_session_automation_record_listener(self):
        if LiveUtils.getSong().session_automation_record_has_listener(self.session_automation_record_change) == 1:
            LiveUtils.getSong().remove_session_automation_record_listener(self.session_automation_record_change)

    
    def add_arrangement_overdub_listener(self):
        self.rem_arrangement_overdub_listener()
        
        if LiveUtils.getSong().arrangement_overdub_has_listener(self.overdub_change) != 1:
            LiveUtils.getSong().add_arrangement_overdub_listener(self.overdub_change)
    
    def rem_arrangement_overdub_listener(self):
        if LiveUtils.getSong().arrangement_overdub_has_listener(self.overdub_change) == 1:
            LiveUtils.getSong().remove_arrangement_overdub_listener(self.overdub_change)



    def session_record_change(self):
        overdub = LiveUtils.getSong().session_record
        self.oscServer.sendOSC("/live/set/session_record", (int(overdub)+1))
    
        trackNumber = 0
        numberOfTracks = len(LiveUtils.getSong().tracks)
        for i in range(numberOfTracks):
            track = LiveUtils.getSong().tracks[i]
            if track.can_be_armed == 1:
                if track.arm == 1:
                    if track.playing_slot_index != -2:
                        if track.playing_slot_index != -1:
                            tid = trackNumber
                            cid = track.playing_slot_index
                            if track.clip_slots[cid].clip.is_audio_clip == 0:
                                if overdub == 1:
                                    self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))
                                else:
                                    self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 1))
                            else:
                                self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))
        
            trackNumber = trackNumber+1
    

    def session_record_status_changed(self):
        overdub = LiveUtils.getSong().session_record_status
        self.oscServer.sendOSC("/live/set/session_record_status", (int(overdub)+1))

    def re_enable_automation_enabled_changed(self):
        overdub = LiveUtils.getSong().re_enable_automation_enabled
        self.oscServer.sendOSC("/live/set/re_enable_automation_enabled", (int(overdub)+1))

    def session_automation_record_change(self):
        overdub = LiveUtils.getSong().session_automation_record
        self.oscServer.sendOSC("/live/set/session_automation_record", (int(overdub)+1))

    def add_overdub_listener(self):
        self.rem_overdub_listener()
    
        if LiveUtils.getSong().overdub_has_listener(self.overdub_change) != 1:
            LiveUtils.getSong().add_overdub_listener(self.overdub_change)
        
    def rem_overdub_listener(self):
        if LiveUtils.getSong().overdub_has_listener(self.overdub_change) == 1:
            LiveUtils.getSong().remove_overdub_listener(self.overdub_change)

    def add_metronome_listener(self):
        self.rem_metronome_listener()
    
        if LiveUtils.getSong().metronome_has_listener(self.metronome_change) != 1:
            LiveUtils.getSong().add_metronome_listener(self.metronome_change)
        
    def rem_metronome_listener(self):
        if LiveUtils.getSong().metronome_has_listener(self.metronome_change) == 1:
            LiveUtils.getSong().remove_metronome_listener(self.metronome_change)

    def metronome_change(self):
        metronome = LiveUtils.getSong().metronome
        self.oscServer.sendOSC("/set/metronome_status", (int(metronome) + 1))
        
    def overdub_change(self):
        try:
            overdub = LiveUtils.getSong().arrangement_overdub
        except:
            overdub = LiveUtils.getSong().overdub

        self.oscServer.sendOSC("/set/overdub_status", (int(overdub) + 1))
        trackNumber = 0
        if Live.Application.get_application().get_major_version() == 8:
            for track in LiveUtils.getSong().tracks:
                if track.can_be_armed == 1:
                    if track.arm == 1:
                        if track.playing_slot_index != -2:
                            tid = trackNumber
                            cid = track.playing_slot_index
                            if track.clip_slots[cid].clip.is_audio_clip == 0:
                                if overdub == 1:
                                    self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))
                                else:
                                    self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 1))
                            else:
                                self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))
        
                trackNumber = trackNumber+1



    def add_record_listener(self):
        self.rem_record_listener()
    
        if LiveUtils.getSong().record_mode_has_listener(self.record_change) != 1:
            LiveUtils.getSong().add_record_mode_listener(self.record_change)
        
    def rem_record_listener(self):
        if LiveUtils.getSong().record_mode_has_listener(self.record_change) == 1:
            LiveUtils.getSong().remove_record_mode_listener(self.record_change)

    def record_change(self):
        record = LiveUtils.getSong().record_mode
        self.oscServer.sendOSC("/set/recording_status", (int(record) + 1))