"""
# Copyright (C) 2007 Rob King (rob@re-mu.org)
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
# For questions regarding this module contact
# Rob King <rob@e-mu.org> or visit http://www.e-mu.org
# .
# Additional touchAble development:
# (c) 2014 Sigabort, Lee Huddleston, ZeroConfig; admin@sigabort.co, http://sigabort.co

This file contains all the current Live OSC callbacks. 

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


import Clips.ClipCallbacks as ClipCallbacks
import Tracks.TrackCallbacks as TrackCallbacks
import Set.SetCallbacks as SetCallbacks 
import Devices.DeviceCallbacks as DeviceCallbacks
import Scenes.SceneCallbacks as SceneCallbacks

import Browser.BrowserCallbacks as BrowserCallbacks

import Devices.WavetableCallbacks as WavetableCallbacks
import Devices.SimplerCallbacks as SimplerCallbacks
import Devices.CompressorCallbacks as CompressorCallbacks
import Devices.PluginCallbacks as PluginCallbacks
import Mixer.MixerCallbacks as MixerCallbacks

class touchAbleCallbacks:

    setCallbacks = 0
    clipCallbacks = 0
    trackCallbacks = 0
    deviceCallbacks = 0
    sceneCallbacks = 0

    browserCallbacks = 0

    simplerCallbacks = 0
    wavetableCallbacks = 0
    compressorCallbacks = 0
    pluginCallbacks = 0
    mixerCallbacks = 0

    offsetx = 0


    loading = 0
    should_check_if_load = 0
    # LMH
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
            #self._session_ring = touchAble.session_ring  # SVH Addition # Zerodebug Change
        else:
            return

        self.setCallbacks = SetCallbacks.SetCallbacks(self.c_instance, self.oscServer, self.touchAble)
        self.clipCallbacks = ClipCallbacks.ClipCallbacks(self.c_instance, self.oscServer, self.touchAble)
        self.trackCallbacks = TrackCallbacks.TrackCallbacks(self.c_instance, self.oscServer, self.touchAble)
        self.deviceCallbacks = DeviceCallbacks.DeviceCallbacks(self.c_instance, self.oscServer, self.touchAble)
        self.sceneCallbacks = SceneCallbacks.SceneCallbacks(self.c_instance, self.oscServer, self.touchAble)
        self.browserCallbacks = BrowserCallbacks.BrowserCallbacks(self.c_instance, self.oscServer, self.touchAble)

        self.simplerCallbacks = SimplerCallbacks.SimplerCallbacks(self.c_instance, self.oscServer, self.touchAble)
        self.wavetableCallbacks = WavetableCallbacks.WavetableCallbacks(self.c_instance, self.oscServer, self.touchAble)
        self.compressorCallbacks = CompressorCallbacks.CompressorCallbacks(self.c_instance, self.oscServer, self.touchAble)
        self.pluginCallbacks = PluginCallbacks.PluginCallbacks(self.c_instance, self.oscServer, self.touchAble)
        try:
            self.mixerCallbacks = MixerCallbacks.MixerCallbacks(self.c_instance, self.oscServer, self.touchAble)
        except:
            self.error_log("touchAbleCallbacks: MixerCallbacks failed")

        #self.callbackManager.add(self.deviceCB, "/live/device")
        self.callbackManager.add(self.selectionCB, "/live/selection")
        self.callbackManager.add(self.touchAble.update_all_listenersCB, "/update_listeners")
        self.callbackManager.add(self.print_string, "/print_string")
        self.callbackManager.add(self.print_app_version, "/print_app_version")
        self.callbackManager.add(self.offsetxCB, "/offsetx")
        self.callbackManager.add(self.scriptLoadCB, "/script/load")
        self.callbackManager.add(self.getVersion, "/getVersion")
        self.callbackManager.add(self.broadcast, "/broadcast")
        self.callbackManager.add(self.getStatus, "/script/ping")




    def getStatus(self, msg):  
        xx = int(self.oscServer.tcpServer.srcPort)
        c = Live.Application.get_application().get_bugfix_version()
        b = Live.Application.get_application().get_minor_version()
        a = Live.Application.get_application().get_major_version()
        
        self.oscServer.sendOSC("/script/pong", (int(self.touchAble.script_version), int(xx), int(a), int(b), int(c),int(self.touchAble.listeners_updated),int(self.touchAble.received_midi_cmd)))
        self.oscServer.sendOSC("/script/version", int(self.touchAble.script_version))

    

    def broadcast( self, msg ):

        #pass
        type = msg[2]
        if type == 3:
            w = msg[6]
            h = msg[7]
            pos_x = int(msg[8])
            pos_y = int(msg[9])
            
            self._touchAble__c_instance.set_session_highlight(pos_x, pos_y, w, h, False ) 
            #self._session_ring.set_offsets(pos_x, pos_y, wigth=w, height=h)  # SVH Addition # Zerodebug Addition 

        else:
            pass
                   
    def getVersion(self, msg):
        
        c = Live.Application.get_application().get_bugfix_version()
        b = Live.Application.get_application().get_minor_version()
        a = Live.Application.get_application().get_major_version()
        self.oscServer.sendOSC("/live/version", (int(a), int(b), int(c)))

    def offsetxCB(self, msg):
        """Called when a /offsetx message is received.

        Messages:
        /offsetx     (offset)
        """
        self.offsetx = msg[2]
        self.oscServer.sendOSC("/offsetx", self.offsetx)

    def print_app_version(self,msg):
        app_version = msg[2]
        app_m_version = msg[3]
        app_sm_version = msg[4]
        if app_version <= self.app_main_version and app_m_version <= self.app_minor_version and app_sm_version < self.app_sub_minor_version:
            self.app_main_version = app_version
            self.app_minor_version = app_m_version
            self.app_sub_minor_version = app_sm_version
        log_text = "app version : " + str(self.app_main_version) + "." + str(self.app_minor_version) + "." + str(self.app_sub_minor_version)
        self._log( log_text , True )

    def print_string(self,msg):
        string = msg[2]
        self._log( string , True )

    def update_all_listenersCB(self,msg):
        self.touchAble.update_all_listenersCB(msg)


    def selectionCB(self, msg):

        self.c_instance.set_session_highlight(msg[2], msg[3], msg[4], msg[5], 0) # Zerodebug Change
        #self._session_ring.set_offsets(msg[2], msg[3], width=msg[4], height=msg[5])  # SVH Change # Zerodebug Additon

    



    def scriptLoadCB(self, msg):
        
        load_browser = msg[2]   

        if self.loading == 0:
            self.oscServer.sendOSC("/script/load/start", 0)
            self.loading = 1
            self.should_check_if_load = 0
            try:
                try:
                    self.loadTracksStartUp(msg)
                except:
                    self.error_log("touchAbleCallbacks: loadTracksStartUp failed")
                try:
                    self.loadBrowserStartUp()
                except:
                    self.error_log("touchAbleCallbacks: loadBrowserStartUp failed")
                try:
                    self.loadScenesStartUp()
                except:                 
                    self.error_log("touchAbleCallbacks: loadScenesStartUp failed")
                self.oscServer.sendOSC("/script/load/end", 0)
            except:
                self.error_log("touchAbleCallbacks: scriptLoadCB failed loading Tracks/Browser/Scenes ")
                self.loading = 0
                self.oscServer.sendOSC("/server/refresh", (1))
                self.oscServer.sendOSC("/script/load/end", 1)
        else:
            self.should_check_if_load = 1
            self.oscServer.sendOSC("/script/load/end", 2)



    def loadTracksStartUp(self, msg):

        self.getVersion(1)

        try:
            self.loadSetStartup()
        except:
            self.error_log("touchAbleCallbacks: loadSetStartup failed")


        self.oscServer.sendOSC("/bundle/start", 1)
        self.oscServer.sendOSC("/song/loop", (int(LiveUtils.getSong().loop)))
               
        trackTotal = len(LiveUtils.getTracks())
        sceneTotal = len(LiveUtils.getScenes())
        returnsTotal = len(LiveUtils.getSong().return_tracks)
        self.oscServer.sendOSC("/set/size", (int(trackTotal), int(sceneTotal), int(returnsTotal)))

        selected_track = LiveUtils.getSong().view.selected_track
        selected_index = 0

        selected_scene = LiveUtils.getSong().view.selected_scene
        
        scene_index = 0
        selected_scene_index = 0
        all_scenes = LiveUtils.getSong().scenes
        
        for sce in all_scenes:
            if sce == selected_scene:
                selected_scene_index = scene_index
            scene_index = scene_index + 1
        
        self.oscServer.sendOSC("/set/selected_scene", int(selected_scene_index+1))


        trackNumber = 0
        ascnm = " "
        nm = " "
        grouptrack = 0
        is_midi_track = 0

        all_tracks = LiveUtils.getTracks()
        
        for track in all_tracks:
            clipNumber = 0
            if track.name != None:
                nm = touchAbleUtils.cut_string2(track.name)
                col = 0
                try:
                    col = track.color
                except:
                    pass
            if track.is_foldable == 1:
                grouptrack = 1
            else:
                grouptrack = 0
            is_midi_track = track.has_midi_input
            

            #self.touchAble._log( "track nr" + str(trackNumber), True)

            live_pointer = ""
            self.oscServer.sendOSC("/track", (trackNumber, touchAbleUtils.repr2(nm), col, grouptrack, int(is_midi_track),live_pointer))
            self.oscServer.sendOSC("/track/volume", (trackNumber, float(LiveUtils.trackVolume(trackNumber))))
            self.oscServer.sendOSC("/pan", (trackNumber, float(LiveUtils.trackPan(trackNumber))))
            self.oscServer.sendOSC("/track/mute", (trackNumber, int(track.mute)))
            self.oscServer.sendOSC("/track/solo", (trackNumber, int(track.solo)))
            self.oscServer.sendOSC("/track/crossfade_assign", (trackNumber, int(track.mixer_device.crossfade_assign)))
            self.oscServer.sendOSC("/track/is_grouped", (trackNumber, int(track.is_grouped)))
            self.oscServer.sendOSC("/track/is_visible", (trackNumber, int(track.is_visible)))

            try:
                self.sendTrackIO(trackNumber, track, "", 0)
            except:
                self.error_log("touchAbleCallbacks: sendTrackIO for track " + str(trackNumber) + "failed")

            try:
                self.sendTrackClips(trackNumber,track)
            except:
                self.error_log("touchAbleCallbacks: sendTrackClips for track " + str(trackNumber) + "failed")
            

            if track.can_be_armed == 1:
                self.oscServer.sendOSC("/track/arm", (trackNumber, int(track.arm)))
                self.oscServer.sendOSC("/track/current_monitoring_state", (trackNumber, track.current_monitoring_state))

            else:
                self.oscServer.sendOSC("/track/arm", (trackNumber, 0))
                self.oscServer.sendOSC("/track/current_monitoring_state", (trackNumber, 3))
     
            try:
                self.load_devices_for_track(track, trackNumber, 0)
            except:
                self.error_log("touchAbleCallbacks: load_devices_for_track for track " + str(trackNumber) + " failed")
            

            return_tracks_length = len(LiveUtils.getSong().return_tracks)
            for i in range(return_tracks_length):
                self.oscServer.sendOSC("/track/send", (trackNumber,i, float(LiveUtils.trackSend(trackNumber, i))))

            if track == selected_track:
                selected_index = trackNumber
                self.oscServer.sendOSC("/set/selected_track", (0, (selected_index)))

            trackNumber = trackNumber + 1
            #sleep(0.02)

        
        try:
            self.load_devices_for_track(LiveUtils.getSong().master_track, int(1), int(1))
        except:
            self.error_log("touchAbleCallbacks: load_devices_for_track for master_track failed")


        if LiveUtils.getSong().master_track == selected_track:
            self.oscServer.sendOSC("/set/selected_track", (1))
        
        try:
            self.loadReturnsStartUp(selected_track)
        except:
            self.error_log("touchAbleCallbacks: loadReturnsStartUp failed")

        self.oscServer.sendOSC("/done", (1))

        self.oscServer.sendOSC("/finish_loading", (1))
        self.oscServer.sendOSC("/bundle/end", (1))
        
        try:
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("setid 0"))
            setid = LiveUtils.getSong().get_data("setid", "")
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("setid 1"))
            
            if setid == "":
                #setid = self.my_random_string()
                setid = "no setid"
                LiveUtils.getSong().set_data("setid", setid)
                #self.oscServer.sendOSC("/NSLOG_REPLACE", ("setid 2"))
            else:
                pass

            #self.oscServer.sendOSC("/NSLOG_REPLACE", (str(setid)))

            self.oscServer.sendOSC("/setid", (str(setid)))
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("setid 3"))
        except:
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("setid -2"))
            
            setid = touchAbleUtils.my_random_string()
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("setid -3"))
            
            LiveUtils.getSong().set_data("setid", setid)
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("setid -4"))
            
            self.oscServer.sendOSC("/setid", (str(setid)))
        
        self.loading = 0
        if self.should_check_if_load == 1:

            trackTotal2 = len(LiveUtils.getTracks())
            sceneTotal2 = len(LiveUtils.getScenes())
            returnsTotal2 = len(LiveUtils.getSong().return_tracks)

            if (trackTotal != trackTotal2 or sceneTotal != sceneTotal2 or returnsTotal != returnsTotal2):
                self.touchAble.error_log("load is needed")

                self.should_check_if_load = 0
                self.tracksCB(msg)


    def sendTrackClips(self, trackNumber, track):
        clipNumber = 0

        all_clip_slots = track.clip_slots
        
        for clipSlot in all_clip_slots:
            if clipSlot.clip != None:
                play = 0
                clip = clipSlot.clip
                if clip.is_playing == 1:
                    play = 1
                elif clip.is_triggered == 1:
                    play = 2
                elif clip.is_recording == 1:
                    play = 3
                if clip.name != None:
                    nm = touchAbleUtils.cut_string2(clip.name)
                    #ascnm = nm.encode('ascii', 'replace')
                else:
                    nm = " "

                is_audio_clip = int(clip.is_audio_clip)

                self.oscServer.sendOSC("/clip", (trackNumber, clipNumber, touchAbleUtils.repr2(nm), clip.color, play,is_audio_clip))



                isLooping = int(clip.looping)
                is_audio_clip = int(clip.is_audio_clip)
                    
                warp = 0
                if is_audio_clip == 1:
                    warp = int(clip.warping)
                else:
                    pass
                
                
                loop_start = clip.loop_start
                loop_end = clip.loop_end
                    
                start = clip.loop_start
                end = clip.loop_end
                    
                self.oscServer.sendOSC('/clip/loopstats', (trackNumber, clipNumber, isLooping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))
            
            else:
                
                play = 0
                if clipSlot.has_stop_button == 1:
                    self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"stop", 2500134, play,int(0)))
                    self.oscServer.sendOSC("/clipslot/stop", (trackNumber, clipNumber))
            
                else:
                    self.oscServer.sendOSC("/clipslot/empty", (trackNumber, clipNumber))
        
            clipNumber = clipNumber + 1
            #return


    def load_devices_for_track(self, track, tid, type):


        message = "load_devices_for_track for track :" + str(tid) + " and type :" + str(type)
        self.ta_logger(message, 4)
        
        if len(track.devices) == 0:
            self.oscServer.sendOSC('/devices_empty', (int(type), int(tid)))


        did = 0
        
        number_of_steps = 0
        i = 0
        indices = []
        
        for device in track.devices:

            lis = list(indices)
            try:
                self.touchAble.tACommon.send_update_for_device(device, track, tid, did, type, len(track.devices), number_of_steps, lis, -1)
            except:
                self.error_log("touchAbleCallbacks: send_update_for_device for " + str(tid) + " failed")


            did = did+1

        self.oscServer.sendOSC('/devices_loaded', (int(type), int(tid)))


    def loadReturnsStartUp(self,selected_track):

        returnNumber = 0
        returnsTotal = len(LiveUtils.getSong().return_tracks)
        self.oscServer.sendOSC("/returns", (int(returnsTotal), 1))

        all_return_tracks = LiveUtils.getSong().return_tracks
        for retTrack in all_return_tracks:
            name = retTrack.name
            color = 0
            try:
                color = retTrack.color
            except:
                pass

            self.oscServer.sendOSC("/return", (int(returnNumber), touchAbleUtils.repr2(name), int(color)))
            self.oscServer.sendOSC("/return/pan", (returnNumber, float(retTrack.mixer_device.panning.value)))
            self.oscServer.sendOSC("/return/mute", (returnNumber, int(retTrack.mute)))
            self.oscServer.sendOSC("/return/crossfade_assign", (returnNumber, int(retTrack.mixer_device.crossfade_assign)))
            self.oscServer.sendOSC("/return/solo", (returnNumber, int(retTrack.solo)))
            self.oscServer.sendOSC("/return/volume", (returnNumber, float(retTrack.mixer_device.volume.value)))

            try:  
                self.sendTrackIO(returnNumber, retTrack, "", 2)
            except:
                self.error_log("touchAbleCallbacks: loadReturnsStartUp : sendTrackIO for returns failed")

            try:  
                self.load_devices_for_track(retTrack, int(returnNumber), int(2))
            except:
                self.error_log("touchAbleCallbacks: loadReturnsStartUp : load_devices_for_track for returns failed")

            return_tracks_length = len(LiveUtils.getSong().return_tracks)

            for i in range(return_tracks_length):
                self.oscServer.sendOSC("/return/send", (returnNumber,i, float(retTrack.mixer_device.sends[i].value)))
        
            
            if retTrack == selected_track:
                selected_index = returnNumber
                self.oscServer.sendOSC("/set/selected_track", (2, (selected_index)))
                
            returnNumber = returnNumber + 1



    def loadScenesStartUp(self):

        sceneNumber = 0
        ascnm = " "
        nm = " "
        all_scenes = LiveUtils.getScenes()
        for scene in all_scenes:
            nm = ""
            if scene.name != None:
                nm = touchAbleUtils.cut_string2(scene.name)
            if scene.color == 0:
                self.oscServer.sendOSC("/scene", (sceneNumber, touchAbleUtils.repr2(nm), 0))
            else:
                self.oscServer.sendOSC("/scene", (sceneNumber, touchAbleUtils.repr2(nm), scene.color))

            scene_color = scene.color
            
            if sceneNumber == 0:

                self.oscServer.sendOSC("/color_pallet_start", 1)
                for x in range(0, 60):
                    try:
                        scene.color_index = x
                        scene1_color = scene.color
                        self.oscServer.sendOSC("/color_pallet", (scene1_color, x - 1))
                        scene.color = scene_color
                    except:
                        self.oscServer.sendOSC("/color_pallet_done", 1)
                        pass

                self.oscServer.sendOSC("/color_pallet_done", 1)
            
            sceneNumber = sceneNumber + 1
            #time.sleep(0.02)

    def loadSetStartup(self):

        tquant = LiveUtils.getSong().clip_trigger_quantization
        rquant = LiveUtils.getSong().midi_recording_quantization
        self.oscServer.sendOSC("/set/quantization", (int(LiveUtils.getSong().clip_trigger_quantization), int(LiveUtils.getSong().midi_recording_quantization)))
        
        songtime = LiveUtils.getSong().current_song_time
        denom = LiveUtils.getSong().signature_denominator
        numer = LiveUtils.getSong().signature_numerator
        
        self.oscServer.sendOSC("/set/playing_position", (float(songtime) + 0.001, float(denom), float(numer)))
        
        overdub = LiveUtils.getSong().overdub
        self.oscServer.sendOSC("/set/overdub_status", (int(overdub) + 1))
        
        record = LiveUtils.getSong().record_mode
        self.oscServer.sendOSC("/set/recording_status", (int(record) + 1))
        
        try:
            overdub = LiveUtils.getSong().session_record
            self.oscServer.sendOSC("/live/set/session_record", (int(overdub)+1))
        
            overdub = LiveUtils.getSong().session_record_status
            self.oscServer.sendOSC("/live/set/session_record_status", (int(overdub)+1))
        
            overdub = LiveUtils.getSong().re_enable_automation_enabled
            self.oscServer.sendOSC("/live/set/re_enable_automation_enabled", (int(overdub)+1))
        
            overdub = LiveUtils.getSong().session_automation_record
            self.oscServer.sendOSC("/live/set/session_automation_record", (int(overdub)+1))
        except:
            self.oscServer.sendOSC("/live/", 8)
        
        master_color = LiveUtils.getSong().master_track.color
        self.oscServer.sendOSC("/master/color", master_color)
        
        tempo = LiveUtils.getTempo()
        self.oscServer.sendOSC("/set/tempo", (tempo))
        
        excl_arm = LiveUtils.getSong().exclusive_arm
        self.oscServer.sendOSC("/set/exclusive_arm", (int(excl_arm) + 1))
        
        excl_solo = LiveUtils.getSong().exclusive_solo
        self.oscServer.sendOSC("/set/exclusive_solo", (int(excl_solo) + 1))
        
        value = LiveUtils.getSong().master_track.mixer_device.cue_volume.value
        self.oscServer.sendOSC("/cuelevel", float(value))
        
        metronome = LiveUtils.getSong().metronome
        self.oscServer.sendOSC("/set/metronome_status", (int(metronome) + 1))
        
        play = LiveUtils.getSong().is_playing
        self.oscServer.sendOSC("/set/playing_status", (int(play) + 1))
        
        master = LiveUtils.getSong().master_track.mixer_device.volume.value
        self.oscServer.sendOSC("/master/volume", (float(master)))
        
        crossfader = LiveUtils.getSong().master_track.mixer_device.crossfader.value
        self.oscServer.sendOSC("/master/crossfader", float(crossfader))

    def sendTrackIO(self, trackNumber, track, type = "", track_type = 0):
        #for current_type in ("available_input_routing_channels", "available_input_routing_types", "available_output_routing_channels", "available_output_routing_types", "input_routing_channel", "input_routing_type", "output_routing_channel", "output_routing_type"):


        input_routing_type_number = 0
        input_routing_channel_number = 0
        output_routing_type_number = 0
        output_routing_channel_number = 0
        name = touchAbleUtils.repr2(track.name)
        if type == "":
            io_data = [track_type, trackNumber, name, type]
        
        
        if type == "input_routing_type" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            track_input_route_type = track.input_routing_type
            track_input_route_type_name = track_input_route_type.display_name
            io_data.append(touchAbleUtils.repr2(track_input_route_type_name))
            found_port = 0
            
            types = track.available_input_routing_types
            length = len(types)
            input_type = track.input_routing_type
            
            for i in range(length):
                rout_type = types[i]
                if rout_type == input_type:
                    input_routing_type_number = i
                    io_data.append(input_routing_type_number)
                    found_port = 1
                    break
            if found_port == 0:
                io_data.append(0)
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)
                    
                    
        
        if type == "input_routing_channel" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            track_input_routing_channel = track.input_routing_channel
            track_input_routing_channel_name = track_input_routing_channel.display_name
            io_data.append(touchAbleUtils.repr2(track_input_routing_channel_name))
            found_port = 0
            
            
            channels = track.available_input_routing_channels
            length = len(channels)
            input_channel = track.input_routing_channel
            
            for i in range(length):
                rout_type = channels[i]
                if rout_type == input_channel:
                    input_routing_channel_number = i
                    io_data.append(input_routing_channel_number)
                    found_port = 1
                    break
            if found_port == 0:
                io_data.append(0)
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)



        if type == "output_routing_type" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            track_output_route_type = track.output_routing_type
            track_output_route_type_name = track_output_route_type.display_name
            io_data.append(touchAbleUtils.repr2(track_output_route_type_name))
            found_port = 0
            
            
            types = track.available_output_routing_types
            length = len(types)
            output_type = track.output_routing_type
            
            
            for i in range(length):
                rout_type = types[i]
                if rout_type == output_type:
                    output_routing_type_number = i
                    io_data.append(output_routing_type_number)
                    found_port = 1
                    break
            if found_port == 0:
                io_data.append(0)
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)

        
        if type == "output_routing_channel" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            track_output_routing_channel = track.output_routing_channel
            track_output_routing_channel_name = track_output_routing_channel.display_name
            io_data.append(touchAbleUtils.repr2(track_output_routing_channel_name))
            found_port = 0
            
            channels = track.available_output_routing_channels
            length = len(channels)
            output_channel = track.output_routing_channel
            
            for i in range(length):
                rout_type = channels[i]
                if rout_type == output_channel:
                    output_routing_channel_number = i
                    io_data.append(output_routing_channel_number)
                    found_port = 1
                    break
            if found_port == 0:
                io_data.append(0)
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)




        if type == "available_input_routing_channels" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            channels = track.available_input_routing_channels
            length = len(channels)
            io_data.append(length)
            for i in range(length):
                rout_type = channels[i]
                route_name = rout_type.display_name
                io_data.append(touchAbleUtils.repr2(route_name))
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)
        
        

        if type == "available_input_routing_types" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            
            types = track.available_input_routing_types
            length = len(types)
            io_data.append(length)
            for i in range(length):
                rout_type = types[i]
                route_name = rout_type.display_name
                io_data.append(touchAbleUtils.repr2(route_name))
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)



        if type == "available_output_routing_channels" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            channels = track.available_output_routing_channels
            length = len(channels)
            io_data.append(length)
            for i in range(length):
                rout_type = channels[i]
                route_name = rout_type.display_name
                io_data.append(touchAbleUtils.repr2(route_name))
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)
        
        
        
        
        if type == "available_output_routing_types" or type == "":
            if type != "":
                io_data = [track_type, trackNumber, name, type]
            types = track.available_output_routing_types
            length = len(types)
            io_data.append(length)
            for i in range(length):
                rout_type = types[i]
                route_name = rout_type.display_name
                io_data.append(touchAbleUtils.repr2(route_name))
            if type != "":
                self.oscServer.sendOSC("/track/io", io_data)




        if type == "":
            self.oscServer.sendOSC("/track/io", io_data)
       

    def loadBrowserStartUp(self):

        a_version = Live.Application.get_application().get_major_version()
        load_browser = 1
        
        if load_browser == 1:
            self.oscServer.sendOSC("/browser/load_browser_1", 1)
            if a_version >= 9:
                self.oscServer.sendOSC("/browser/live_9", 1)

                try:
                    self.oscServer.sendOSC("/browser/starting", 1)
                    self.getBrowserItems()
                except:
                    self.oscServer.sendOSC("/browser/except", 1)
                    self.error_log("touchAbleCallbacks: getBrowserItems failed")
                    pass
            else:
                self.oscServer.sendOSC("/browser/live_not_9", 1)
        else:
            self.oscServer.sendOSC("/browser/load_browser_0", 1)

        self.oscServer.sendOSC("/track/update_state", (1))
        self.oscServer.sendOSC("/browser/end", 1) 

    def getBrowserItems(self):
        self.oscServer.sendOSC("/browser/getting_browser", 1)

        browser = Live.Application.get_application().browser
        self.oscServer.sendOSC("/browser/got_browser", 1)

        dir(browser)
        
        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)
        
        self.oscServer.sendOSC("/browser/got_root_items", 1)


        steps = 1
        i = 0

        self.oscServer.sendOSC("/browser/start", 1)

    
        for item in root_items:
    

            is_folder = 1
            
            count = len(item.children)

            indis = [touchAbleUtils.repr2(item.name), int(steps), int(item.is_loadable), int(count)]
            indis.append(int(i))
            
            self.oscServer.sendOSC("/browser/item", tuple(indis))
            i = i+1


        obj = list(browser.user_folders)
        count = len(obj)
        indis = ["User folder", int(steps), int(0), int(count)]
        indis.append(int(i))
        self.oscServer.sendOSC("/browser/item", tuple(indis))
        
        
        i = i+1
        a_version = Live.Application.get_application().get_major_version()
        
        if a_version >= 10:
            obj = list(browser.colors)
            count = len(obj)
            indis = ["Collections", int(steps), int(0), int(count)]
            indis.append(int(i))

        self.oscServer.sendOSC("/browser/item", tuple(indis))

        self.ta_logger("touchAbleCallbacks: getBrowserItems succeeded",5)

    

            
