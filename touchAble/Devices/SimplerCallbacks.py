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

class SimplerCallbacks:
    # LMH
    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble

        else:
            return

        self.callbackManager.add(self.simpler_gain, "/simpler_gain")
        self.callbackManager.add(self.update_simpler_waveformcb, "/update_simpler_waveform")
        self.callbackManager.add(self.simpler_sensitivity, "/simpler_sensitivity")
        self.callbackManager.add(self.simpler_pad_slicing, "/simpler_pad_slicing")
        self.callbackManager.add(self.simpler_slicing_playback_mode, "/simpler_slicing_playback_mode")
        self.callbackManager.add(self.simpler_start_marker, "/simpler_start_marker")
        self.callbackManager.add(self.simpler_end_marker, "/simpler_end_marker")
        self.callbackManager.add(self.simpler_selected_slice, "/simpler_selected_slice")
        self.callbackManager.add(self.simpler_move_slice, "/simpler_move_slice")
        self.callbackManager.add(self.simpler_new_slice, "/simpler_new_slice")
        self.callbackManager.add(self.simpler_remove_slice, "/simpler_remove_slice")
        self.callbackManager.add(self.simpler_slicing_type, "/simpler_slicing_type")
        self.callbackManager.add(self.reverse_sample, "/reverse_sample")
        self.callbackManager.add(self.crop_sample, "/crop_sample")
        self.callbackManager.add(self.warp_double, "/warp_double")
        self.callbackManager.add(self.warp_half, "/warp_half")
        self.callbackManager.add(self.warp_as, "/warp_as")
        self.callbackManager.add(self.warping, "/warping")
        self.callbackManager.add(self.warp_mode, "/warp_mode")

        self.callbackManager.add(self.convert_clip_to_simpler, "/converttosimpler")
        self.callbackManager.add(self.simpler_playback_mode, "/live/track/device/simpler/playback_mode")
        self.callbackManager.add(self.sliced_simpler_to_drum_rack, "/sliced_simpler_to_drum_rack")
        self.callbackManager.add(self.create_midi_track_with_simpler, "/create_midi_track_with_simpler")
        self.callbackManager.add(self.reset_simpler_slices, "/reset_simpler_slices")


    def get_device_for_message(self,msg):

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
        
        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]
        

        return device


    def reset_simpler_slices(self, msg):
        
        
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
    
        if device.class_name == 'OriginalSimpler':
            simpler = device
            sample = simpler.sample
        
            if not sample:
                return
                
            sample.reset_slices()

    def sliced_simpler_to_drum_rack(self, msg):
        
        
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
    
        if device.class_name == 'OriginalSimpler':
            Live.Conversions.sliced_simpler_to_drum_rack(LiveUtils.getSong(), device)

    def create_midi_track_with_simpler(self, msg):
        
        
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
    
        if device.class_name == 'OriginalSimpler':
            Live.Conversions.create_midi_track_with_simpler(LiveUtils.getSong(), device)


    def simpler_playback_mode(self, msg):
        
        
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        a_playback_mode = msg[new_index]
    
        if device.class_name == 'OriginalSimpler':
            simpler = device
            simpler.playback_mode = a_playback_mode

    
    


    def simpler_gain(self, msg):
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2

        if device.class_name == 'OriginalSimpler':

            simpler = device
            gain_val = msg[new_index]
            sample = simpler.sample
            sample.gain = gain_val



    def simpler_pad_slicing(self, msg):

        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            gain_val = msg[new_index]
            sample = simpler.sample
            simpler.pad_slicing = gain_val


    def simpler_slicing_playback_mode(self, msg):
        
        
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2


        if device.class_name == 'OriginalSimpler':
            
            simpler = device
            gain_val = msg[new_index]
            sample = simpler.sample
            
            simpler.slicing_playback_mode = gain_val


    def simpler_sensitivity(self, msg):
        
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            gain_val = msg[new_index]
            sample = simpler.sample
            sample.slicing_sensitivity = gain_val


    def simpler_start_marker(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            start_marker = msg[new_index]
            sample = simpler.sample
            sample.start_marker = start_marker

    def simpler_end_marker(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            end_marker = msg[new_index]
            sample = simpler.sample
            sample.end_marker = end_marker

    def simpler_slicing_type(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            end_marker = msg[new_index]
            sample = simpler.sample
            sample.end_marker = end_marker


    def reverse_sample(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            simpler.reverse()


    def crop_sample(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            simpler.crop()

    def warp_half(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            simpler.warp_half()

    def warp_double(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            simpler.warp_double()

    def warp_as(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            simpler.warp_as()

    def warping(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler' and device.sample != None:
            device.sample.warping = msg[new_index]

    def warp_mode(self, msg):
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler' and device.sample != None:
            device.sample.warp_mode = msg[new_index]


    def simpler_selected_slice(self, msg):
    

        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            sample = simpler.sample
            selected_slice = msg[new_index]
            
            messsage = "new slice " + str(selected_slice) + "old slice " + str(simpler.view.selected_slice)

            #sample.insert_slice(selected_slice)
            #sample.remove_slice(simpler.view.selected_slice)
            simpler.view.selected_slice = selected_slice


    def simpler_move_slice(self, msg):

        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            sample = simpler.sample
            selected_slice_pos = msg[new_index]

            sample.move_slice(simpler.view.selected_slice,selected_slice_pos)
            simpler.view.selected_slice = selected_slice_pos

    def simpler_new_slice(self, msg):

        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            sample = simpler.sample
            selected_slice_pos = msg[new_index]

            sample.insert_slice(selected_slice_pos)
            simpler.view.selected_slice = selected_slice_pos


    def simpler_remove_slice(self, msg):

        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        
        if device.class_name == 'OriginalSimpler':
            simpler = device
            sample = simpler.sample
            selected_slice_pos = msg[new_index]

            sample.remove_slice(selected_slice_pos)

    def convert_clip_to_simpler(self,msg):
    
        tid = msg[2]
        cid = msg[3]

        clip = LiveUtils.getClip(tid, cid)
    
        Live.Conversions.create_midi_track_with_simpler(clip)


    def update_simpler_waveformcb(self, msg):
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update_simpler_waveformcb")

        type = msg[2]
        tid = msg[3]
        did = msg[4]
        start_in_percent = msg[5]
        end_in_percent = msg[6]

        number_of_steps = msg[7]
        
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update_simpler_waveformcb0")

        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update_simpler_waveformcb05")

        device = track.devices[did]
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update_simpler_waveformcb1115")

        num = len(track.devices)
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update_simpler_waveformcb15")

        indices = []
        device_id = -1
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update_simpler_waveformcb25")

        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update_simpler_waveformcb1")

        for i in range(number_of_steps):
            chain_id = msg[8+i*2]
            device_id = msg[9+i*2]
        
            chain = device.chains[chain_id]
            indices.append(int(chain_id))
            
            device = chain.devices[device_id]
            num = len(chain.devices)
            
            indices.append(int(device_id))

        if device.class_name == 'OriginalSimpler':
            simpler = device
            #self.oscServer.sendOSC("/NSLOG_REPLACE", "update_simpler_waveformcb2")

            self.update_simpler_waveform(simpler, track, tid, did, type, number_of_steps, indices, start_in_percent, end_in_percent)




    def update_simpler_waveform(self, simpler, track, tid, did, type, number_of_steps, indices, start_in_percent, end_in_percent):
        try:
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("update_simpler_waveform"))

            sample = simpler.sample
            
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("update_simpler_waveform2"))
            
            sample_length = simpler.sample.length
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("update_simpler_waveform3"))

            path = simpler.sample.file_path
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("update_simpler_waveform4"))

            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("update_simpler_waveform3"))

            reset_data = [int(type)]
            reset_data.append(int(tid))
            reset_data.append(int(did))
            reset_data.append(int(number_of_steps))
        
            # self.oscServer.sendOSC("/NSLOG_REPLACE", (str(path)))

            for index in range(number_of_steps * 2):
                reset_data.append(int(indices[index]))
        
            reset_data.append(str(path))
            reset_data.append(float(start_in_percent))
            reset_data.append(float(end_in_percent))
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("reset_waveform"))

            self.oscServer.sendOSC("/device/simpler/reset_waveform", (tuple(reset_data)))
    
            if simpler.sample.warping:
                try:
                    waveform_data = [int(tid)]
                    waveform_data.append(int(cid))
                    waveform_data.append(float(simpler.sample.sample_to_beat_time(simpler.sample.sample_length)))
            
                    self.oscServer.sendOSC("/device/simpler/sample_length", (tuple(waveform_data)))
                except:
                    pass
            else:
                pass
        
        except:
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("no wave file found"))
            pass

