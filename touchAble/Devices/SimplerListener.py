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




class SimplerListener:
    __doc__ = "Listener class adding Simpler Listener for Live"


    simpler_selected_slice_listener = defaultdict(dict)
    simpler_playing_position_listener = defaultdict(dict)
    simpler_playbackmode_listener = defaultdict(dict)
    simpler_slicing_playbackmode_listener = defaultdict(dict)
    simpler_sampler_listener = defaultdict(dict)


    sample_slice_listener = defaultdict(dict)
    sample_slice_sensitivity_listener = defaultdict(dict)
    sample_gain_listener = defaultdict(dict)
    sample_end_marker_listener = defaultdict(dict)
    sample_start_marker_listener = defaultdict(dict)
    sample_warping_listener = defaultdict(dict)
    sample_warping_mode_listener = defaultdict(dict)
    maxSampleLength = 1024
    
    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
            self.error_log = touchAble.error_log
            self.ta_logger = self.touchAble.ta_logger
        else:
            return



    def add_listener_for_simpler(self, device, track, tid, did, type, num, number_of_steps, indices):
        
        message = "add_listener_for_simpler for device: " + str(device.name) + "on track: " + str(tid) + "and device id: " + str(did)
        self.ta_logger(message, 4)

        cb1 = lambda :self.update_playbackmode(device, track, tid, did, type , number_of_steps, indices)        
        cb2 = lambda :self.update_selected_slice(device, track, tid, did, type , number_of_steps, indices)
        cb3 = lambda :self.update_simpler_playing_position(device, track, tid, did, type , number_of_steps, indices)
        cb5 = lambda :self.update_slicing_playback_mode(device, track, tid, did, type , number_of_steps, indices)
        cb6 = lambda :self.update_simpler_sample(device, track, tid, did, type , number_of_steps, indices)

        key = '%s.%s' % (type, tid)
        simpler_playbackmode_listener  = self.simpler_playbackmode_listener[key]
        simpler_slicing_playbackmode_listener = self.simpler_slicing_playbackmode_listener[key]
        simpler_selected_slice_listener = self.simpler_selected_slice_listener[key]
        simpler_playing_position_listener = self.simpler_playing_position_listener[key]
        simpler_sampler_listener = self.simpler_sampler_listener[key]

        simpler = device

            
        if simpler_playbackmode_listener.has_key(device) != 1:
            #self.update_playbackmode(simpler, track, tid, did, type , number_of_steps, indices)
            device.add_playback_mode_listener(cb1)
            simpler_playbackmode_listener[device] = cb1
        
        if simpler_selected_slice_listener.has_key(device.view) != 1:
            #self.update_selected_slice(simpler, track, tid, did, type , number_of_steps, indices)
            device.view.add_selected_slice_listener(cb2)
            simpler_selected_slice_listener[device.view] = cb2
        
        if simpler_playing_position_listener.has_key(device) != 1:
            #self.update_simpler_playing_position(device, track, tid, did, type , number_of_steps, indices)
            device.add_playing_position_listener(cb3)
            simpler_playing_position_listener[device] = cb3
                
        if simpler_slicing_playbackmode_listener.has_key(device) != 1:
            #self.update_slicing_playback_mode(device, track, tid, did, type , number_of_steps, indices)
            device.add_slicing_playback_mode_listener(cb5)
            simpler_slicing_playbackmode_listener[device] = cb5

        if simpler_sampler_listener.has_key(device) != 1:
            #self.update_slicing_playback_mode(device, track, tid, did, type , number_of_steps, indices)
            device.add_sample_listener(cb6)
            simpler_sampler_listener[device] = cb6
        
        
    
        self.add_listener_for_simpler_sample(device, track, tid, did, type, number_of_steps, indices)
                


    def remove_simpler_listeners_of_track(self, track, tid, type):

        message = "remove_simpler_listeners_of_track for track: " + str(tid) + "and type: " + str(type)
        self.ta_logger(message, 4)

        key = '%s.%s' % (type, tid)

        if self.simpler_slicing_playbackmode_listener.has_key(key) == 1:
            simpler_slicing_playbackmode_listener = self.simpler_slicing_playbackmode_listener[key]
            for pr in simpler_slicing_playbackmode_listener:
                if pr != None:
                    ocb = simpler_slicing_playbackmode_listener[pr]
                    if pr.slicing_playback_mode_has_listener(ocb) == 1:
                        pr.remove_slicing_playback_mode_listener(ocb)




            del self.simpler_slicing_playbackmode_listener[key]

        if self.simpler_playbackmode_listener.has_key(key) == 1:
            simpler_playbackmode_listener = self.simpler_playbackmode_listener[key]
            for pr in simpler_playbackmode_listener:
                if pr != None:
                    ocb = simpler_playbackmode_listener[pr]
                    if pr.playback_mode_has_listener(ocb) == 1:
                        pr.remove_playback_mode_listener(ocb)


            del self.simpler_playbackmode_listener[key]


        if self.simpler_selected_slice_listener.has_key(key) == 1:
            simpler_selected_slice_listener = self.simpler_selected_slice_listener[key]
            
            for pr in simpler_selected_slice_listener:
                if pr != None:
                    ocb = simpler_selected_slice_listener[pr]
                    if pr.selected_slice_has_listener(ocb) == 1:
                        pr.remove_selected_slice_listener(ocb)
    
            del self.simpler_selected_slice_listener[key]
    

        if self.simpler_playing_position_listener.has_key(key) == 1:
            simpler_playing_position_listener = self.simpler_playing_position_listener[key]
        
            for pr in simpler_playing_position_listener:
                if pr != None:
                    ocb = simpler_playing_position_listener[pr]
                    if pr.playing_position_has_listener(ocb) == 1:
                        pr.remove_playing_position_listener(ocb)
    
            del self.simpler_playing_position_listener[key]


        if self.simpler_sampler_listener.has_key(key) == 1:
            simpler_sampler_listener = self.simpler_sampler_listener[key]
        
            for pr in simpler_sampler_listener:
                if pr != None:
                    ocb = simpler_sampler_listener[pr]
                    if pr.sample_has_listener(ocb) == 1:
                        pr.remove_sample_listener(ocb)

                try:
                    message = "remove_listener_for_simpler_sample for device: " + str(device.name) + "on track: " + str(tid) + "and device id: " + str(did)
                    self.ta_logger(message, 4)
                    #self.remove_listener_for_simpler_sample(0, track, tid, 0, type, 0, 0)
                except:
                    self.error_log("could not remove listener for sample")

    
            del self.simpler_sampler_listener[key]

        #self.remove_listener_for_simpler_sample(device, track, tid, did, type, number_of_steps, indices)



    def update_simpler_sample(self, device, track, tid, did, type , number_of_steps, indices):

        message = "update_simpler_sample for device: " + str(device.name) + "on track: " + str(tid) + "and device id: " + str(did)
        self.ta_logger(message, 4)

        slicing_pp_mode_data = [int(type)]
        slicing_pp_mode_data.append(int(tid))
        slicing_pp_mode_data.append(int(did))
        slicing_pp_mode_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            slicing_pp_mode_data.append(int(indices[index]))


        self.update_simpler_waveform(device, track, tid, did, type, number_of_steps, indices, 0, 1)
        self.add_listener_for_simpler_sample(device, track, tid, did, type, number_of_steps, indices)


    def update_slicing_playback_mode(self, device, track, tid, did, type , number_of_steps, indices):
    
        slicing_pp_mode_data = [int(type)]
        slicing_pp_mode_data.append(int(tid))
        slicing_pp_mode_data.append(int(did))
        slicing_pp_mode_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            slicing_pp_mode_data.append(int(indices[index]))
    
        slicing_pp_mode = device.slicing_playback_mode
        slicing_pp_mode_data.append(int(slicing_pp_mode))
        
        self.oscServer.sendOSC("/device/simpler/update_simpler_slicing_pp_mode", slicing_pp_mode_data)
            

    def update_simpler_playing_position(self, device, track, tid, did, type , number_of_steps, indices):

        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))

        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))

        play_pos = device.playing_position
        play_pos_data.append(play_pos)

        self.oscServer.sendOSC("/device/simpler/update_simpler_playing_position", play_pos_data)


    def update_selected_slice(self, device, track, tid, did, type , number_of_steps, indices):

        slice_data = [int(type)]
        slice_data.append(int(tid))
        slice_data.append(int(did))
        slice_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            slice_data.append(int(indices[index]))
        
        if device.sample != None:
        
            #message = "selected slice " + str(device.view.selected_slice)
            #self.oscServer.sendOSC("/NSLOG_REPLACE", message)

            sel_slice_val = device.view.selected_slice
            if sel_slice_val >= 0:
                slice_data.append(sel_slice_val)
                self.oscServer.sendOSC("/device/simpler/update_selected_slice", slice_data)


    def update_slices(self, device, track, tid, did, type, number_of_steps, indices, sample):
        
        slices = sample.slices
        length = sample.length
                        
        slice_data = [int(type)]
        slice_data.append(int(tid))
        slice_data.append(int(did))
        slice_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            slice_data.append(int(indices[index]))

        sel_slice_val = device.view.selected_slice

        #slice_data.append(int(sel_slice_val))

        slice_data.append(int(len(slices)))
        
        for pid in range(len(slices)):
            slice = slices[pid]
            message = str(pid) + str(slice)
            slice_val = slice*self.maxSampleLength/length
            slice_data.append(float(slice))


        self.oscServer.sendOSC("/device/simpler/update_slices", (tuple(slice_data)))


    def update_playbackmode(self, simpler, track, tid, did, type , number_of_steps, indices):
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "playbackmode got updated")

        waveform_data = [int(type)]
        waveform_data.append(int(tid))
        waveform_data.append(int(did))
        waveform_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            waveform_data.append(int(indices[index]))

        waveform_data.append(int(simpler.playback_mode))

        #self.oscServer.sendOSC("/NSLOG_REPLACE", str(simpler.playback_mode))

        self.oscServer.sendOSC("/device/simpler/update_playback_mode", waveform_data)


    def update_simpler_waveformcb(self, msg):

        type = msg[2]
        tid = msg[3]
        did = msg[4]
        start_in_percent = msg[5]
        end_in_percent = msg[6]

        number_of_steps = msg[7]
        

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
            chain_id = msg[8+i*2]
            device_id = msg[9+i*2]
        
            chain = device.chains[chain_id]
            indices.append(int(chain_id))
            
            device = chain.devices[device_id]
            num = len(chain.devices)
            
            indices.append(int(device_id))

        if device.class_name == 'OriginalSimpler':
            simpler = device

            self.update_simpler_waveform(simpler, track, tid, did, type, number_of_steps, indices, start_in_percent, end_in_percent)




    def update_simpler_waveform(self, simpler, track, tid, did, type, number_of_steps, indices, start_in_percent, end_in_percent):
        try:

            sample = simpler.sample
            
            
            sample_length = simpler.sample.length
            path = simpler.sample.file_path

            reset_data = [int(type)]
            reset_data.append(int(tid))
            reset_data.append(int(did))
            reset_data.append(int(number_of_steps))
        

            for index in range(number_of_steps * 2):
                reset_data.append(int(indices[index]))
        
            reset_data.append(str(path))
            reset_data.append(float(start_in_percent))
            reset_data.append(float(end_in_percent))

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
            pass



    def remove_listener_for_simpler_sample(self, device, track, tid, did, type, number_of_steps, indices):

        simpler = device
        key = '%s.%s' % (type, tid)


        if self.sample_slice_listener.has_key(key) == 1:
            sample_slice_listener = self.sample_slice_listener[key]
            for pr in sample_slice_listener:
                if pr != None:
                    ocb = sample_slice_listener[pr]
                    if pr.slices_has_listener(ocb) == 1:
                        pr.remove_slices_listener(ocb)


            del self.sample_slice_listener[key]

        if self.sample_gain_listener.has_key(key) == 1:
            sample_gain_listener = self.sample_gain_listener[key]
            for pr in sample_gain_listener:
                if pr != None:
                    ocb = sample_gain_listener[pr]
                    if pr.gain_has_listener(ocb) == 1:
                        pr.remove_gain_listener(ocb)


            del self.sample_gain_listener[key]


        if self.sample_end_marker_listener.has_key(key) == 1:
            sample_end_marker_listener = self.sample_end_marker_listener[key]
            for pr in sample_end_marker_listener:
                if pr != None:
                    ocb = sample_end_marker_listener[pr]
                    if pr.end_marker_has_listener(ocb) == 1:
                        pr.remove_end_marker_listener(ocb)


            del self.sample_end_marker_listener[key]


        if self.sample_start_marker_listener.has_key(key) == 1:
            sample_start_marker_listener = self.sample_start_marker_listener[key]
            for pr in sample_start_marker_listener:
                if pr != None:
                    ocb = sample_start_marker_listener[pr]
                    if pr.start_marker_has_listener(ocb) == 1:
                        pr.remove_start_marker_listener(ocb)


            del self.sample_start_marker_listener[key]


        if self.sample_warping_listener.has_key(key) == 1:
            sample_warping_listener = self.sample_warping_listener[key]
            for pr in sample_warping_listener:
                if pr != None:
                    ocb = sample_warping_listener[pr]
                    if pr.warping_has_listener(ocb) == 1:
                        pr.remove_warping_listener(ocb)


            del self.sample_warping_listener[key]


        if self.sample_warping_mode_listener.has_key(key) == 1:
            sample_warping_mode_listener = self.sample_warping_mode_listener[key]
            for pr in sample_warping_mode_listener:
                if pr != None:
                    ocb = sample_warping_mode_listener[pr]
                    if pr.warp_mode_has_listener(ocb) == 1:
                        pr.remove_warp_mode_listener(ocb)


            del self.sample_warping_mode_listener[key]


        if self.sample_slice_sensitivity_listener.has_key(key) == 1:
            sample_slice_sensitivity_listener = self.sample_slice_sensitivity_listener[key]
            for pr in sample_slice_sensitivity_listener:
                if pr != None:
                    ocb = sample_slice_sensitivity_listener[pr]
                    if pr.slicing_sensitivity_has_listener(ocb) == 1:
                        pr.remove_slicing_sensitivity_listener(ocb)


            del self.sample_slice_sensitivity_listener[key]




    def add_listener_for_simpler_sample(self, device, track, tid, did, type, number_of_steps, indices):

        message = "add_listener_for_simpler_sample for device: " + str(device.name) + "on track: " + str(tid) + "and device id: " + str(did)
        self.ta_logger(message, 4)

        #self.remove_listener_for_simpler_sample(device, track, tid, did, type, number_of_steps, indices)



        simpler = device
        sample = simpler.sample
        
        if not sample:
            message = "add_listener_for_simpler_sample no sample found for track: " + str(tid) + "and type: " + str(type)
            self.ta_logger(message, 4)
            return
                
        key = '%s.%s' % (type, tid)

        sample_slice_listener  = self.sample_slice_listener[key]
        sample_gain_listener  = self.sample_gain_listener[key]
        sample_end_marker_listener = self.sample_end_marker_listener[key]
        sample_start_marker_listener = self.sample_start_marker_listener[key]
        sample_warping_listener = self.sample_warping_listener[key]
        sample_warping_mode_listener = self.sample_warping_mode_listener[key]
        sample_slice_sensitivity_listener = self.sample_slice_sensitivity_listener[key]
        
        self.update_slices(device, track, tid, did, type, number_of_steps, indices,sample)
        self.update_gain(device, track, tid, did, type, number_of_steps, indices,sample)
        self.update_slice_sensitivity(device, track, tid, did, type, number_of_steps, indices,sample)
        self.update_marker(device, track, tid, did, type, number_of_steps, indices,sample)
        self.update_sample_warping(device, track, tid, did, type, number_of_steps, indices,sample)
        self.update_sample_warping_mode(device, track, tid, did, type, number_of_steps, indices,sample)

        cb = lambda :self.update_slices(device, track, tid, did, type, number_of_steps, indices,sample)
        
        cb1 = lambda :self.update_gain(device, track, tid, did, type, number_of_steps, indices,sample)
        
        cb2 = lambda :self.update_slice_sensitivity(device, track, tid, did, type, number_of_steps, indices,sample)
        
        cb3 = lambda :self.update_marker(device, track, tid, did, type, number_of_steps, indices,sample)

        cb4 = lambda :self.update_sample_warping(device, track, tid, did, type, number_of_steps, indices,sample)

        cb5 = lambda :self.update_sample_warping_mode(device, track, tid, did, type, number_of_steps, indices,sample)
        
        if sample_slice_listener.has_key(sample) != 1:
            sample.add_slices_listener(cb)
            sample_slice_listener[sample] = cb
    
        if sample_gain_listener.has_key(sample) != 1:
            sample.add_gain_listener(cb1)
            sample_gain_listener[sample] = cb1
    
        if sample_slice_sensitivity_listener.has_key(sample) != 1:
            sample.add_slicing_sensitivity_listener(cb2)
            sample_slice_sensitivity_listener[sample] = cb2

        if sample_end_marker_listener.has_key(sample) != 1:
            sample.add_end_marker_listener(cb3)
            sample_end_marker_listener[sample] = cb3

        if sample_start_marker_listener.has_key(sample) != 1:
            sample.add_start_marker_listener(cb3)
            sample_start_marker_listener[sample] = cb3

        if sample_warping_listener.has_key(sample) != 1:
            sample.add_warping_listener(cb4)
            sample_warping_listener[sample] = cb4

        if sample_warping_mode_listener.has_key(sample) != 1:
            sample.add_warp_mode_listener(cb5)
            sample_warping_mode_listener[sample] = cb5



    def update_simpler_parameters(self,device, track, tid, did, type , number_of_steps, indices):

        if device.class_name == 'OriginalSimpler':

            try:
                message = "add_listener_for_simpler_sample for device: " + str(device.name) + "on track: " + str(tid) + "and device id: " + str(did)
                self.ta_logger(message, 4)
                #self.add_listener_for_simpler_sample(device, track, tid, did, type, number_of_steps, indices)
            except:
                self.error_log("SimplerListener: add_listener_for_simpler_sample failed")

            try:
                self.update_playbackmode(device, track, tid, did, type , number_of_steps, indices)
                self.update_slicing_playback_mode(device, track, tid, did, type , number_of_steps, indices)
                self.update_selected_slice(device, track, tid, did, type , number_of_steps, indices)
                self.update_simpler_playing_position(device, track, tid, did, type , number_of_steps, indices)
                self.update_slicing_playback_mode(device, track, tid, did, type , number_of_steps, indices)
                self.update_simpler_sample_parameters(device, track, tid, did, type , number_of_steps, indices)
            except:
                self.error_log("SimplerListener: update_simpler_parameters update sample failed")


    def update_simpler_sample_parameters(self,device, track, tid, did, type , number_of_steps, indices):
        
        if device.sample != None:
            self.update_slices(device, track, tid, did, type, number_of_steps, indices,device.sample)
            self.update_gain(device, track, tid, did, type, number_of_steps, indices,device.sample)
            self.update_slice_sensitivity(device, track, tid, did, type, number_of_steps, indices,device.sample)
            self.update_marker(device, track, tid, did, type, number_of_steps, indices,device.sample)
            self.update_sample_warping(device, track, tid, did, type, number_of_steps, indices,device.sample)
            self.update_sample_warping_mode(device, track, tid, did, type, number_of_steps, indices,device.sample)


    def update_sample_warping(self, device, track, tid, did, type, number_of_steps, indices,sample):

        warping_data = [int(type)]
        warping_data.append(int(tid))
        warping_data.append(int(did))
        warping_data.append(int(number_of_steps))
            
        for index in range(number_of_steps * 2):
            warping_data.append(int(indices[index]))
        
        warping_data.append(sample.warping)

        self.oscServer.sendOSC("/device/simpler/update_warping", (tuple(warping_data)))
    
    def update_sample_warping_mode(self, device, track, tid, did, type, number_of_steps, indices,sample):
    
        warping_mode = sample.warp_mode
        
        warping_mode_data = [int(type)]
        warping_mode_data.append(int(tid))
        warping_mode_data.append(int(did))
        warping_mode_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            warping_mode_data.append(int(indices[index]))

        """ for obj_string in dir(device.sample):
            self.oscServer.sendOSC("/NSLOG_REPLACE", obj_string) """
        
        warping_mode_data.append(warping_mode)
        
        self.oscServer.sendOSC("/device/simpler/update_warping_mode", (tuple(warping_mode_data)))
    


    def update_gain(self, device, track, tid, did, type, number_of_steps, indices, sample):
        
        gain = sample.gain

        gain_string = sample.gain_display_string()

        gain_data = [int(type)]
        gain_data.append(int(tid))
        gain_data.append(int(did))
        gain_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            gain_data.append(int(indices[index]))
        
        """ for obj_string in dir(device.sample):
            self.oscServer.sendOSC("/NSLOG_REPLACE", obj_string) """

        gain_data.append(gain)
        gain_data.append(gain_string.__str__())
        self.oscServer.sendOSC("/device/simpler/update_gain", (tuple(gain_data)))
    
    
    
    
    def update_slice_sensitivity(self, device, track, tid, did, type, number_of_steps, indices, sample):
        
        slicing_sensitivity = sample.slicing_sensitivity
        
        gain_data = [int(type)]
        gain_data.append(int(tid))
        gain_data.append(int(did))
        gain_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            gain_data.append(int(indices[index]))
        
        """ for obj_string in dir(sample):
            self.oscServer.sendOSC("/NSLOG_REPLACE", obj_string) """
        
        gain_data.append(slicing_sensitivity)
        self.oscServer.sendOSC("/device/simpler/slicing_sensitivity", (tuple(gain_data)))
    


    def update_marker(self, device, track, tid, did, type, number_of_steps, indices, sample):

        start_marker = sample.start_marker
        end_marker = sample.end_marker
        
        length = sample.length

        marker_data = [int(type)]
        marker_data.append(int(tid))
        marker_data.append(int(did))
        marker_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            marker_data.append(int(indices[index]))
        
        """ for obj_string in dir(sample):
            self.oscServer.sendOSC("/NSLOG_REPLACE", obj_string) """
        
        """ start_val = float(start_marker*self.maxSampleLength)/length
        end_val = float(end_marker*self.maxSampleLength)/length """


        marker_data.append(start_marker)
        marker_data.append(end_marker)
        
        self.oscServer.sendOSC("/device/simpler/update_marker", (tuple(marker_data)))
