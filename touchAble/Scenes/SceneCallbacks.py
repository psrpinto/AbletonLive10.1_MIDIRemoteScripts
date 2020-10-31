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

class SceneCallbacks:
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

        self.callbackManager.add(self.playSceneCB, "/live/play/scene")  
        self.callbackManager.add(self.scenesCB, "/live/scenes")
        self.callbackManager.add(self.viewSceneCB, "/live/scene/view")
        self.callbackManager.add(self.createScene, "/scene/create")
        self.callbackManager.add(self.deleteScene, "/scene/delete")
        self.callbackManager.add(self.duplicateScene, "/scene/duplicate")
        self.callbackManager.add(self.renamesceneCB, "/renamescene")
        self.callbackManager.add(self.colorindexSceneCB, "/live/scene/color_index")


    def viewSceneCB(self, msg):
        """Called when a /live/scene/view message is received.
        
        Messages:
        /live/scene/view     (int track)      Selects a track to view
        """
        
        if len(msg) == 3:
            scene = msg[2]
            LiveUtils.getSong().view.selected_scene = LiveUtils.getSong().scenes[scene]
            
     
    def renamesceneCB(self, msg):
        sceneNumber = msg[2]
        new_name = msg[3]
        scene = LiveUtils.getScene(sceneNumber).name = new_name


    def duplicateScene(self, msg):
        scene = msg[2]
        LiveUtils.getSong().duplicate_scene(scene)
    
    def createScene(self, msg):
        scene = msg[2]
        LiveUtils.getSong().create_scene(scene)
    
    def deleteScene(self, msg):
        scene = msg[2]
        LiveUtils.getSong().delete_scene(scene)

    def colorindexSceneCB(self, msg):
    
        scene = msg[2]
        color_index = msg[3]
    
        LiveUtils.getSong().scenes[scene].color_index = color_index

    def playSceneCB(self, msg):
        """Called when a /live/play/scene message is received.

        Messages:
        /live/play/scene    (int scene)     Launches scene number scene
        """
        if len(msg) == 3:
            scene = msg[2]
            trackNumber = 0
            LiveUtils.launchScene(scene)
            #self.oscServer.sendOSC("/scene/fired", int(scene)+1)
            all_tracks = LiveUtils.getTracks()
            for track in all_tracks:
                if track.is_foldable != 1:
                    clipslot = track.clip_slots[scene]
                    if clipslot.clip == None:
                        if track.playing_slot_index != -2:
                            if track.playing_slot_index != -1:
                                if clipslot.has_stop_button == 1:
                                    self.oscServer.sendOSC('/clip/playing_status', (trackNumber, scene, 5))
                                else:
                                    pass
                            else:
                                pass
                        else:
                            pass
                    else:
                        if track.arm == 1 and clipslot.clip.is_audio_clip == 0 and LiveUtils.getSong().overdub == 1:
                            self.oscServer.sendOSC('/clip/playing_status', (trackNumber, scene, 4))
                        else:
                            self.oscServer.sendOSC('/clip/playing_status', (trackNumber, scene, 2))
                else:
                    pass
                            
                trackNumber = trackNumber +1

    def scenesCB(self, msg):
        """Called when a /live/scenes message is received.

        Messages:
        /live/scenes        no argument or 'query'  Returns the total number of scenes

        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            sceneTotal = len(LiveUtils.getScenes())
            self.oscServer.sendOSC("/scenes", (sceneTotal))
            return
                    
