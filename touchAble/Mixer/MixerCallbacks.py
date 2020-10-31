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
import IOCallbacks 

class MixerCallbacks:
    # LMH

    ioCallbacks = 0

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

        try:
            self.ioCallbacks = IOCallbacks.IOCallbacks(self.c_instance, self.oscServer, self.touchAble)
        except:
            self.error_log("touchAbleCallbacks: ioCallbacks failed")

        self.callbackManager.add(self.armTrackCB, "/arm")
        self.callbackManager.add(self.muteTrackCB, "/live/mute")
        self.callbackManager.add(self.muteTrackCB, "/live/return/mute")
        self.callbackManager.add(self.soloTrackCB, "/solo")
        self.callbackManager.add(self.soloTrackCB, "/live/return/solo")
        self.callbackManager.add(self.volumeCB, "/live/volume")
        self.callbackManager.add(self.volumeCB, "/live/return/volume")
        self.callbackManager.add(self.volumeCB, "/live/master/volume")
        self.callbackManager.add(self.panCB, "/live/master/pan")
        self.callbackManager.add(self.panCB, "/live/return/pan")
        self.callbackManager.add(self.panCB, "/live/pan")
        self.callbackManager.add(self.sendCB, "/live/send")
        self.callbackManager.add(self.sendCB, "/live/return/send")

        self.callbackManager.add(self.crossfaderCB, "/live/master/crossfader")
        self.callbackManager.add(self.monitorTrackCB, "/live/monitor")

        self.callbackManager.add(self.trackxfaderCB, "/abAssign")
        self.callbackManager.add(self.trackxfaderCB, "/return/abAssign")
        self.callbackManager.add(self.trackxfaderCB, "/live/track/crossfader")
        self.callbackManager.add(self.trackxfaderCB, "/live/return/crossfader")




    def armTrackCB(self, msg):
        """Called when a /live/arm message is received.

        Messages:
        /live/arm     (int track)   (int armed/disarmed)     Arms track number track
        """
        track = msg[2]
        
        if len(msg) == 4:
            trk = LiveUtils.getTrack(track)
            if trk.can_be_armed:
                if msg[3] == 1:
                    status = LiveUtils.getTrack(track).arm

                    if LiveUtils.getSong().exclusive_arm == 1:
                        i = 0
                        all_tracks = LiveUtils.getTracks()
                        for tr in all_tracks:
                            if tr.can_be_armed:
                                LiveUtils.disarmTrack(i)
                            else:
                                pass
                            i = i+1
                    
                    if status == 1:
                        LiveUtils.disarmTrack(track)
                    elif status == 0:
                        LiveUtils.armTrack(track)
                elif msg[3] == 2:

                    tr = LiveUtils.getTrack(track)
                    if tr.can_be_armed:
                        LiveUtils.armTrack(track)
                else:
                    LiveUtils.disarmTrack(track)
            else:
                pass
        # Return arm status
        elif len(msg) == 3:
            status = LiveUtils.getTrack(track).arm
            self.oscServer.sendOSC("/arm", (track, int(status)))     
            
    def muteTrackCB(self, msg):
        """Called when a /live/mute message is received.

        Messages:
        /live/mute     (int track)   Mutes track number track
        """
        ty = msg[0] == '/live/return/mute' and 1 or 0
        track = msg[2]
            
        if len(msg) == 4:
            if msg[3] == 1:
                if ty == 1:
                    status = LiveUtils.getSong().return_tracks[track].mute
                else:
                    status = LiveUtils.getTrack(track).mute
                if status == 1:
                    LiveUtils.unmuteTrack(track, ty)
                elif status == 0:        
                    LiveUtils.muteTrack(track, ty)
            else:
                LiveUtils.unmuteTrack(track, ty)
                
        elif len(msg) == 3:
            if ty == 1:
                status = LiveUtils.getSong().return_tracks[track].mute
                self.oscServer.sendOSC("/return/mute", (track, int(status)))
                
            else:
                status = LiveUtils.getTrack(track).mute
                self.oscServer.sendOSC("/mute", (track, int(status)))

    def soloTrackCB(self, msg):
        """Called when a /live/solo message is received.

        Messages:
        /live/solo     (int track)   Solos track number track
        """
        ty = msg[0] == '/live/return/solo' and 1 or 0
        track = msg[2]
        
        if len(msg) == 4:
            if msg[3] == 1:
                status = 0
                if ty == 1:
                    status = LiveUtils.getSong().return_tracks[track].solo
                    if LiveUtils.getSong().exclusive_solo == 1:
                        i = 0
                        for tr in LiveUtils.getSong().return_tracks:
                            LiveUtils.unsoloTrack(i, ty)
                            i = i+1
                else:
                    trk = LiveUtils.getTrack(track)
                    status = trk.solo
                    #trk.color = 12410829
                    if LiveUtils.getSong().exclusive_solo == 1:
                        i = 0
                        all_tracks = LiveUtils.getTracks()
                        for tr in all_tracks:
                            LiveUtils.unsoloTrack(i, ty)
                            
                            i = i+1
                        
                if status == 1:
                    LiveUtils.unsoloTrack(track, ty)
                elif status == 0:
                    LiveUtils.soloTrack(track, ty)
            elif msg[3] == 2:
                message = "solo track nr: " + str(track)
                
                tr = LiveUtils.getTrack(track)
                if tr.can_be_armed:
                    LiveUtils.soloTrack(track)
            else:
                LiveUtils.unsoloTrack(track, ty)
            
        elif len(msg) == 3:
            if ty == 1:
                status = LiveUtils.getSong().return_tracks[track].solo
                self.oscServer.sendOSC("/return/solo", (track, int(status)))
                
            else:
                status = LiveUtils.getTrack(track).solo
                self.oscServer.sendOSC("/solo", (track, int(status)))


    def volumeCB(self, msg):
        """Called when a /live/volume message is received.

        Messages:
        /live/volume     (int track)                            Returns the current volume of track number track as: /live/volume (int track, float volume(0.0 to 1.0))
        /live/volume     (int track, float volume(0.0 to 1.0))  Sets track number track's volume to volume
        """
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "master volume121212121212")

        if msg[0] == '/live/return/volume':
            ty = 1
        elif msg[0] == '/live/master/volume':
            ty = 1
        else:
            ty = 0
        
        if len(msg) == 1 and ty == 1:
            self.oscServer.sendOSC("/live/master/volume", LiveUtils.getSong().master_track.mixer_device.volume.value)
        
        elif len(msg) == 3 and ty == 1:
            volume = msg[2]
            LiveUtils.getSong().master_track.mixer_device.volume.value = volume
        
        elif len(msg) == 4:
            track = msg[2]
            volume = msg[3]
            
            if ty == 0:
                LiveUtils.trackVolume(track, volume)
            elif ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.volume.value = volume

        elif len(msg) == 3:
            track = msg[2]

            if ty == 1:
                self.oscServer.sendOSC("/return/volume", (track, LiveUtils.getSong().return_tracks[track].mixer_device.volume.value))
            
            else:
                self.oscServer.sendOSC("/volume", (track, LiveUtils.trackVolume(track)))


    def panCB(self, msg):
        """Called when a /live/pan message is received.

        Messages:
        /live/pan     (int track)                            Returns the pan of track number track as: /live/pan (int track, float pan(-1.0 to 1.0))
        /live/pan     (int track, float pan(-1.0 to 1.0))    Sets track number track's pan to pan

        """
        if msg[0] == '/live/return/pan':
            ty = 1
        elif msg[0] == '/live/master/pan':
            ty = 2
        else:
            ty = 0
        
        if len(msg) == 2 and ty == 2:
            self.oscServer.sendOSC("/live/master/pan", LiveUtils.getSong().master_track.mixer_device.panning.value)
        
        elif len(msg) == 3 and ty == 2:
            pan = msg[2]
            LiveUtils.getSong().master_track.mixer_device.panning.value = pan
            
        elif len(msg) == 4:
            track = msg[2]
            pan = msg[3]
            
            if ty == 0:
                LiveUtils.trackPan(track, pan)
            elif ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.panning.value = pan
            
        elif len(msg) == 3:
            track = msg[2]
            
            if ty == 1:
                self.oscServer.sendOSC("/pan", (track, LiveUtils.getSong().return_tracks[track].mixer_device.panning.value))
            
            else:
                self.oscServer.sendOSC("/pan", (track, LiveUtils.trackPan(track)))

    def sendCB(self, msg):
        """Called when a /live/send message is received.

        Messages:
        /live/send     (int track, int send)                              Returns the send level of send (send) on track number track as: /live/send (int track, int send, float level(0.0 to 1.0))
        /live/send     (int track, int send, float level(0.0 to 1.0))     Sets the send (send) of track number (track)'s level to (level)

        """
        ty = msg[0] == '/live/return/send' and 1 or 0
        track = msg[2]
        
        if len(msg) == 5:
            send = msg[3]
            level = msg[4]
            if ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.sends[send].value = level
            
            else:
                LiveUtils.trackSend(track, send, level)
        
        elif len(msg) == 4:
            send = msg[3]
            if ty == 1:
                self.oscServer.sendOSC("/live/return/send", (track, send, float(LiveUtils.getSong().return_tracks[track].mixer_device.sends[send].value)))

            else:
                self.oscServer.sendOSC("/live/send", (track, send, float(LiveUtils.trackSend(track, send))))
            
        elif len(msg) == 3:
            if ty == 1:
                sends = LiveUtils.getSong().return_tracks[track].mixer_device.sends
            else:
                sends = LiveUtils.getSong().tracks[track].mixer_device.sends
                
            so = [track]
            length_sends = len(sends)
            for i in range(length_sends):
                so.append(i)
                so.append(float(sends[i].value))
                
            if ty == 1:
                self.oscServer.sendOSC("/return/send", tuple(so))
            else:
                self.oscServer.sendOSC("/send", tuple(so))



    def crossfaderCB(self, msg):
        val = msg[2]
        LiveUtils.getSong().master_track.mixer_device.crossfader.value = val




    def monitorTrackCB(self, msg):
        """Called when a /live/monitor message is received.

        Messages:
        /live/monitor     (int track)   monitors track number track
        """
        track = msg[2]
        status = msg[3]
        if len(msg) == 4:
            LiveUtils.getTrack(track).current_monitoring_state = status
        elif len(msg) == 3:
            status = LiveUtils.getTrack(track).current_monitoring_state
            self.oscServer.sendOSC("/monitor", (track, int(status)))


    def trackxfaderCB(self, msg):
        """ Called when a /live/track/crossfader or /live/return/crossfader message is received
        """
        ty = msg[0] == '/return/abAssign' and 1 or 0
    
        if len(msg) == 3:
            track = msg[2]
        
            if ty == 1:
                assign = LiveUtils.getSong().return_tracks[track].mixer_device.crossfade_assign
                name   = LiveUtils.getSong().return_tracks[track].mixer_device.crossfade_assignments.values[assign]
            
                self.oscServer.sendOSC("/return/crossfader", (track, touchAbleUtils.repr2(assign), touchAbleUtils.repr2(name)))
            else:
                assign = LiveUtils.getSong().tracks[track].mixer_device.crossfade_assign
                name   = LiveUtils.getSong().tracks[track].mixer_device.crossfade_assignments.values[assign]
            
                self.oscServer.sendOSC("/track/crossfader", (track, touchAbleUtils.repr2(assign), touchAbleUtils.repr2(name)))

            
        elif len(msg) == 4:
            track = msg[2]
            assign = msg[3]
            
            if ty == 1:
                track = LiveUtils.getSong().return_tracks[track]
                oldVal = track.mixer_device.crossfade_assign
                if oldVal == assign:
                    track.mixer_device.crossfade_assign = 1
                else:
                    track.mixer_device.crossfade_assign = assign
            else:
                track = LiveUtils.getSong().tracks[track]
                oldVal = track.mixer_device.crossfade_assign
                if oldVal == assign:
                    track.mixer_device.crossfade_assign = 1
                else:
                    track.mixer_device.crossfade_assign = assign


