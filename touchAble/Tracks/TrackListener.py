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


class TrackListener:
    __doc__ = "Listener class adding Simpler Listener for Live"

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





    def add_tracks_listener(self):
        self.ta_logger("add track listener",5)
        self.rem_tracks_listener()
        
        if LiveUtils.getSong().tracks_has_listener(self.tracks_change) != 1:
            LiveUtils.getSong().add_tracks_listener(self.tracks_change)
    
        if LiveUtils.getSong().visible_tracks_has_listener(self.update_state) != 1:
            LiveUtils.getSong().add_visible_tracks_listener(self.update_state)
        
        if LiveUtils.getSong().return_tracks_has_listener(self.returns_change) != 1:
            LiveUtils.getSong().add_return_tracks_listener(self.returns_change)

    def rem_tracks_listener(self):
        self.ta_logger("rem track listener",5)
        if LiveUtils.getSong().tracks_has_listener(self.tracks_change) == 1:
            LiveUtils.getSong().remove_tracks_listener(self.tracks_change)
        
        if LiveUtils.getSong().visible_tracks_has_listener(self.update_state) == 1:
            LiveUtils.getSong().remove_visible_tracks_listener(self.update_state)
        
        if LiveUtils.getSong().return_tracks_has_listener(self.returns_change) == 1:
            LiveUtils.getSong().remove_return_tracks_listener(self.returns_change)
    
    def tracks_change(self):
        self.ta_logger("tracks_change",5)
        self.update_track_listeners()
        self.ta_logger("send server refresh",5)
        self.oscServer.sendOSC("/server/refresh", (1))

    def returns_change(self):
        self.ta_logger("returns_change",5)
        self.update_return_listeners()
        self.oscServer.sendOSC("/server/refresh", (1))

    def update_track_listeners(self):
        self.ta_logger("update_track_listeners",5)
        self.touchAble.tAListener.clipListener.add_clip_listeners()
        self.touchAble.tAListener.mixerListener.add_mixer_listeners()
        self.touchAble.tAListener.mixerListener.add_xFader_listeners()
        self.touchAble.tAListener.deviceListener.add_device_listeners()

    def update_return_listeners(self):
        self.ta_logger("update_return_listeners",5)
        self.touchAble.tAListener.mixerListener.add_mixer_listeners()
        self.touchAble.tAListener.mixerListener.add_RxFader_listeners()
        self.touchAble.tAListener.deviceListener.add_device_listeners()


    def update_state(self):
        self.ta_logger("update_state",5)
        i = 0
        for track in LiveUtils.getSong().tracks:
            self.oscServer.sendOSC("/track/is_grouped", (int(i), int(track.is_grouped)))
            self.oscServer.sendOSC("/track/is_visible", (int(i), int(track.is_visible)))
            i = i+1
        self.oscServer.sendOSC("/track/update_state", (1))

