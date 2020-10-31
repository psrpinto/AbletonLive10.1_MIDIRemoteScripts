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

class TrackCallbacks:
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


        self.callbackManager.add(self.mviewTrackCB, "/live/master/view")
        self.callbackManager.add(self.viewTrackCB, "/live/return/view")
        self.callbackManager.add(self.viewTrackCB, "/live/track/view")
        self.callbackManager.add(self.focusChain, "/live/track/chain/view")
        self.callbackManager.add(self.renametrackCB, "/renametrack")
        self.callbackManager.add(self.stopTrackCB, "/live/stop/track")
        self.callbackManager.add(self.duplicateTrack, "/track/duplicate")
        self.callbackManager.add(self.trackJump, "/live/track/jump")

        self.callbackManager.add(self.colorindexTrackCB, "/live/track/color_index")
        self.callbackManager.add(self.foldTrackCB, "/foldTrack")

        self.callbackManager.add(self.deleteTrack, "/track/delete")
        self.callbackManager.add(self.deleteReturn, "/return/delete")
        self.callbackManager.add(self.createMidiTrack, "/track/create_midi")
        self.callbackManager.add(self.createAudioTrack, "/track/create_audio")
        self.callbackManager.add(self.createReturnTrack, "/track/create_return")



    def viewTrackCB(self, msg):
        """Called when a /live/track/view message is received.
        
        Messages:
        /live/track/view     (int track)      Selects a track to view
        """
        ty = msg[0] == '/live/return/view' and 1 or 0
        track_num = msg[2]
        
        if len(msg) == 3:
            if ty == 1:
                track = LiveUtils.getSong().return_tracks[track_num]
            else:
                track = LiveUtils.getSong().tracks[track_num]
                
            LiveUtils.getSong().view.selected_track = track
            Live.Application.get_application().view.show_view("Detail/DeviceChain")
                
            #track.view.select_instrument()
            
    def mviewTrackCB(self, msg):
        """Called when a /live/master/view message is received.
        
        Messages:
        /live/track/view     (int track)      Selects a track to view
        """
        track = LiveUtils.getSong().master_track

        LiveUtils.getSong().view.selected_track = track
        Live.Application.get_application().view.show_view("Detail/DeviceChain")   





    def focusChain(self, msg):
        self.oscServer.sendOSC('/focus_chain', 1)
        
        type = msg[2]
        track_id = int(msg[3])
        device_id = int(msg[4])
        number_of_steps = msg[5]
        
        
        if type == 1:
            self.oscServer.sendOSC('/focus_normal_track', ((track_id)))
            
            track = LiveUtils.getSong().tracks[track_id]
        elif type == 3:
            self.oscServer.sendOSC('/focus_return_track', ((track_id)))
            
            track = LiveUtils.getSong().return_tracks[track_id]
        else:
            self.oscServer.sendOSC('/focus_master_track', (int(type)))
            
            track = LiveUtils.getSong().master_track
        
        device = track.devices[device_id]
        
        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            chain = device.chains[chain_id]
            device = chain.devices[device_id]
        
        self.oscServer.sendOSC('/focus_chain', 2)

        chain_id = msg[6+number_of_steps*2]
        
        chain = device.chains[chain_id]
        self.oscServer.sendOSC('/focus_chain', chain_id)

        Live.Application.get_application().view.show_view("Detail/DeviceChain")
        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.select_device(device)
        browser = Live.Application.get_application().browser
        device.view.selected_chain = chain

        browser.hotswap_target = chain
        

        self.oscServer.sendOSC('/focus_chain', 4)




    def renametrackCB(self, msg):
        trackNumber = msg[2]
        new_name = msg[3]
        track = LiveUtils.getTrack(trackNumber).name = new_name





    def stopTrackCB(self, msg):
        """Called when a /live/stop/track message is received.

        Messages:
        /live/stop/track     (int track, int clip)   Stops track number track
        """
        
        i = msg[2]
        LiveUtils.stopTrack(i)
        track = LiveUtils.getTrack(i)
        if track.playing_slot_index != -2:
            if track.playing_slot_index != -1: 
                self.oscServer.sendOSC('/track/stop', (1, i))
            else:
                pass
        else:
            pass

    def duplicateTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().duplicate_track(track)


    def createMidiTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().create_midi_track(track)
    
    
    def createAudioTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().create_audio_track(track)
    
    
    def createReturnTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().create_return_track()

    
    def deleteTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().delete_track(track)
    
    def deleteReturn(self, msg):
        track = msg[2]
        LiveUtils.getSong().delete_return_track(track)

    def colorindexTrackCB(self, msg):
    
        track = msg[3]
        color_index = msg[4]
    
        LiveUtils.getSong().tracks[track].color_index = color_index

    def foldTrackCB(self, msg):
        tr = msg[2]
        
        track = LiveUtils.getTrack(tr)
        if track.is_foldable == 1:
            if track.fold_state == 0:
                track.fold_state = 1
            else:
                track.fold_state = 0
        else:
            pass    


    def trackJump(self, msg):
        """Called when a /live/track/jump message is received.

        Messages:
        /live/track/jump     (int track, float beats)   Jumps in track's currently running session clip by beats
        """
        if len(msg) == 4:
            track = msg[2]
            beats = msg[3]
            track = LiveUtils.getTrack(track)
            track.jump_in_running_session_clip(beats)

