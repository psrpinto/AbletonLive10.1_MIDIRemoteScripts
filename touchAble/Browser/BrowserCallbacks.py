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

class BrowserCallbacks:
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


        self.callbackManager.add(self.trackLoad, "/browser/load/track")
        self.callbackManager.add(self.returnLoad, "/browser/load/return")
        self.callbackManager.add(self.masterLoad, "/browser/load/master")
        self.callbackManager.add(self.clipLoad, "/browser/load/clip")
        self.callbackManager.add(self.drumpadLoad, "/browser/load/drum_pad")
        self.callbackManager.add(self.drumpadAudioEffectLoad, "/browser/load/drum_pad_audio_effect")
        self.callbackManager.add(self.previewItem, "/browser/start_stop_preview_item")
        self.callbackManager.add(self.loadChildren, "/browser/load_children")        

        self.callbackManager.add(self.deviceLoad, "/browser/load/device")
        self.callbackManager.add(self.chainLoad, "/browser/load/chain")


    def deviceLoad(self, msg):
        position = msg[2]
        type = msg[3]
        tid = msg[4]
        steps = msg[5]
        #self.oscServer.sendOSC("/browser/loadstart", 1)

        track = LiveUtils.getSong().master_track
        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]

        LiveUtils.getSong().view.selected_track = track
        browser = Live.Application.get_application().browser
        
        #self.oscServer.sendOSC("/browser/loadstart", 2)


        if position == 1:
            track.view.device_insert_mode = Live.Track.DeviceInsertMode.selected_left
        elif position == 0:
            track.view.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
        elif position == -1:
            track.view.device_insert_mode = Live.Track.DeviceInsertMode.default
        #self.oscServer.sendOSC("/browser/loadstart", 3)

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

        ind = msg[6]
        #self.oscServer.sendOSC("/browser/loadstart", 4)

        if ind >= len(root_items):
            if ind == 11:
                item = list(browser.user_folders)
            if ind == 12:
                item = list(browser.colors)
            subItem = item[msg[7]]

            for i in range(steps-2):
                message = "userfolder load " + str(i)


                index = msg[8+i]
                subItem = subItem.children[index]
            
            browser.load_item(subItem)


        else:
            item = root_items[msg[6]]

            for i in range(steps-1):
            
                index = msg[7+i]
                item = item.children[index]
        
            browser.load_item(item)


    def chainLoad(self, msg):
        type = msg[2]
        tid = msg[3]
        steps = msg[4]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        
        track = LiveUtils.getSong().master_track
        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
    
        #LiveUtils.getSong().view.selected_track = track
        browser = Live.Application.get_application().browser
        
        #self.oscServer.sendOSC("/browser/loadstart", 2)
        
        track.view.device_insert_mode = Live.Track.DeviceInsertMode.default
        #self.oscServer.sendOSC("/browser/loadstart", 3)
    

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
        
        item = root_items[msg[5]]
        #self.oscServer.sendOSC("/browser/loadstart", 4)
        
        for i in range(steps-1):
            
            index = msg[6+i]
            item = item.children[index]
        
            
        #self.oscServer.sendOSC("/browser/loadstart", 5)
        
        if not Live.Application.get_application().view.browse_mode:
            Live.Application.get_application().view.toggle_browse()

        browser.load_item(item)
        
        browser.hotswap_target = None


        if Live.Application.get_application().view.browse_mode:
            Live.Application.get_application().view.toggle_browse()

        #self.oscServer.sendOSC("/browser/loadstart", 6)






    def trackLoad(self, msg):
        trk = msg[2]
        steps = msg[3]
        #self.oscServer.sendOSC("/browser/loadstart", 1)

        track = LiveUtils.getSong().tracks[trk]
        application = Live.Application.get_application()
        
        LiveUtils.getSong().view.selected_track = track
        
        #Live.Application.get_application().view.show_view("Detail/DeviceChain")

        browser = Live.Application.get_application().browser
        
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
        
        item = root_items[msg[4]]
        #self.oscServer.sendOSC("/browser/loadstart", 2)

        for i in range(steps-1):
            #self.oscServer.sendOSC("/browser/loadstart", 3)

            index = msg[5+i]
            item = item.children[index]
        #self.oscServer.sendOSC("/browser/loadstart", 3)

        #if not Live.Application.get_application().view.browse_mode:
            #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 4)

        browser.load_item(item)
        #self.oscServer.sendOSC("/browser/loadstart", 5)
                
        #if Live.Application.get_application().view.browse_mode:
            #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 6)

    def returnLoad(self, msg):
        trk = msg[2]
        steps = msg[3]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        
        track = LiveUtils.getSong().return_tracks[trk]
        application = Live.Application.get_application()
        
        LiveUtils.getSong().view.selected_track = track
        
        #Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
        browser = Live.Application.get_application().browser
        
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
        
        item = root_items[msg[4]]
        #self.oscServer.sendOSC("/browser/loadstart", 2)
        
        for i in range(steps-1):
            #self.oscServer.sendOSC("/browser/loadstart", 3)
            
            index = msg[5+i]
            item = item.children[index]
        #self.oscServer.sendOSC("/browser/loadstart", 3)
        
        #if not Live.Application.get_application().view.browse_mode:
        #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 4)
        
        browser.load_item(item)
        #self.oscServer.sendOSC("/browser/loadstart", 5)
        
        #if Live.Application.get_application().view.browse_mode:
        #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 6)

    
    def masterLoad(self, msg):
        steps = msg[2]
        self.oscServer.sendOSC("/browser/loadstart", 1)
        
        track = LiveUtils.getSong().master_track
        application = Live.Application.get_application()
        
        LiveUtils.getSong().view.selected_track = track
        
        #Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
        browser = Live.Application.get_application().browser
        
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
        
        item = root_items[msg[3]]
        #self.oscServer.sendOSC("/browser/loadstart", 2)
        
        for i in range(steps-1):
            #self.oscServer.sendOSC("/browser/loadstart", 3)
            
            index = msg[4+i]
            item = item.children[index]
        #self.oscServer.sendOSC("/browser/loadstart", 3)
        
        #if not Live.Application.get_application().view.browse_mode:
        #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 4)
        
        browser.load_item(item)
        #self.oscServer.sendOSC("/browser/loadstart", 5)
        
        #if Live.Application.get_application().view.browse_mode:
        #Live.Application.get_application().view.toggle_browse()
        self.oscServer.sendOSC("/browser/loadstart", 6)


    def drumpadLoad(self, msg):
        #self.oscServer.sendOSC("/browser/load/drumpad", 1)
        trk = msg[2]
        dev = msg[3]
        
        number_of_steps = msg[4]
        
        track = LiveUtils.getSong().tracks[trk]
        trackk = track;
        device = track.devices[dev]
        
        for i in range(number_of_steps):
            chain_id = msg[5+i*2]
            device_id = msg[6+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]

        
        pad = 127-msg[5 + number_of_steps * 2]

        steps = msg[6 + number_of_steps * 2]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        
        
        browser = Live.Application.get_application().browser


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
        
        item = root_items[msg[7 + number_of_steps * 2]]
        
        for i in range(steps-1):
            
            index = msg[8 + number_of_steps * 2 +i]
            item = item.children[index]
        
        drum_pad = device.drum_pads[pad]
                    
                

            
        LiveUtils.getSong().view.selected_track = trackk
        #LiveUtils.getSong().view.select_device(device)
        Live.Application.get_application().view.show_view("Detail/DeviceChain")
            
        if isinstance(drum_pad, Live.DrumPad.DrumPad):
            if drum_pad.chains and drum_pad.chains[0].devices:
                LiveUtils.getSong().view.select_device(drum_pad.chains[0].devices[0])
                drum_pad.canonical_parent.view.selected_chain = drum_pad.chains[0]
                browser.hotswap_target = drum_pad.chains[0]

            else:
                browser.hotswap_target = drum_pad

            
            drum_pad.canonical_parent.view.selected_drum_pad = drum_pad

            
            #self.oscServer.sendOSC("/browser/loadstart", 2)

            #browser.hotswap_target = drum_pad
                
            if not Live.Application.get_application().view.browse_mode:
                Live.Application.get_application().view.toggle_browse()

            browser.load_item(item)

            if Live.Application.get_application().view.browse_mode:
                Live.Application.get_application().view.toggle_browse()

        else:
            pass
   
        #self.oscServer.sendOSC("/browser/loadstart", 6)
    
    
    def drumpadAudioEffectLoad(self, msg):
        #self.oscServer.sendOSC("/browser/load/drumpad", 1)

        trk = msg[2]
        dev = msg[3]
        
        number_of_steps = msg[4]
        
        track = LiveUtils.getSong().tracks[trk]
        device = track.devices[dev]
        
        for i in range(number_of_steps):
            chain_id = msg[5+i*2]
            device_id = msg[6+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]
        
        pad = 127-msg[5 + number_of_steps * 2]
        
        steps = msg[6 + number_of_steps * 2]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        
        track = LiveUtils.getSong().tracks[trk]
        device = track.devices[dev]
        
        
        browser = Live.Application.get_application().browser
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
        
        item = root_items[msg[7 + number_of_steps * 2]]
        
        for i in range(steps-1):
            
            index = msg[8 + number_of_steps * 2+i]
            item = item.children[index]
        
        drum_pad = device.drum_pads[pad]
        
        
        
        
        LiveUtils.getSong().view.selected_track = track
        #LiveUtils.getSong().view.select_device(device)
        Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
        if isinstance(drum_pad, Live.DrumPad.DrumPad):
            if drum_pad.chains and drum_pad.chains[0].devices:
                LiveUtils.getSong().view.select_device(drum_pad.chains[0].devices[0])
                drum_pad.canonical_parent.view.selected_chain = drum_pad.chains[0]
                browser.hotswap_target = drum_pad.chains[0]
                #self.oscServer.sendOSC("/browser/loadstart", 2)

            else:
                browser.hotswap_target = drum_pad
                #self.oscServer.sendOSC("/browser/loadstart", 3)


            #self.oscServer.sendOSC("/browser/loadstart", 4)

            
            
            drum_pad.canonical_parent.view.selected_drum_pad = drum_pad
            
            
            #self.oscServer.sendOSC("/browser/loadstart", 5)
            
            #browser.hotswap_target = drum_pad
            
            if not Live.Application.get_application().view.browse_mode:
                Live.Application.get_application().view.toggle_browse()
                
            browser.load_item(item)

            if Live.Application.get_application().view.browse_mode:
                Live.Application.get_application().view.toggle_browse()
                
            
        
        #self.oscServer.sendOSC("/browser/loadstart", 6)

    def clipLoad(self, msg):
        trk = msg[2]
        scene = msg[3]
        steps = msg[4]
        #self.oscServer.sendOSC("/browser/loadstart", 1)

        track = LiveUtils.getSong().tracks[trk]
        ascene = LiveUtils.getSong().scenes[scene]

        clip_slot = track.clip_slots[scene]
        
        """ LiveUtils.getSong().view.highlighted_clip_slot = clip_slot """
        

        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.selected_scene = ascene
        

        Live.Application.get_application().view.show_view("Detail/Clip")
                
        #Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
        browser = Live.Application.get_application().browser
        
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


        item = root_items[msg[5]]
        
        for i in range(steps-1):
            index = msg[6+i]
            item = item.children[index]


        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.selected_scene = ascene

    
        browser.load_item(item)


    def previewItem(self,msg):

        start_stop = msg[2]
        steps = msg[3]

        browser = Live.Application.get_application().browser


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

        ind = msg[4]
        #self.oscServer.sendOSC("/browser/loadstart", 4)
        if ind >= len(root_items):
            if ind == 11:
                item = list(browser.user_folders)
            if ind == 12:
                item = list(browser.colors)
            subItem = item[msg[5]]
            for i in range(steps-2):
                index = msg[6+i]
                subItem = subItem.children[index]
            if start_stop == 1:
                browser.preview_item(subItem)
            else:
                browser.stop_preview()

        else:

            item = root_items[ind]
            for i in range(steps-1):
                index = msg[5+i]
                item = item.children[index]
            if start_stop == 1:
                browser.preview_item(item)
            else:
                browser.stop_preview()


    def loadChildren(self, msg):
        
        steps = msg[2]
        browser = Live.Application.get_application().browser
        
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
        
        ind = msg[3]
        message = "steps = " + str(steps)
        self.oscServer.sendOSC("/NSLOG_REPLACE", message)
        #message = " length root items " + str(len(root_items)) + " index "  + str(ind)
        #self.oscServer.sendOSC("/NSLOG_REPLACE", message)
        
        if ind >= len(root_items):
            indexInPlaces = ind - len(root_items)
            if ind == 11:
                item_list = list(browser.user_folders)
                item = list(browser.user_folders)
            if ind == 12:
                item_list = list(browser.colors)
                item = list(browser.colors)

            indices = [msg[3]]
            
            for i in range(steps-1):
                if i < 1:
                    index = msg[4+i]
                    message = "index = " + str(msg[4+i]) + "i = " + str(i)
                    self.oscServer.sendOSC("/NSLOG_REPLACE", message)
                    item = item[index]
                    message =  "got new item" + str(item)
                    self.oscServer.sendOSC("/NSLOG_REPLACE", message)
                    indices.append(int(index))
                else:
                    index = msg[4+i]
                    item = item.children[index]
                    indices.append(int(index))

    
            message = "steps = " + str(steps)
            self.oscServer.sendOSC("/NSLOG_REPLACE", message)
            j = 0
        
            if steps < 2:
                self.oscServer.sendOSC("/NSLOG_REPLACE", "steps < 2")

                c = len(item)
                itemIndis = [steps]
                itemIndis.append(int(c))
                for index in indices:
                    itemIndis.append(int(index))
                
                item_length = len(item)
                
                for i in range(item_length):
                    subItem = item[i]
                    count = (len(subItem.children))
                    indis = [touchAbleUtils.repr2(subItem.name), int(steps+1), int(1), int(count)]
                    for index in indices:
                        indis.append(int(index))
                    indis.append(int(j))
                    self.oscServer.sendOSC("/browser/item", tuple(indis))
                    j = j+1
            else:
                message = "steps = " + str(steps)
                self.oscServer.sendOSC("/NSLOG_REPLACE", message)

                c = len(item.children)
                itemIndis = [steps]
                itemIndis.append(int(c))
                message = "childre = " + str(len(item.children))
                self.oscServer.sendOSC("/NSLOG_REPLACE", message)
                for index in indices:
                    itemIndis.append(int(index))
                
                item_children = item.children
                
                for subItem in item_children:
                    count = len(subItem.children)
                    indis = [touchAbleUtils.repr2(subItem.name), int(steps+1), int(subItem.is_loadable), int(count)]
                    for index in indices:
                        indis.append(int(index))
                    indis.append(int(j))
                    self.oscServer.sendOSC("/browser/item", tuple(indis))
                    j = j+1
    
        
            self.oscServer.sendOSC("/browser/children_loaded", tuple(itemIndis))
        
        else:
            
            item = root_items[msg[3]]
            
            
            indices = [msg[3]]
            
            for i in range(steps-1):
                index = msg[4+i]
                item = item.children[index]
                indices.append(int(index))
            
            
            c = len(item.children)
            itemIndis = [steps]
            itemIndis.append(int(c))
            for index in indices:
                itemIndis.append(int(index))
            
            
            j = 0
            #self.oscServer.sendOSC("/bundle/start", (1))
            item_children = item.children
            
            for subItem in item_children:
                count = len(subItem.children)
                indis = [touchAbleUtils.repr2(subItem.name), int(steps+1), int(subItem.is_loadable), int(count)]
                for index in indices:
                    indis.append(int(index))
                indis.append(int(j))
                
                self.oscServer.sendOSC("/browser/item", tuple(indis))
                j = j+1
            self.oscServer.sendOSC("/browser/children_loaded", tuple(itemIndis))
        #self.oscServer.sendOSC("/bundle/end", (1))
           


