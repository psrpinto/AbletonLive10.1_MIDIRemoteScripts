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
import Utils.touchAbleUtils as touchAbleUtils
import struct
import Live
import Utils.LiveUtils as LiveUtils
import time
import unicodedata
import thread
from threading import Timer
from collections import defaultdict
from Utils.Logger import Logger as Logger
from time import sleep


import Clips.ClipListener as ClipListener
import Devices.DeviceListener as DeviceListener 
import Devices.CompressorListener as CompressorListener
import Devices.PluginListener as PluginListener
import Devices.SimplerListener as SimplerListener
import Devices.WavetableListener as WavetableListener
import Mixer.MixerListener as MixerListener 
import Scenes.SceneListener as SceneListener
import Tracks.TrackListener as TrackListener
import Set.SetListener as SetListener

from time import sleep

class touchAbleListener:
    # LMH

    clipListener = 0
    deviceListener = 0
    pluginListener = 0
    simplerListener = 0
    wavetableListener = 0
    mixerListener = 0
    sceneListener = 0
    trackListener = 0
    setListener = 0

    def __init__(self, c_instance, oscServer, touchAble):

        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
            self.tA_log = touchAble.tA_log
            self.error_log = touchAble.error_log
            self.ta_logger = touchAble.ta_logger
            self.error_logger = touchAble.error_logger

        else:
            return

        self.clipListener = ClipListener.ClipListener(self.c_instance, self.oscServer, self.touchAble)
        self.deviceListener = DeviceListener.DeviceListener(self.c_instance, self.oscServer, self.touchAble)
        self.compressorListener = CompressorListener.CompressorListener(self.c_instance, self.oscServer, self.touchAble)
        self.pluginListener = PluginListener.PluginListener(self.c_instance, self.oscServer, self.touchAble)
        self.simplerListener = SimplerListener.SimplerListener(self.c_instance, self.oscServer, self.touchAble)
        self.wavetableListener = WavetableListener.WavetableListener(self.c_instance, self.oscServer, self.touchAble)
        self.mixerListener = MixerListener.MixerListener(self.c_instance, self.oscServer, self.touchAble)
        self.sceneListener = SceneListener.SceneListener(self.c_instance, self.oscServer, self.touchAble)
        self.trackListener = TrackListener.TrackListener(self.c_instance, self.oscServer, self.touchAble)
        self.setListener = SetListener.SetListener(self.c_instance, self.oscServer, self.touchAble)


    def update_all_listeners(self):

        self.tA_log("update all listener")
        self.add_set_listeners()
        self.add_clip_listeners()
        self.add_mixer_listeners()
        self.add_scene_listeners()
        self.add_tracks_listener()
        self.add_device_listeners()
        self.oscServer.sendOSC("/server/refresh", (1))
        self.tA_log("touchAbleListener: update_all_listeners finished successful")

    def add_tracks_listener(self):        
        try:
            self.tA_log("touchAbleListener: trackListener start")
            self.trackListener.add_tracks_listener()
            self.tA_log("touchAbleListener: trackListener finished")
        except:
            self.error_log("touchAbleListener: add_tracks_listener failed")

    def add_device_listeners(self):        
        try:
            self.deviceListener.add_device_listeners()
        except:
            self.error_log("touchAbleListener: add_device_listeners failed")

    def add_scene_listeners(self):
        try:
            self.sceneListener.add_scene_listeners()
        except:
            self.error_log("touchAbleListener: add_scene_listeners failed")
        try:
            self.sceneListener.add_scenes_listeners()
        except:
            self.error_log("touchAbleListener: add_scenes_listeners failed")
        try:
            self.sceneListener.add_scenes_listener()
        except:
            self.error_log("touchAbleListener: add_scenes_listeners failed")


    def add_clip_listeners(self):
        try:
            self.clipListener.add_clip_listeners()
        except:
            self.error_log("touchAbleListener: add_clip_listeners failed")
        

    def add_mixer_listeners(self):
        try:
            self.mixerListener.add_mixer_listeners()
        except:
            self.error_log("touchAbleListener: add_mixer_listeners failed")
        try:
            self.mixerListener.add_xFader_listeners()
        except:
            self.error_log("touchAbleListener: add_xFader_listeners failed")
        try:
            self.mixerListener.add_RxFader_listeners()
        except:
            self.error_log("touchAbleListener: add_RxFader_listeners failed")
        
        
        

    def add_set_listeners(self):
        try:
            self.setListener.add_set_listeners()
        except:
            self.error_log("touchAbleListener: add_set_listeners failed")
        

    def remove_all_listeners(self):
        try:
            self.rem_set_listeners()
            self.rem_clip_listeners()
            self.rem_mixer_listeners()
            self.rem_scene_listeners()
            self.rem_tracks_listener()
            self.rem_device_listeners()

        except:
            self.error_log("touchAbleListener: remove_all_listeners failed")
            self.oscServer.sendOSC('/remix/oscserver/shutdown', 1)
            self.oscServer.shutdown()


    def rem_tracks_listener(self):
        try:
            self.trackListener.rem_tracks_listener()
        except:
            self.error_log("touchAbleListener: rem_tracks_listener failed")

    def rem_device_listeners(self):
        try:
            self.deviceListener.rem_all_device_listeners()
        except:
            self.error_log("touchAbleListener: rem_all_device_listeners failed")

    def rem_scene_listeners(self):
        try:
            self.sceneListener.rem_scene_listeners()
        except:
            self.error_log("touchAbleListener: rem_scene_listeners failed")
        try:
            self.sceneListener.rem_scenes_listeners()
        except:
            self.error_log("touchAbleListener: rem_scenes_listeners failed")
        try:
            self.sceneListener.rem_scenes_listener()
        except:
            self.error_log("touchAbleListener: rem_scenes_listeners failed")

    def rem_clip_listeners(self):
        try:
            self.clipListener.rem_clip_listeners()
        except:
            self.error_log("touchAbleListener: rem_clip_listeners failed")
            
    def rem_mixer_listeners(self):
        try:
            self.mixerListener.rem_mixer_listeners()
        except:
            self.error_log("touchAbleListener: rem_mixer_listeners failed")
        try:
            self.mixerListener.rem_RxFader_listeners()
        except:
            self.error_log("touchAbleListener: rem_RxFader_listeners failed")
        try:
            self.mixerListener.rem_xFader_listeners()
        except:
            self.error_log("touchAbleListener: rem_xFader_listeners failed")


    def rem_set_listeners(self):
        try:
            self.setListener.rem_set_listeners()        
        except:
            self.error_log("touchAbleListener: rem_set_listeners failed")

