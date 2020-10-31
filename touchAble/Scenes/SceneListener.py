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

class SceneListener:
    __doc__ = "Listener class adding Simpler Listener for Live"


    sclisten = {}
    snlisten = {}
    stlisten = {}

    scene = 0
    


    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
            self.log_message = touchAble.log_message
            self.error_log = touchAble.error_log
            self.ta_logger = touchAble.ta_logger
            self.error_logger = touchAble.error_logger
        else:
            return


    def add_scenes_listener(self):
        self.rem_scenes_listener()
        if LiveUtils.getSong().scenes_has_listener(self.scenes_change) != 1:
            LiveUtils.getSong().add_scenes_listener(self.scenes_change)


    def scenes_change(self):
        self.update_scene_listeners()
        self.oscServer.sendOSC("/server/refresh", (1))

    
    def rem_scenes_listener(self):
        if LiveUtils.getSong().scenes_has_listener(self.scenes_change) == 1:
            LiveUtils.getSong().remove_scenes_listener(self.scenes_change)

            



    def add_scenes_listeners(self):
        self.rem_scenes_listeners()
        scenes = LiveUtils.getSong().scenes
        for sc in range (len(scenes)):
            scene = scenes[sc]
            self.add_scenelistener(scene, sc)

    def rem_scenes_listeners(self):
        for scene in self.sclisten:
            if scene != None:
                if scene.color_has_listener(self.sclisten[scene]) == 1:
                    scene.remove_color_listener(self.sclisten[scene])
            else:
                pass
        self.sclisten = {}

        for scene in self.snlisten:
            if scene != None:
                if scene.name_has_listener(self.snlisten[scene]) == 1:
                    scene.remove_name_listener(self.snlisten[scene])
            else:
                pass
        self.snlisten = {}
        
        for scene in self.stlisten:
            if scene != None:
                if scene.is_triggered_has_listener(self.stlisten[scene]) == 1:
                    scene.remove_is_triggered_listener(self.stlisten[scene])
            else:
                pass
        self.stlisten = {}
            

    def add_scenelistener(self, scene, sc):
        cb = lambda :self.scene_color_changestate(scene, sc)
        if self.sclisten.has_key(scene) != 1:
            scene.add_color_listener(cb)
            self.sclisten[scene] = cb
        else:
            pass
            
        cb2 = lambda :self.scene_name_changestate(scene, sc)
        if self.snlisten.has_key(scene) != 1:
            scene.add_name_listener(cb2)
            self.snlisten[scene] = cb2
        else:
            pass
                
        cb3 = lambda :self.scene_triggered(scene, sc)
        if self.stlisten.has_key(scene) != 1:
            scene.add_is_triggered_listener(cb3)
            self.stlisten[scene] = cb3
        else:
            pass
        

    def scene_color_changestate(self, scene, sc):
        nm = ""
        nm = scene.name
        if scene.color == 0:
            self.oscServer.sendOSC("/scene", (sc, touchAbleUtils.repr3(nm), 0))
        else:
            self.oscServer.sendOSC("/scene", (sc, touchAbleUtils.repr3(nm), scene.color))

    def scene_name_changestate(self, scene, sc):
        nm = ""
        nm = scene.name
        if scene.color == 0:
            self.oscServer.sendOSC("/scene", (sc, touchAbleUtils.repr3(nm), 0))
        else:
            self.oscServer.sendOSC("/scene", (sc, touchAbleUtils.repr3(nm), scene.color))

    def scene_triggered(self, scene, sc):
        
        self.oscServer.sendOSC("/scene/fired", int(sc+1))

    def scene_change(self):
        selected_scene = LiveUtils.getSong().view.selected_scene
        scenes = LiveUtils.getSong().scenes
        index = 0
        selected_index = 0
        for scene in scenes:
            index = index + 1        
            if scene == selected_scene:
                selected_index = index
                
        if selected_index != self.scene:
            self.scene = selected_index
            self.oscServer.sendOSC("/set/selected_scene", (selected_index))

    def rem_scene_listeners(self):
        try:
            if LiveUtils.getSong().view.selected_scene_has_listener(self.scene_change) == 1:
                LiveUtils.getSong().view.remove_selected_scene_listener(self.scene_change)
        except:
            self.error_log("SceneListener: remove_selected_scene_listener failed")

        try:
            if LiveUtils.getSong().view.selected_track_has_listener(self.track_change) == 1:
                LiveUtils.getSong().view.remove_selected_track_listener(self.track_change)
        except:
            self.error_log("SceneListener: remove_selected_track_listener failed")



    def add_scene_listeners(self):
        try:
            self.rem_scene_listeners()
        except:
            self.error_log("SceneListener: rem_scene_listeners failed")
            

        if LiveUtils.getSong().view.selected_scene_has_listener(self.scene_change) != 1:
            LiveUtils.getSong().view.add_selected_scene_listener(self.scene_change)

        if LiveUtils.getSong().view.selected_track_has_listener(self.track_change) != 1:
            LiveUtils.getSong().view.add_selected_track_listener(self.track_change)


    def update_scene_listeners(self):
        self.add_scenes_listeners()
        self.add_scenes_listener()
        self.touchAble.tAListener.clipListener.add_clip_listeners()


    def track_change(self):
        selected_track = LiveUtils.getSong().view.selected_track
        tracks = LiveUtils.getSong().tracks
        returns = LiveUtils.getSong().return_tracks

        index = 0
        selected_index = 0
        for track in tracks:
            if track == selected_track:
                selected_index = index
                self.oscServer.sendOSC("/set/selected_track", (0, (selected_index)))
            index = index + 1


        
        index = 0
        for ret in returns:
            if ret == selected_track:
                selected_index = index
                self.oscServer.sendOSC("/set/selected_track", (2, (selected_index)))
            index = index + 1


        if selected_track == LiveUtils.getSong().master_track:
            self.oscServer.sendOSC("/set/selected_track", 1)
    

