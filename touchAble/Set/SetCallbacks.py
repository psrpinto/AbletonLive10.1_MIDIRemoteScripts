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

class SetCallbacks:
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

        self.callbackManager.add(self.nudgeupCB, "/nudgeup")
        self.callbackManager.add(self.nudgedownCB, "/nudgedown")
        self.callbackManager.add(self.cuelevelCB, "/cuelevel")
        self.callbackManager.add(self.tempoCB, "/live/tempo")
        self.callbackManager.add(self.timeCB, "/live/time")
        self.callbackManager.add(self.nextCueCB, "/live/next/cue")
        self.callbackManager.add(self.prevCueCB, "/live/prev/cue")
        self.callbackManager.add(self.playCB, "/live/play")
        self.callbackManager.add(self.playContinueCB, "/live/play/continue")
        self.callbackManager.add(self.playSelectionCB, "/live/play/selection")
        self.callbackManager.add(self.quantizationCB, "/live/quantization")
        self.callbackManager.add(self.recquantizationCB, "/live/recquantization")
        self.callbackManager.add(self.quantsCB, "/quants")
        self.callbackManager.add(self.metronomeCB, "/live/metronome")
        self.callbackManager.add(self.recordCB, "/live/record")
        self.callbackManager.add(self.overdubCB, "/live/overdub")
        self.callbackManager.add(self.stopAllCB, "/live/stopall")

        self.callbackManager.add(self.undoCB, "/live/undo")
        self.callbackManager.add(self.redoCB, "/live/redo")

        self.callbackManager.add(self.stopCB, "/live/stop")
        self.callbackManager.add(self.sigCB, "/live/clip/signature")

        self.callbackManager.add(self.doneCB, "/done")

        self.callbackManager.add(self.set_current_songtime, "/set_current_songtime")
        self.callbackManager.add(self.set_current_loop_start, "/set_loop_start")
        self.callbackManager.add(self.set_current_loop_length, "/set_loop_length")
        self.callbackManager.add(self.songLoop, "/song_loop")

        self.callbackManager.add(self.setGlobalGroove, "/set/global_groove")
        self.callbackManager.add(self.setExclusiveSolo, "/exclusive_solo")
        self.callbackManager.add(self.setExclusiveArm, "/exclusive_arm")

        self.callbackManager.add(self.meterModeCB, "/metermode")
        self.callbackManager.add(self.positionsCB, "/positions")

        self.callbackManager.add(self.onetapCB, "/onetap")
        self.callbackManager.add(self.tapTempo, "/set/tap_tempo")

        self.callbackManager.add(self.session_record_chang, "/live/set/session_record")
        self.callbackManager.add(self.session_record_status_chang, "/live/set/trigger_session_record")
        self.callbackManager.add(self.re_enable_automation_enabled_chang, "/live/set/re_enable_automation")
        self.callbackManager.add(self.session_automation_record_chang, "/live/set/session_automation_record")
        self.callbackManager.add(self.sesion_capture_midi, "/live/set/capture_midi")


    def nudgeupCB(self, msg):
        onoff = msg[2]
        LiveUtils.getSong().nudge_up = onoff

    def nudgedownCB(self, msg):
        onoff = msg[2]
        LiveUtils.getSong().nudge_down = onoff

    def cuelevelCB(self, msg):
        if len(msg) == 2:
            value = LiveUtils.getSong().master_track.mixer_device.cue_volume.value
            self.oscServer.sendOSC("/set/cuelevel", float(value))
        elif len(msg) == 3:
            value = msg[2]
            LiveUtils.getSong().master_track.mixer_device.cue_volume.value = value


    def tempoCB(self, msg):
        """Called when a /live/tempo message is received.

        Messages:
        /live/tempo                 Request current tempo, replies with /live/tempo (float tempo)
        /live/tempo (float tempo)   Set the tempo, replies with /live/tempo (float tempo)
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            self.oscServer.sendOSC("/set/tempo", LiveUtils.getTempo())
        
        elif len(msg) == 3:
            tempo = msg[2]
            LiveUtils.setTempo(tempo)
        
    def timeCB(self, msg):
        """Called when a /live/time message is received.

        Messages:
        /live/time                 Request current song time, replies with /live/time (float time)
        /live/time (float time)    Set the time , replies with /live/time (float time)
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):

            self.oscServer.sendOSC("/set/playing_position", float(LiveUtils.currentTime(),float(4),float(4)))

        elif len(msg) == 3:
            time = msg[2]
            LiveUtils.currentTime(time)


    def nextCueCB(self, msg):
        """Called when a /live/next/cue message is received.

        Messages:
        /live/next/cue              Jumps to the next cue point
        """
        LiveUtils.jumpToNextCue()
        
    def prevCueCB(self, msg):
        """Called when a /live/prev/cue message is received.

        Messages:
        /live/prev/cue              Jumps to the previous cue point
        """
        LiveUtils.jumpToPrevCue()
        
    def playCB(self, msg):
        """Called when a /live/play message is received.

        Messages:
        /live/play              Starts the song playing
        """
        LiveUtils.play()
        
    def playContinueCB(self, msg):
        """Called when a /live/play/continue message is received.

        Messages:
        /live/play/continue     Continues playing the song from the current point
        """
        LiveUtils.continuePlaying()
        
    def playSelectionCB(self, msg):
        """Called when a /live/play/selection message is received.

        Messages:
        /live/play/selection    Plays the current selection
        """
        LiveUtils.playSelection()


    def quantizationCB(self, msg):
        quant = msg[2]
        LiveUtils.getSong().clip_trigger_quantization = quant

    def recquantizationCB(self, msg):
        recquant = msg[2]
        LiveUtils.getSong().midi_recording_quantization = recquant

    def quantsCB(self, msg):
        self.oscServer.sendOSC("/set/quantization", (int(LiveUtils.getSong().clip_trigger_quantization), int(LiveUtils.getSong().midi_recording_quantization)))

    def metronomeCB(self, msg):
        """Called when a /live/metronome message is received.
        
        Messages:
        /live/metronome     (int on/off)      Enables/disables metronome
        """        
        if len(msg) == 3:
            metronome = msg[2]
            LiveUtils.getSong().metronome = metronome


    def recordCB(self, msg):
        """Called when a /live/record message is received.
        
        Messages:
        /live/record     (int on/off)      Enables/disables recording
        """        
        if len(msg) == 3:
            record = msg[2]
            LiveUtils.getSong().record_mode = record


    def overdubCB(self, msg):
        """Called when a /live/overdub message is received.
        
        Messages:
        /live/overdub     (int on/off)      Enables/disables overdub
        """        
        overdub = msg[2]
        a = LiveUtils.getApp().get_major_version()
        self.oscServer.sendOSC('/overdub_status', int(a))


        if a >= 9:
            self.oscServer.sendOSC('/overdub_status', 1)
            LiveUtils.getSong().arrangement_overdub = overdub
        
        else:
            self.oscServer.sendOSC('/overdub_status', 1)
            LiveUtils.getSong().overdub = overdub
            self.oscServer.sendOSC('/overdub_status', 2)

    def stopAllCB(self, msg):
        """Called when a /live/stop/track message is received.

        Messages:
        /live/stop/track     (int track, int clip)   Stops track number track
        """
        if len(msg) == 2:
            LiveUtils.getSong().stop_all_clips()  


    def undoCB(self, msg):
        """Called when a /live/undo message is received.
        
        Messages:
        /live/undo      Requests the song to undo the last action
        """
        LiveUtils.getSong().undo()
        
    def redoCB(self, msg):
        """Called when a /live/redo message is received.
        
        Messages:
        /live/redo      Requests the song to redo the last action
        """
        LiveUtils.getSong().redo()

    def stopCB(self, msg):
        """Called when a /live/stop message is received.

        Messages:
        /live/stop              Stops playing the song
        """
        LiveUtils.stop()

    def sigCB(self, msg):
        """ Called when a /live/clip/signature message is recieved
        """
        track = msg[2]
        clip = msg[3]
        c = LiveUtils.getSong().tracks[track].clip_slots[clip].clip
        
        if len(msg) == 4:
            self.oscServer.sendOSC("/live/clip/signature", (track, clip, c.signature_numerator, c.signature_denominator))
            
        if len(msg) == 6:
            self.oscServer.sendOSC("/live/clip/signature", 1)
            c.signature_denominator = msg[5]
            c.signature_numerator = msg[4]

    def doneCB(self, msg):
        self.oscServer.sendOSC("/done", 1)


    def set_current_songtime(self,msg):

        song_time = msg[2]
        LiveUtils.getSong().current_song_time = song_time
    
    def set_current_loop_start(self,msg):
        
        song_time = msg[2]
        LiveUtils.getSong().loop_start = song_time
            
    def set_current_loop_length(self,msg):
        
        song_time = msg[2]
        LiveUtils.getSong().loop_length = song_time

    def songLoop(self,msg):
        
        song_loop = msg[2]
        LiveUtils.getSong().loop = song_loop


    def setGlobalGroove(self,msg):
    
        global_groove = msg[2]
        self.oscServer.sendOSC("/NSLOG_REPLACE", "try to groove set")

        LiveUtils.getSong().groove_amountProperty = global_groove
    
    def setExclusiveSolo(self,msg):
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "solo")

        global_groove = msg[2]
        LiveUtils.getSong().exclusive_solo = global_groove
        self.oscServer.sendOSC("/NSLOG_REPLACE", "solo set")

    def setExclusiveArm(self,msg):
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "arm")

        global_groove = msg[2]        
        LiveUtils.getSong().exclusive_arm = global_groove
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "arm set")


    def positionsCB(self, msg):
        self.positions()
        
    def meterModeCB(self, msg):

        self.metermode = msg[2]
        self.oscServer.sendOSC("/metermode", self.metermode)

    def tapTempo(self, msg):
        LiveUtils.getSong().tap_tempo()
    
    def onetapCB(self, msg):
        self.touchAble.onetap = msg[2]

    def session_record_chang(self, msg):
        
        session_record = msg[2]

        
        LiveUtils.getSong().session_record = session_record
    
    def sesion_capture_midi(self, msg):
        
        LiveUtils.getSong().capture_midi()
    
    
    def session_record_status_chang(self, msg):
        
        newActive = 0

        selected_scene = LiveUtils.getSong().view.selected_scene

        index = 0
        selected_index = 0
        for scene in LiveUtils.getSong().scenes:
            if scene == selected_scene:
                selected_index = index
            index = index + 1

        

        tracks = LiveUtils.getSong().tracks
        
        for track in tracks:
            if track.can_be_armed:
                if track.arm:
                    if track.clip_slots[selected_index].clip != None:
                        newActive = 1
                        break

        if newActive == 1:
            
            maxScenes = len(LiveUtils.getSong().scenes)
            startIndex = selected_index
            sceneIsEmpty = 0
            newSceneIndex = 0
            
            for i in range(startIndex, maxScenes):
                sceneIsEmpty = 1
                for track in tracks:
                    if track.can_be_armed:
                        if track.arm:
                            if track.clip_slots[i].clip != None:
                                sceneIsEmpty = 0

                                break
                if sceneIsEmpty == 1:
                    newSceneIndex = i
                    break
            
            if len(LiveUtils.getSong().scenes) == newSceneIndex:
                LiveUtils.getSong().create_scene()
            
            newScene = LiveUtils.getSong().scenes[newSceneIndex]
            LiveUtils.getSong().view.selected_scene = newScene

            for track in tracks:
                if track.can_be_armed:
                    if track.arm:
                        track.stop_all_clips()
                            




    def re_enable_automation_enabled_chang(self, msg):
        LiveUtils.getSong().re_enable_automation()
    
    
    def session_automation_record_chang(self, msg):
        
        session_automation_record = msg[2]
        
        LiveUtils.getSong().session_automation_record = session_automation_record
        
        


