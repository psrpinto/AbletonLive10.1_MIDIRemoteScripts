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
The example plug-in will consist of 10 mixer channels. Each channel will contain: volume, pan, sends, send_update_for_devicesolo, mute, track name, record arm, automation state.

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

class DeviceCallbacks:
    # LMH
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
            self.simplerListener = self.touchAble.tAListener.simplerListener

        else:
            return



        self.callbackManager.add(self.change_device_parameter, "/change_device_parameter")

        self.callbackManager.add(self.focusDevice, "/live/track/device/view")
        self.callbackManager.add(self.focusDevice, "/live/return/device/view")
        self.callbackManager.add(self.focusDevice, "/live/master/device/view")

        self.callbackManager.add(self.drumpadMute, "/drumpad/mute")
        self.callbackManager.add(self.drumpadSolo, "/drumpad/solo")

        self.callbackManager.add(self.deviceSelect, "/live/deviceselect")
        self.callbackManager.add(self.deleteDevice, "/device/delete")
        self.callbackManager.add(self.expand_deviceCB, "/expand_device")
        self.callbackManager.add(self.simpler_meta, "/simpler_meta")

        self.callbackManager.add(self.deleteReturnDevice, "/return_device/delete")
        self.callbackManager.add(self.deleteMasterDevice, "/master_device/delete")
        self.callbackManager.add(self.move_device, "/move_device")

    def send_values_for_device(self, device, track, tid, did, type, number_of_steps, indices):
        
        
        nm = touchAbleUtils.repr2(device.name)
        params = device.parameters
        onoff = params[0].value
        num = len(track.devices)
        numParams = len(params)
        cnam = touchAbleUtils.repr2(device.class_name)
        
        
        tr = tid
        dev = did
        
        name = track.name
        devicename = device.name
        
        po = [type]
        po.append(int(tr))
        po.append(int(dev))
        
        
        is_selected = 0
        
        if device == LiveUtils.getSong().appointed_device:
            is_selected = 1
        
        
        po2 = [type]
        po2.append(int(tr))
        po2.append(int(dev))
        po2.append(touchAbleUtils.repr2(name))
        po2.append(touchAbleUtils.repr2(devicename))
        
        po2.append(int(is_selected))
        
        po.append(int(number_of_steps))
        po2.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            po.append(int(indices[index]))
            po2.append(int(indices[index]))
        

        for j in range(len(params)):
            po.append(params[j].min)
            po.append(params[j].max)
            po.append(params[j].is_quantized+1)
            po2.append(float(params[j].value))
            po2.append(touchAbleUtils.repr2(params[j].name))
            po2.append(touchAbleUtils.repr2(params[j].__str__()))


        self.oscServer.sendOSC("/device/range", tuple(po))
        self.oscServer.sendOSC("/master/device/parameters", tuple(po2))







    def change_device_parameter(self, msg):
        
        type = msg[2]
        tid = msg[3]
        did = msg[4]
        pid = msg[5]
        value = msg[6]
        
        number_of_steps = msg[7]

        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track
        
        device = track.devices[did]
        indices = []

        for i in range(number_of_steps):
            chain_id = msg[8+i*2]
            device_id = msg[9+i*2]
            
            chain = device.chains[chain_id]
            indices.append(int(chain_id))
            
            device = chain.devices[device_id]
            indices.append(int(device_id))


        if device.parameters[pid].is_enabled:
            device.parameters[pid].value = float(value)
        else:
            pass
            


    def focusDevice(self, msg):

        type = msg[2]
        track_id = msg[3]
        device_id = msg[4]
        number_of_steps = msg[5]


        if type == 1:

            track = LiveUtils.getSong().tracks[track_id]
        elif type == 3:

            track = LiveUtils.getSong().return_tracks[track_id]
        else:

            track = LiveUtils.getSong().master_track
        
        device = track.devices[device_id]

        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            chain = device.chains[chain_id]
            device = chain.devices[device_id]


        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.select_device(device)
        Live.Application.get_application().view.show_view("Detail/DeviceChain")


    def drumpadMute(self, msg):
    
        type = msg[2]
        track_id = msg[3]
        device_id = msg[4]
        number_of_steps = msg[5]
        drum_id =  msg[6]
        muted =  msg[7]

        if type == 1:
            
            track = LiveUtils.getSong().tracks[track_id]
        elif type == 3:
            
            track = LiveUtils.getSong().return_tracks[track_id]
        else:
            
            track = LiveUtils.getSong().master_track
        
        device = track.devices[device_id]
        
        for i in range(number_of_steps):
            chain_id = msg[8+i*2]
            device_id = msg[9+i*2]
            
            chain = device.chains[chain_id]
            device = chain.devices[device_id]

        if device.can_have_drum_pads == 1:
            drum_pad = device.drum_pads[drum_id]
            drum_pad.mute = muted

    def drumpadSolo(self, msg):
    
        type = msg[2]
        track_id = msg[3]
        device_id = msg[4]
        number_of_steps = msg[5]
        drum_id =  msg[6]
        solod =  msg[7]
        
        if type == 1:
            
            track = LiveUtils.getSong().tracks[track_id]
        elif type == 3:
        
            track = LiveUtils.getSong().return_tracks[track_id]
        else:
            
            track = LiveUtils.getSong().master_track

        device = track.devices[device_id]
    
        for i in range(number_of_steps):
            chain_id = msg[8+i*2]
            device_id = msg[9+i*2]
            
            chain = device.chains[chain_id]
            device = chain.devices[device_id]
        
        if device.can_have_drum_pads == 1:
            drum_pad = device.drum_pads[drum_id]
            drum_pad.solo = solod



    def deviceSelect(self, msg):
        fxview = msg[2]
        track = msg[3]
        device = msg[4]
        params = 0
        if track == 1000:
            params = LiveUtils.getSong().master_track.devices[device].parameters
        elif track >= 2000:
            params = LiveUtils.getSong().return_tracks[int(track/1000)-2].devices[device].parameters

        else:
            params = LiveUtils.getSong().tracks[track].devices[device].parameters
            
        block = [fxview]                           
        if len(params) == 10:
            block.extend([1])
        elif len(params) == 9:
            block.extend([1])
        else:
            block.extend([0])

        self.oscServer.sendOSC("/devicerack", block)

    def deleteDevice(self, msg):

        type = msg[2]
        tid = msg[3]
        device_id = msg[4]

        number_of_steps = msg[5]

        if type == 0:
            track = LiveUtils.getSong().tracks[tid]

        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track

        device = track.devices[device_id]


        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]

        track.delete_device(device_id)

    def deleteReturnDevice(self, msg):
        tr = msg[2]
        de = msg[3]
        track = LiveUtils.getSong().return_tracks[tr]
        track.delete_device(de)

    
    def deleteMasterDevice(self, msg):
        de = msg[2]
        track = LiveUtils.getSong().master_track
        track.delete_device(de)



    def move_device(self, msg):


        type = msg[2]
        track_id = msg[3]
        device_id = msg[4]
        new_index = msg[5]
        number_of_steps = msg[6]


        if type == 1:
            
            track = LiveUtils.getSong().tracks[track_id]
        elif type == 3:
            
            track = LiveUtils.getSong().return_tracks[track_id]
        else:
            
            track = LiveUtils.getSong().master_track
        
        device = track.devices[device_id]
        
        for i in range(number_of_steps):
            chain_id = msg[7+i*2]
            device_id = msg[8+i*2]
            
            chain = device.chains[chain_id]
            device = chain.devices[device_id]

        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.select_device(device)
        

        parent = device.canonical_parent
        device_index = list(parent.devices).index(device)
        
        if new_index > device_index:
        
            if new_index > len(parent.devices) + 1 and isinstance(parent, Live.Chain.Chain):
                move_behind=True
                self.move_out(parent.canonical_parent, move_behind,device)

            elif new_index < len(parent.devices):
                right_device = parent.devices[new_index]
                if right_device.can_have_chains and right_device.view.is_showing_chain_devices and right_device.view.selected_chain:
                    move_to_end = False
                    self.move_in(right_device, move_to_end,device)
                else:
                    LiveUtils.getSong().move_device(device, parent, new_index)

        else:
            parent = device.canonical_parent
            if new_index > 0:
                left_device = parent.devices[new_index]
                if left_device.can_have_chains and left_device.view.is_showing_chain_devices and left_device.view.selected_chain:
                    move_to_end=True
                    self.move_in(left_device, move_to_end,device)
                else:
                    LiveUtils.getSong().move_device(device, parent, new_index)
            else:
                LiveUtils.getSong().move_device(device, parent, new_index)


    def move_out(self, rack, move_behind,device):
        parent = rack.canonical_parent
        rack_index = list(parent.devices).index(rack)
        LiveUtils.getSong().move_device(device, parent, rack_index + 1 if move_behind else rack_index)
    
    def move_in(self, rack, move_to_end,device):
        chain = rack.view.selected_chain
        if chain:
            LiveUtils.getSong().move_device(device, chain, len(chain.devices) if move_to_end else 0)


    def simpler_meta(self, msg):

        type = msg[2]
        tid = msg[3]
        did = msg[4]
        
        number_of_steps = msg[5]

        
        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track
        
        device = track.devices[did]
        num = len(track.devices)
        indices = []
        device_id = -1


        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]

            chain = device.chains[chain_id]
            indices.append(int(chain_id))
            
            device = chain.devices[device_id]
            num = len(chain.devices)
            
            indices.append(int(device_id))


        if device.class_name == 'OriginalSimpler':
            try:
                self.simplerListener.update_playbackmode(device, track, tid, did, type , number_of_steps, indices)
                simpler = device
                sample = simpler.sample
                if not sample:
                    return
                    
                self.simplerListener.update_slices(device, track, tid, did, type, number_of_steps, indices,sample)
                self.simplerListener.update_gain(device, track, tid, did, type, number_of_steps, indices,sample)
                self.simplerListener.update_marker(device, track, tid, did, type, number_of_steps, indices,sample)
                self.simplerListener.update_sample_warping(device, track, tid, did, type, number_of_steps, indices,sample)
                self.simplerListener.update_sample_warping_mode(device, track, tid, did, type, number_of_steps, indices,sample)
            except:
                self.error_log("DeviceCallbacks: simpler_meta failed")

    def expand_deviceCB(self, msg):

        self.ta_logger("expand_deviceCB",4)

        type = msg[2]
        tid = msg[3]
        did = msg[4]
        
        number_of_steps = msg[5]

        
        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track
        
        device = track.devices[did]
        num = len(track.devices)
        indices = []
        device_id = -1


        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]

            chain = device.chains[chain_id]
            indices.append(int(chain_id))
            
            device = chain.devices[device_id]
            num = len(chain.devices)
            
            indices.append(int(device_id))
        

        if device.class_name == 'OriginalSimpler':
            try:
                self.touchAble.tACommon.expand_simpler(device)
                self.simplerListener.update_playbackmode(device, track, tid, did, type , number_of_steps, indices)
            except:
                self.error_log("DeviceCallbacks: expand_simpler failed")
            try:
                self.touchAble.tACommon.send_update_for_device(device, track, tid, did, type, num, number_of_steps, indices, -1)
            except:
                self.error_log("DeviceCallbacks: send_update_for_device failed")
            
            device_data = [int(type)]
            device_data.append(int(tid))
            device_data.append(int(did))
            device_data.append(int(number_of_steps))
            
            for index in range(number_of_steps * 2):
                device_data.append(int(indices[index]))
        
            self.oscServer.sendOSC("/device/simpler/ui_update", (tuple(device_data)))

        elif device.class_name == 'MultiSampler':
            try:
                self.touchAble.tACommon.expand_multi_sampler(device)
            except:
                self.error_log("DeviceCallbacks: expand_multi_sampler failed")
    


