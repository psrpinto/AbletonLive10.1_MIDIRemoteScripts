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


class ClipListener:
    __doc__ = "Listener class adding Simpler Listener for Live"



    oldloop_start = {}
    oldloop_end = {}
    oldplay_start = {}
    oldplay_end = {}
    loop_length = {}
    trackid = {}
    clipid = {}
    oldlooping  = {}
    hotlooping = {}

    clipwarplisten = {}
    clipwarpmodelisten = {}
    clipmutelisten = {}
    cliplooplisten = {}
    clipgainlisten = {}
    clipcoarselisten = {}
    clipfinelisten = {}

    noteListeners = {}
    noteBuffers = defaultdict(list)


    isCheckingLoop = 0

    plisten = {}
    fplisten = {}
    clisten = {}
    slisten = {}
    sslisten = {}
    pplisten = {}
    cnlisten = {}
    smlisten = {}
    emlisten = {}
    lslisten = {}
    lelisten = {}
    cclisten = {}


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



    def add_clip_listeners(self):
        self.oscServer.sendOSC("/NSLOG_REPLACE", "add clip listener")

        self.rem_clip_listeners()
        self.oscServer.sendOSC("/NSLOG_REPLACE", "removed old clip listener")

        tracks = self.getslots()
        length_tracks = len(tracks)
        for track in range(length_tracks):
            length_clips = len(tracks[track])
            for clip in range(length_clips):
                c = tracks[track][clip]
                if c.clip != None:
                    self.add_cliplistener(c.clip, track, clip) 
                self.add_slotlistener(c, track, clip)
                
    def add_cliplistener(self, clip, tid, cid):

        cb = lambda :self.clip_changestate(clip, tid, cid)
        
        if self.clisten.has_key(clip) != 1:
            clip.add_playing_status_listener(cb)
            self.clisten[clip] = cb
        
        #if clip.is_audio_clip == 0:
        #cb4 = lambda :self.notesChanged(tid, cid, clip)
        #if self.noteListeners.has_key(clip) != 1:
        # clip.add_notes_listener(cb4)
        # self.noteListeners[clip] = cb4
            

        cb3 = lambda :self.clip_name(clip, tid, cid)
        if self.cnlisten.has_key(clip) != 1:
            clip.add_name_listener(cb3)
            self.cnlisten[clip] = cb3

        if self.cclisten.has_key(clip) != 1:
            clip.add_color_listener(cb3)
            self.cclisten[clip] = cb3

        cb4 = lambda :self.clip_marker(clip, tid, cid)

        if self.smlisten.has_key(clip) != 1:
            clip.add_start_marker_listener(cb4)
            self.smlisten[clip] = cb4
                
        if self.emlisten.has_key(clip) != 1:
            clip.add_end_marker_listener(cb4)
            self.emlisten[clip] = cb4


        if self.lslisten.has_key(clip) != 1:
            clip.add_loop_start_listener(cb4)
            self.lslisten[clip] = cb4
        
        if self.lelisten.has_key(clip) != 1:
            clip.add_loop_end_listener(cb4)
            self.lelisten[clip] = cb4
    
        
        cb5 = lambda :self.file_path_changed(clip, tid, cid)

        if self.fplisten.has_key(clip) != 1 and clip.is_audio_clip:
            clip.add_file_path_listener(cb5)
            self.fplisten[clip] = cb5

        cb6 = lambda :self.clip_loop_status_changed(clip, tid, cid)

        if self.cliplooplisten.has_key(clip) != 1:
            clip.add_looping_listener(cb6)
            self.cliplooplisten[clip] = cb6

        cb7 = lambda :self.clip_warping_status_changed(clip, tid, cid)

        if self.clipwarplisten.has_key(clip) != 1 and clip.is_audio_clip:
            clip.add_warping_listener(cb7)
            self.clipwarplisten[clip] = cb7




        cb007 = lambda :self.clip_warping_mode_changed(clip, tid, cid)

        if self.clipwarpmodelisten.has_key(clip) != 1 and clip.is_audio_clip:
            clip.add_warp_mode_listener(cb007)
            self.clipwarpmodelisten[clip] = cb007


        
        cb8 = lambda :self.clip_muted_status_changed(clip, tid, cid)
    
        if self.clipmutelisten.has_key(clip) != 1:
            clip.add_muted_listener(cb8)
            self.clipmutelisten[clip] = cb8

        cb9 = lambda :self.clip_gain_changed(clip, tid, cid)

        if self.clipgainlisten.has_key(clip) != 1 and clip.is_audio_clip:
            clip.add_gain_listener(cb9)
            self.clipgainlisten[clip] = cb9

        cb10 = lambda :self.clip_coarse_changed(clip, tid, cid)
    
        if self.clipcoarselisten.has_key(clip) != 1 and clip.is_audio_clip:
            clip.add_pitch_coarse_listener(cb10)
            self.clipcoarselisten[clip] = cb10
        
        cb11 = lambda :self.clip_fine_changed(clip, tid, cid)

        if self.clipfinelisten.has_key(clip) != 1 and clip.is_audio_clip:
            clip.add_pitch_fine_listener(cb11)
            self.clipfinelisten[clip] = cb11



    def add_slotlistener(self, slot, tid, cid):
        cb = lambda :self.slot_changestate(slot, tid, cid)

        if self.slisten.has_key(slot) != 1:
            slot.add_has_clip_listener(cb)
            self.slisten[slot] = cb

        cb2 = lambda :self.stop_changestate(slot, tid, cid)
        if self.sslisten.has_key(slot) != 1:
            tracks = LiveUtils.getSong().tracks
            track = tracks[tid]
            if track.is_foldable != 1:
                slot.add_has_stop_button_listener(cb2)
                self.sslisten[slot] = cb2
            else:
                pass

    def rem_clip_listeners(self):

        for slot in self.slisten:
            if slot != None:
                if slot.has_clip_has_listener(self.slisten[slot]) == 1:
                    slot.remove_has_clip_listener(self.slisten[slot])
                    
        self.slisten = {}
    

        for slot in self.sslisten:
            if slot != None:
                if slot.has_stop_button_has_listener(self.sslisten[slot]) == 1:
                    slot.remove_has_stop_button_listener(self.sslisten[slot])
                    
        self.sslisten = {}
    
        
        for clip in self.clisten:
            if clip != None:
                if clip.playing_status_has_listener(self.clisten[clip]) == 1:
                    clip.remove_playing_status_listener(self.clisten[clip])
                
        self.clisten = {}

        for clip in self.pplisten:
            if clip != None:
                if clip.playing_position_has_listener(self.pplisten[clip]) == 1:
                    clip.remove_playing_position_listener(self.pplisten[clip])
                
        self.pplisten = {}
    

        for clip in self.cnlisten:
            if clip != None:
                if clip.name_has_listener(self.cnlisten[clip]) == 1:
                    clip.remove_name_listener(self.cnlisten[clip])
                
        self.cnlisten = {}
        
        for clip in self.smlisten:
            if clip != None:
                if clip.start_marker_has_listener(self.smlisten[clip]) == 1:
                    clip.remove_start_marker_listener(self.smlisten[clip])
                    
        self.smlisten = {}
        
        for clip in self.emlisten:
            if clip != None:
                if clip.end_marker_has_listener(self.emlisten[clip]) == 1:
                    clip.remove_end_marker_listener(self.emlisten[clip])

        self.emlisten = {}
        
        for clip in self.lslisten:
            if clip != None:
                if clip.loop_start_has_listener(self.lslisten[clip]) == 1:
                    clip.remove_loop_start_listener(self.lslisten[clip])
                    
        self.lslisten = {}
        
        for clip in self.lelisten:
            if clip != None:
                if clip.loop_end_has_listener(self.lelisten[clip]) == 1:
                    clip.remove_loop_end_listener(self.lelisten[clip])

        self.lelisten = {}
        
        for clip in self.cliplooplisten:
            if clip != None:
                if clip.looping_has_listener(self.cliplooplisten[clip]) == 1:
                    clip.remove_looping_listener(self.cliplooplisten[clip])
                    
        self.cliplooplisten = {}
        
        for clip in self.clipwarplisten:
            if clip != None:
                if clip.warping_has_listener(self.clipwarplisten[clip]) == 1:
                    clip.remove_warping_listener(self.clipwarplisten[clip])
                    
        self.clipwarplisten = {}
        
        
        
        for clip in self.clipwarpmodelisten:
            if clip != None:
                if clip.warp_mode_has_listener(self.clipwarpmodelisten[clip]) == 1:
                    clip.remove_warp_mode_listener(self.clipwarpmodelisten[clip])
                    
        self.clipwarpmodelisten = {}



        for clip in self.clipmutelisten:
            if clip != None:
                if clip.muted_has_listener(self.clipmutelisten[clip]) == 1:
                    clip.remove_muted_listener(self.clipmutelisten[clip])
        
        self.clipmutelisten = {}
        
        for clip in self.clipgainlisten:
            if clip != None:
                if clip.gain_has_listener(self.clipgainlisten[clip]) == 1:
                    clip.remove_gain_listener(self.clipgainlisten[clip])
                    
        self.clipgainlisten = {}
        
        for clip in self.clipcoarselisten:
            if clip != None:
                if clip.pitch_coarse_has_listener(self.clipcoarselisten[clip]) == 1:
                    clip.remove_pitch_coarse_listener(self.clipcoarselisten[clip])
                    
        self.clipcoarselisten = {}
        
        for clip in self.clipfinelisten:
            if clip != None:
                if clip.pitch_fine_has_listener(self.clipfinelisten[clip]) == 1:
                    clip.remove_pitch_fine_listener(self.clipfinelisten[clip])
        
        self.clipfinelisten = {}
        


        for clip in self.cclisten:
            if clip != None:
                if clip.color_has_listener(self.cclisten[clip]) == 1:
                    clip.remove_color_listener(self.cclisten[clip])
                
        self.cclisten = {}

        for clip in self.noteListeners:
            if clip != None:
                if clip.notes_has_listener(self.noteListeners[clip]) == 1:
                    clip.remove_notes_listener(self.oldplay_start[clip])

        self.noteListeners = {}

        for clip in self.fplisten:
            if clip != None:
                if clip.file_path_has_listener(self.fplisten[clip]) == 1:
                    clip.remove_file_path_listener(self.fplisten[clip])
        
        self.fplisten = {}





    def clip_name(self, clip, tid, cid):
        ascnm = ""
        nm = ""
        play = 0
        audioclip = 0

        if clip.name != None:
            nm = touchAbleUtils.cut_string(clip.name)
            #ascnm = (nm.encode('ascii', 'replace'))
        if clip.is_playing == 1:
            play = 1
        if clip.is_triggered == 1:
            play = 2
        if clip.is_recording == 1:
            if clip.is_playing == 1:
                play = 3
        if clip.is_audio_clip:
            audioclip = 1

        nm = touchAbleUtils.repr3(nm)
        self.oscServer.sendOSC('/clip', (tid, cid, nm, clip.color, play, int(audioclip)))


    def clip_marker(self, clip, tid, cid):
        ascnm = ""
        nm = ""
        play = 0
        start_marker_pos = clip.start_marker
        end_marker_pos = clip.end_marker
        #clip_loop_value = clip.looping
        #clip.looping = 1
        loop_start_pos = clip.loop_start
        loop_end_pos = clip.loop_end
        #clip.looping = clip_loop_value
        a_length = clip.length

        self.oscServer.sendOSC("/clip/marker", (tid, cid, nm, start_marker_pos, end_marker_pos, loop_start_pos, loop_end_pos, a_length))
    
    
    def clip_loop_status_changed(self, clip, tid, cid):
        
        try:
            is_looping = clip.looping
            self.oscServer.sendOSC("/clip/looping", (tid, cid, int(is_looping)))
        except:
            pass
        
    
    def clip_warping_status_changed(self, clip, tid, cid):

        try:
            is_looping = clip.warping
            self.oscServer.sendOSC("/clip/warping", (tid, cid,  int(is_looping)))
        except:
            pass
    
    def clip_warping_mode_changed(self, clip, tid, cid):
        try:
            warp_mode = clip.warp_mode
            self.oscServer.sendOSC("/clip/warp_mode", (tid, cid,  int(warp_mode)))
        except:
            pass


    def clip_muted_status_changed(self, clip, tid, cid):
        try:
            is_looping = clip.muted
            self.oscServer.sendOSC("/clip/muted", (tid, cid,  int(is_looping)))
        except:
            pass
    
    def clip_gain_str_changed(self, clip, tid, cid):
        try:
            gain_string = clip.gain_display_string
            self.oscServer.sendOSC("/clip/gain_str_changed", (tid, cid,  touchAbleUtils.repr3(gain_string)))
        except:
            pass

    def clip_gain_changed(self, clip, tid, cid):
        try:
            gain_val = clip.gain
            self.oscServer.sendOSC("/clip/gain_changed", (tid, cid,  gain_val))
            self.clip_gain_str_changed(clip, tid, cid)
        except:
            pass
    

    def clip_coarse_changed(self, clip, tid, cid):
        try:
            coarse_val = clip.pitch_coarse
        
            self.oscServer.sendOSC("/clip/coarse_changed", (tid, cid,  float(coarse_val)))
        except:
            pass

    def clip_fine_changed(self, clip, tid, cid):
        try:
            fine_val = clip.pitch_fine
            self.oscServer.sendOSC("/clip/fine_changed", (tid, cid,  float(fine_val)))
        except:
            pass

    
    def file_path_changed(self, clip, tid, cid):
        self.oscServer.sendOSC("/NSLOG_REPLACE", "file_path_changed")


    def clip_loopchanged(self, clip, tid, cid):
        
        if self.isCheckingLoop != 1:
            self.isCheckingLoop = 1
            self.oscServer.sendOSC('/clip/loopchanged', (tid, cid))
        else:
            self.isCheckingLoop = 0

    def slot_changestate(self, slot, tid, cid):

        ascnm = ""
        nm = ""
        # Added new clip
        if slot.clip != None:
            self.add_cliplistener(slot.clip, tid, cid)
            play = 0
            audioclip = 0
            
            if slot.clip.is_audio_clip:
                audioclip = 1
            if slot.clip.name != None:
                nm = touchAbleUtils.cut_string(slot.clip.name)
                #ascnm = (nm.encode('ascii', 'replace'))
            if slot.clip.is_playing == 1:
                play = 1
 
            if slot.clip.is_triggered == 1:
                play = 2

            if slot.clip.is_recording == 1:
                if slot.clip.is_playing == 1:
                    play = 3
                    if self.touchAble.onetap == 1:
                        if LiveUtils.getSong().clip_trigger_quantization > 0:
                            slot.clip.fire()
                        else:
                            pass
                    else:
                        pass
            
                else:
                    pass
            else:
                pass
            self.oscServer.sendOSC('/clip/playing_status', (tid, cid, play))
            self.oscServer.sendOSC('/clip', (tid, cid, touchAbleUtils.repr3(nm), slot.clip.color, play, int(audioclip)))
        
            clip = slot.clip

            is_audio_clip = int(clip.is_audio_clip)
            
            isLooping = int(clip.looping)
            is_audio_clip = int(clip.is_audio_clip)
            
            warp = 0
            if is_audio_clip == 1:
                warp = int(clip.warping)
            else:
                pass
            loop_start = clip.loop_start
            loop_end = clip.loop_end
    
            try:
                start = clip.start_marker
                end = clip.end_marker
            except:
                start = clip.loop_start
                end = clip.loop_end


            self.oscServer.sendOSC('/clip/loopstats', (tid, cid, isLooping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))
    
        else:

            self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 0))
            self.stop_changestate(slot, tid, cid)
            if slot.has_stop_button_has_listener != 1:
                cb2 = lambda :self.stop_changestate(slot, tid, cid)
                slot.add_has_stop_button_listener(cb2)
            if self.clisten.has_key(slot.clip) == 1:
                slot.clip.remove_playing_status_listener(self.clisten[slot.clip])
                
            if self.pplisten.has_key(slot.clip) == 1:
                slot.clip.remove_playing_position_listener(self.pplisten[slot.clip])

            if self.cnlisten.has_key(slot.clip) == 1:
                slot.clip.remove_name_listener(self.cnlisten[slot.clip])
            
            if self.smlisten.has_key(slot.clip) == 1:
                slot.clip.remove_start_marker_listener(self.smlisten[slot.clip])

            if self.emlisten.has_key(slot.clip) == 1:
                slot.clip.remove_end_marker_listener(self.emlisten[slot.clip])
            
            if self.lslisten.has_key(slot.clip) == 1:
                slot.clip.remove_loop_start_listener(self.lslisten[slot.clip])
                    
            if self.lelisten.has_key(slot.clip) == 1:
                slot.clip.remove_loop_end_listener(self.lelisten[slot.clip])
            
            if self.cliplooplisten.has_key(slot.clip) == 1:
                slot.clip.remove_looping_listener(self.cliplooplisten[slot.clip])
                    
            if self.clipwarplisten.has_key(slot.clip) == 1:
                slot.clip.remove_warping_listener(self.clipwarplisten[slot.clip])
            
            
            if self.clipwarpmodelisten.has_key(slot.clip) == 1:
                slot.clip.remove_warp_mode_listener(self.clipwarpmodelisten[slot.clip])
            
            
            if self.clipmutelisten.has_key(slot.clip) == 1:
                slot.clip.remove_muted_listener(self.clipmutelisten[slot.clip])
            
            if self.clipgainlisten.has_key(slot.clip) == 1:
                slot.clip.remove_gain_listener(self.clipgainlisten[slot.clip])
            
            if self.clipcoarselisten.has_key(slot.clip) == 1:
                slot.clip.remove_pitch_coarse_listener(self.clipcoarselisten[slot.clip])
        
            if self.clipfinelisten.has_key(slot.clip) == 1:
                slot.clip.remove_pitch_fine_listener(self.clipfinelisten[slot.clip])
            
            if self.fplisten.has_key(slot.clip) == 1 and slot.clip.is_audio_clip:
                slot.clip.remove_file_path_listener(self.fplisten[slot.clip])

            if self.cclisten.has_key(slot.clip) == 1:
                slot.clip.remove_color_listener(self.cclisten[slot.clip])
            
            if self.noteListeners.has_key(slot.clip) == 1:
                slot.clip.remove_notes_listener(self.noteListeners[slot.clip])
        
    
    
    def clip_changestate(self, clip, x, y):
        playing = 0
        
        if clip.is_playing == 1:
            playing = 1
            if clip.is_recording == 1:
                playing = 3
            if LiveUtils.getSong().tracks[x].arm == 1 and clip.is_audio_clip == 0:
                if LiveUtils.getSong().overdub == 1:
                    playing = 3
                else:
                    playing = 1
        else:
            pass
        if clip.is_triggered == 1:
            playing = 2
        else:
            pass
        
        self.oscServer.sendOSC('/clip/playing_status', (x, y, playing))
        #self.log("Clip changed x:" + str(x) + " y:" + str(y) + " status:" + str(playing)) 
        

    def stop_changestate(self, slot, tid, cid):
        if slot.clip != None:
            pass
        else:
            if slot.has_stop_button == 1:
                self.oscServer.sendOSC('/clip', (tid, cid, "stop", 2500134, 0, int(0), int(0)))
                self.oscServer.sendOSC('/clipslot/stop', (tid, cid))
            else:
                self.oscServer.sendOSC('/clipslot/empty', (tid, cid))


    def getslots(self):
        tracks = LiveUtils.getSong().tracks

        clipSlots = []
        for track in tracks:
            clipSlots.append(track.clip_slots)
        return clipSlots

                
