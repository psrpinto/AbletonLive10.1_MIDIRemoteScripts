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


class DeviceListener:
    __doc__ = "Listener class adding Simpler Listener for Live"


    prlisten = defaultdict(dict)
    parameters_listeners = defaultdict(dict)
    wavetable_listeners = defaultdict(dict)
    simpler_listeners = defaultdict(dict)
    compressor_listeners = defaultdict(dict)
    plugin_listeners = defaultdict(dict)
    
    chainslisten = defaultdict(dict)
    chaindevicelisten = defaultdict(dict)

    device_name_listen = defaultdict(dict)

    devices_listen = {}
    drum_pad_listen = defaultdict(dict)
    drum_pads_listen = {}

    wavetableListener = 0
    simplerListener = 0
    compressorListener = 0
    pluginListener = 0

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


    def update_listeners_for_device(self, device, track, tid, did, type, num, number_of_steps, lis, device_id):

        message = "update_listeners_for_device for device: " + str(device.name) + "on track: " + str(tid) + "and device id: " + str(did)
        self.ta_logger(message, 4)


        try:
            self.add_device_listeners_for_track(track, int(tid), int(type))
        except:
            self.error_log("DeviceListener: add_device_listeners_for_track failed on update_listeners_for_device")
        try:
            self.touchAble.tACommon.send_update_for_device(device, track, int(tid), int(did), int(type), int(num), int(number_of_steps), lis, int(device_id))
        except:
            self.error_log("DeviceListener: send_update_for_device failed on update_listeners_for_device")



    def add_device_listeners_for_track(self, track, tid, type):

        message = "add_device_listeners_for_track for device on track: " + str(tid) + "and type: " + str(type)
        self.ta_logger(message, 4)

        try:
            self.remove_device_listeners_of_track(track, tid, type)
        except:
            self.error_log("DeviceListener: remove_device_listeners_of_track failed")
        
        try:
            self.add_devices_listener(track, tid, type)
        except:
            self.error_log("DeviceListener: add_devices_listener failed")


        try:
            self.wavetableListener = self.touchAble.tAListener.wavetableListener
            self.compressorListener = self.touchAble.tAListener.compressorListener
            self.pluginListener = self.touchAble.tAListener.pluginListener
            self.simplerListener = self.touchAble.tAListener.simplerListener
        except:
            self.error_log("DeviceListener: devices listener pointer assigment failed")


        key = '%s.%s' % (type, tid)

        self.prlisten[key] = {}
        self.parameters_listeners[key] = {}
        self.wavetable_listeners[key] = {}
        self.simpler_listeners[key] = {}
        self.compressor_listeners[key] = {}
        self.plugin_listeners[key] = {}
        
        self.chainslisten[key] = {}
        self.chaindevicelisten[key] = {}
        self.drum_pad_listen[key] = {}

        """ simpler device """
        self.simplerListener.simpler_playbackmode_listener[key] = {}
        self.simplerListener.simpler_slicing_playbackmode_listener[key] = {}
        self.simplerListener.simpler_selected_slice_listener[key] = {}
        self.simplerListener.simpler_playing_position_listener[key] = {}
        
        """ compressor device """
        self.compressorListener.compressor_available_input_routing_channels_listener[key] = {}
        self.compressorListener.compressor_available_input_routing_types_listener[key] = {}
        self.compressorListener.compressor_input_routing_channel_listener[key] = {}
        self.compressorListener.compressor_input_routing_type_listener[key] = {}
        
        """ wavetable device """
        self.wavetableListener.wavetable_filter_routing_listener[key] = {}
        self.wavetableListener.wavetable_modulation_matrix_listener[key] = {}
        self.wavetableListener.wavetable_mono_poly_listener[key] = {}
        self.wavetableListener.wavetable_oscillator_1_effect_listener[key] = {}
        self.wavetableListener.wavetable_oscillator_1_wavetable_category_listener[key] = {}
        self.wavetableListener.wavetable_oscillator_1_wavetable_index_listener[key] = {}
        self.wavetableListener.wavetable_oscillator_1_wavetables_listener[key] = {}
        self.wavetableListener.wavetable_oscillator_2_effect_listener[key] = {}
        self.wavetableListener.wavetable_oscillator_2_wavetable_category_listener[key] = {}
        self.wavetableListener.wavetable_oscillator_2_wavetable_index_listener[key] = {}
        self.wavetableListener.wavetable_oscillator_2_wavetables_listener[key] = {}
        self.wavetableListener.wavetable_poly_voices_listener[key] = {}
        self.wavetableListener.wavetable_unison_mode_listener[key] = {}
        self.wavetableListener.wavetable_unison_voice_count_listener[key] = {}
        self.wavetableListener.wavetable_visible_modulation_target_names_listener[key] = {}

        """ plugin device """
        self.pluginListener.plugin_presets_listener[key] = {}
        self.pluginListener.plugin_selected_preset_index_listener[key] = {}
        
        drum_pad_listen = self.drum_pad_listen[key]

        a = Live.Application.get_application().get_major_version()
        number_of_steps = 0
        i = 0
        indices = []

        if len(track.devices) >= 1:

            length_track_devices = len(track.devices)
            for did in range(length_track_devices):
                
                device = track.devices[did]
                lis = list(indices)
                try:
                    self.add_listener_for_device(track, tid, did, type, device, 0, lis, -1)
                except:
                    err_message = "DeviceListener: add_listener_for_device for track" + str(tid) + "failed"
                    self.error_log(err_message)

            
    def remove_device_listeners_of_track(self, track, tid, type):

        self.remove_devices_listener(track, tid, type)
        key = '%s.%s' % (type, tid)

        if self.prlisten.has_key(key) == 1:
            #self.oscServer.sendOSC('/live/track/device_listeners_found', 1)

            prlisten = self.prlisten[key]

            for pr in prlisten:
                if pr != None:
                    ocb = prlisten[pr]
                    if pr.value_has_listener(ocb) == 1:
                        pr.remove_value_listener(ocb)
            del self.prlisten[key]
                                                    
           

        if self.parameters_listeners.has_key(key) == 1:
           #self.oscServer.sendOSC('/live/track/device_listeners_found', 1)
           
            parameters_listeners = self.parameters_listeners[key]
               
            for pr in parameters_listeners:
                if pr != None:
                    ocb = parameters_listeners[pr]
                    if pr.parameters_has_listener(ocb) == 1:
                        pr.remove_parameters_listener(ocb)
            del self.parameters_listeners[key]


        try:
            self.wavetableListener = self.touchAble.tAListener.wavetableListener
            self.compressorListener = self.touchAble.tAListener.compressorListener
            self.pluginListener = self.touchAble.tAListener.pluginListener
            self.simplerListener = self.touchAble.tAListener.simplerListener
        except:
            self.error_log("DeviceListener: devices listener pointer assigment failed")
                
        if self.wavetable_listeners.has_key(key) == 1:
            try:
                self.wavetableListener.remove_wavetable_listeners_of_track(track, tid, type)
                del self.wavetable_listeners[key]
            except:
                self.error_log("DeviceListener: remove_wavetable_listeners_of_track failed")
        elif self.simpler_listeners.has_key(key) == 1:
            try:
                self.simplerListener.remove_simpler_listeners_of_track(track, tid, type)
                del self.simpler_listeners[key]
            except:
                self.error_log("DeviceListener: remove_simpler_listeners_of_track failed")

        elif self.compressor_listeners.has_key(key) == 1:
            try:
                self.compressorListener.remove_compressor_listeners_of_track(track, tid, type)
                del self.compressor_listeners[key]
            except:
                self.error_log("DeviceListener: remove_compressor_listeners_of_track failed")


        elif self.plugin_listeners.has_key(key) == 1:
            try:
                self.pluginListener.remove_plugin_listeners_of_track(track, tid, type)
                del self.plugin_listeners[key]
            except:
                self.error_log("DeviceListener: remove_plugin_listeners_of_track failed")

        
        """ compressor device """
        if self.chainslisten.has_key(key) == 1:
            #self.oscServer.sendOSC('/live/track/device_listeners_found', 1)
            
            chainslisten = self.chainslisten[key]
            
            for dev in chainslisten:
                if dev != None:
                    ocb = chainslisten[dev]
                    if dev.chains_has_listener(ocb) == 1:
                        dev.remove_chains_listener(ocb)
            del self.chainslisten[key]
    
    
    
        if self.drum_pad_listen.has_key(track) == 1:

            drum_pad_listen = self.drum_pad_listen[key]
        
            for drum_pad in drum_pad_listen:
                if drum_pad != None:
                    ocb = drum_pad_listen[drum_pad]
                    if drum_pad.name_has_listener(ocb) == 1:
                        drum_pad.remove_name_listener(ocb)
            del self.drum_pad_listen[key]

    def add_listener_for_device(self, track, tid, did, type, device, number_of_steps, indices, i):
        
        #self.oscServer.sendOSC("/NSLOG_REPLACE", ("add_listener_for_device", repr3(device.name)))

        #self.expand_device_dev(device)
        
        a = Live.Application.get_application().get_major_version()
        key = '%s.%s' % (type, tid)

        if i != -1:
            indices.append(int(i))
            number_of_steps = number_of_steps+1
        else:
            indic = []
            indices = list(indic)
        


        try:
            self.wavetableListener = self.touchAble.tAListener.wavetableListener
            self.compressorListener = self.touchAble.tAListener.compressorListener
            self.pluginListener = self.touchAble.tAListener.pluginListener
            self.simplerListener = self.touchAble.tAListener.simplerListener
        except:
            self.error_log("DeviceListener: devices listener pointer ass. failed")

        prlisten = self.prlisten[key]
        parameters_listeners = self.parameters_listeners[key]
        chaindevicelisten = self.chaindevicelisten[key]
        
        tr = device.canonical_parent
        
        num = len(tr.devices)
        lis = list(indices)


        cb = lambda :self.update_listeners_for_device(device, track, tid, did, type, num, number_of_steps, lis, -1)


        if parameters_listeners.has_key(device) != 1:
            device.add_parameters_listener(cb)
            parameters_listeners[device] = cb

            #self.oscServer.sendOSC("/NSLOG_REPLACE", "try add sample listener for simpler")
            #self.oscServer.sendOSC("/NSLOG_REPLACE", ("adding device listener", tid, did))

        a_version = Live.Application.get_application().get_major_version()
        if device.class_name == 'OriginalSimpler':
            try:
                self.simplerListener.add_listener_for_simpler(device, track, tid, did, type, num, number_of_steps, lis)
                self.simpler_listeners[key] = 1
            except:
                self.error_log("DeviceListener: simplerListener.add_listener_for_simpler failed")        
        elif device.class_name == 'InstrumentVector' and a_version >= 10:
            try:
                self.wavetableListener.add_listener_for_wavetable(device, track, tid, did, type, num, number_of_steps, lis)
                self.wavetable_listeners[key] = 1
            except:
                self.error_log("DeviceListener: wavetableListener.add_listener_for_wavetable failed")
        elif device.class_name == 'Compressor2' and a_version >= 10:
            try:
                self.compressorListener.add_listener_for_compressor(device, track, tid, did, type, num, number_of_steps, lis)
                self.compressor_listeners[key] = 1
            except:
                self.error_log("DeviceListener: compressorListener.add_listener_for_compressor failed")
        elif device.class_name == 'PluginDevice':
            try:
                self.pluginListener.add_listener_for_plugindevice(device, track, tid, did, type, num, number_of_steps, lis)
                self.plugin_listeners[key] = 1
            except:
                self.error_log("DeviceListener: pluginListener.add_listener_for_plugindevice failed")

        else:
            pass
            
        if a >= 9:
            if type == 0:
                if device.can_have_drum_pads == 1:
                    key = '%s.%s' % (type, tid)
                    drum_pad_listen = self.drum_pad_listen[key]
                    length_drum_pads = len(device.drum_pads)
                    for drum_id in range(length_drum_pads):
                        drum_pad = device.drum_pads[drum_id]
                        #self.oscServer.sendOSC("/NSLOG_REPLACE", "ADDING DRUM PAD LISTENER")
                        
                        self.add_drum_pad_listener(drum_pad_listen, drum_pad, int(tid), int(did), number_of_steps, lis)
        
        
            if device.can_have_chains == 1:
                
                chainslisten = self.chainslisten[key]
                if chainslisten.has_key(device) != 1:
                    device.add_chains_listener(cb)
                    chainslisten[device] = cb

                length_device_chains = len(device.chains)
                for chain_id in range(length_device_chains):
                    chain = device.chains[chain_id]

                    self.add_chain_devices_listener(track, tid, type, chain)
                    
                    listt = list(indices)
                    listt.append(int(chain_id))
                    another_length_device_chains = len(chain.devices)

                    for device_id in range(another_length_device_chains):
                        dev = chain.devices[device_id]

                        lis = list(listt)
                        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update add listener for device from itself" + device.name)

                        self.add_listener_for_device(track, tid, did, type, dev, number_of_steps, lis, device_id)
    
    
    
    
    

        #self.oscServer.sendOSC('/adding_device_listeners_for_device2', (int(type), int(tid), int(did), int(number_of_steps), tuple(indis)))
        
        #self.oscServer.sendOSC('/adding_device_listeners_for_device2', (tuple(indices)))

        if len(device.parameters) >= 1:
            length_device_parameters = len(device.parameters)
            for pid in range(length_device_parameters):
                param = device.parameters[pid]
                self.add_parameter_listener(prlisten, param, int(tid), int(did), int(pid), int(type), int(number_of_steps), tuple(indices))

        #self.oscServer.sendOSC('/adding_device_listeners_for_device3', (tuple(indices)))




    def add_parameter_listener(self, prlisten, param, tid, did, pid, type, number_of_steps, indices):
        cb = lambda :self.param_changestate(param, int(tid), int(did), int(pid), int(type), int(number_of_steps), indices)
        if prlisten.has_key(param) != 1:
            param.add_value_listener(cb)
            prlisten[param] = cb


    def rem_app_device_listener(self):
        if LiveUtils.getSong().appointed_device_has_listener(self.device_changestate) == 1:
            LiveUtils.getSong().remove_appointed_device_listener(self.device_changestate)
    
    
    def do_add_device_listeners(self, tracks, type):
        for tid in range(len(tracks)):
            track = tracks[tid]
            try:
                self.add_device_listeners_for_track(track, tid, type)
            except:
                err_message = "DeviceListener: add_device_listeners_for_track for track" + str(tid) + "failed"
                self.error_log(err_message)

            


    def do_remove_device_listeners(self, tracks, type):
        for tid in range(len(tracks)):
            track = tracks[tid]
            self.remove_device_listeners_of_track(track, tid, type)

    def rem_all_device_listeners(self):
        #self.oscServer.sendOSC('/live/track/removing_all_dev_listeners', 1)

        try:
            self.do_remove_device_listeners(LiveUtils.getSong().tracks,0)
        except:
            err_message = "DeviceListener: do_remove_device_listeners for track " + str(0) + " failed"
            self.error_log(err_message)
        try:
            self.do_remove_device_listeners(LiveUtils.getSong().return_tracks,2)
        except:
            err_message = "DeviceListener: do_remove_device_listeners for track " + str(1) + " failed"
            self.error_log(err_message)
        try:
            self.do_remove_device_listeners([LiveUtils.getSong().master_track],1)
        except:  
            err_message = "DeviceListener: do_remove_device_listeners for track " + str(2) + " failed"
            self.error_log(err_message)        
        
        
        
        #self.oscServer.sendOSC('/live/track/removing_all_dev_listeners', 2)

        for key in self.drum_pad_listen:
        
            #self.oscServer.sendOSC('/live/track/removing_all_dev_listeners', 3)
            drum_pad_listen = self.drum_pad_listen[key]
            for drum_pad in drum_pad_listen:
                if drum_pad != None:
                    ocb = drum_pad_listen[drum_pad]
                    if drum_pad.name_has_listener(ocb) == 1:
                        drum_pad.remove_name_listener(ocb)
    
        #self.oscServer.sendOSC('/live/track/removing_all_dev_listeners', 4)
        self.drum_pad_listen = {}

    def add_paramlistener(self, param, tid, did, pid, type):
        cb = lambda :self.param_changestate(param, tid, did, pid, type)
        
        if self.prlisten.has_key(param) != 1:
            param.add_value_listener(cb)
            self.prlisten[param] = cb

        

    def add_drum_pad_listener(self, drum_pad_listen, drum_pad, i, j, number_of_steps, indices):
        cb = lambda :self.drum_pad_changed(drum_pad, i, j, number_of_steps, indices)
        if drum_pad_listen.has_key(drum_pad) != 1:
            drum_pad.add_name_listener(cb)
            drum_pad_listen[drum_pad] = cb
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "ADDED DRUM PAD LISTENER")


    def add_drumpads_listener(self, device, i, j, number_of_steps, indices):
        cb = lambda :self.drum_pads_changed(device.drum_pads, i, j, number_of_steps, indices)
        if self.drum_pads_listen.has_key(device) != 1:
            device.add_drum_pads_listener(cb)
            self.drum_pads_listen[device] = cb


    def drum_pads_changed(self, drum_pads, i, j, number_of_steps, indices):
        #self.oscServer.sendOSC("/NSLOG_REPLACE", str("DRUM PADSSS CHANGED !!!!!!!11111"))

        drum_pads_tuple = [0, i, j, number_of_steps]
        for index in range(number_of_steps * 2):
            drum_pads_tuple.append(int(indices[index]))
        
        drum_pads_tuple.append(int(len(drum_pads)))

        for drum_pad in drum_pads:
            drum_pads_tuple.append(int(drum_pad.note))
            drum_pads_tuple.append(touchAbleUtils.repr3(drum_pad.name))
            drum_pads_tuple.append(int(drum_pad.mute))
            drum_pads_tuple.append(int(drum_pad.solo))
        self.oscServer.sendOSC("/track/device/drumpads", tuple(drum_pads_tuple))
    

    def drum_pad_changed(self, drum_pad, i, j, number_of_steps, indices):
        #self.oscServer.sendOSC("/NSLOG_REPLACE", str("DRUM PAD CHANGED !!!!!!!11111"))

        drum_pad_tuple = [0, i, j, number_of_steps]
        for index in range(number_of_steps * 2):
            drum_pad_tuple.append(int(indices[index]))
                
        drum_pad_tuple.append(int(drum_pad.note))
        drum_pad_tuple.append(touchAbleUtils.repr3(drum_pad.name))
        drum_pad_tuple.append(int(drum_pad.mute))
        drum_pad_tuple.append(int(drum_pad.solo))
        self.oscServer.sendOSC("/track/device/drumpad", tuple(drum_pad_tuple))


    
    def param_changestate(self, param, tid, did, pid, type, number_of_steps, indices):
        if type == 1:
            indis = [type, 0, did, pid, param.value, touchAbleUtils.repr3(param.__str__()), number_of_steps]
            for index in range(number_of_steps * 2):
                indis.append(int(indices[index]))
            indis.append(int(param.is_enabled))
            indis.append(int(param.automation_state))
            self.oscServer.sendOSC('/master/device/parameter', (tuple(indis)))
        elif type == 2:
            indis = [type, tid, did, pid, param.value, touchAbleUtils.repr3(param.__str__()), number_of_steps]
            for index in range(number_of_steps * 2):
                indis.append(int(indices[index]))
            indis.append(int(param.is_enabled))
            indis.append(int(param.automation_state))
            self.oscServer.sendOSC('/return/device/parameter', (tuple(indis)))
        else:
            indis = [type, tid, did, pid, param.value, touchAbleUtils.repr3(param.__str__()), number_of_steps]
            for index in range(number_of_steps * 2):
                indis.append(int(indices[index]))
            indis.append(int(param.is_enabled))
            indis.append(int(param.automation_state))
            self.oscServer.sendOSC('/track/device/parameter', (tuple(indis)))


    def add_devices_listener(self, track, tid, type):

        key = '%s.%s' % (type, tid)

        cb = lambda :self.devices_changed(track, tid, type)
        if self.devices_listen.has_key(key) != 1:
            track.add_devices_listener(cb)
            self.devices_listen[key] = cb



    def add_chain_devices_listener(self, track, tid, type, chain):
    
        key = '%s.%s' % (type, tid)
        chaindevicelisten = self.chaindevicelisten[key]
        
        cb = lambda :self.devices_changed(track, tid, type)
        if chaindevicelisten.has_key(chain) != 1:
            chain.add_devices_listener(cb)
            chaindevicelisten[chain] = cb


    def device_changestate(self):

        self.ta_logger("device_changestate",5)

        device = LiveUtils.getSong().appointed_device
        if device == None:
            return
        else:
            pass
        
        track = device.canonical_parent
        did = 0
        type = 0
        number_of_steps = 0
        indices = []

        while track.canonical_parent != LiveUtils.getSong():

            if number_of_steps % 2 != 0:
                indices.append(touchAbleUtils.tuple_idx(track.chains, device))
            else:
                indices.append(touchAbleUtils.tuple_idx(track.devices, device))
    

            number_of_steps = number_of_steps + 1
            
            device = track
            track = device.canonical_parent

        self.ta_logger("got canonical_parent device",4)


        if track.canonical_parent == LiveUtils.getSong():

            did = touchAbleUtils.tuple_idx(track.devices, device)
            tid = touchAbleUtils.tuple_idx(LiveUtils.getSong().tracks, track)
            type = 0

            if tid < 0:

                tid = touchAbleUtils.tuple_idx(LiveUtils.getSong().return_tracks, track)
                
                if tid >= 0:
                    type = 2
                else:
                    type = 1
                    tid = 0
        indis = [type, tid, did, int(number_of_steps/2)]

        for i in range(len(indices)):
            indis.append(int(indices[len(indices)-1-i]))
       
        self.oscServer.sendOSC("/selected_device", tuple(indis))
        self.ta_logger("sent selected device",4)

    
    def add_device_listeners(self):
        try:
            self.do_add_device_listeners(LiveUtils.getSong().tracks,0)
        except:
            self.error_log("DeviceListener: do_add_device_listeners 0 failed")
        try:
            self.do_add_device_listeners(LiveUtils.getSong().return_tracks,2)
        except:
            self.error_log("DeviceListener: do_add_device_listeners 2 failed")
        try:
            self.do_add_device_listeners([LiveUtils.getSong().master_track],1)
        except:
            self.error_log("DeviceListener: do_add_device_listeners 1 failed")
        try:
            self.add_app_device_listener()
        except:
            self.error_log("DeviceListener: add_app_device_listener failed")


        #self.oscServer.sendOSC('/track/adding_all_listeners', 2)

    def add_app_device_listener(self):
        self.rem_app_device_listener()
            
        if LiveUtils.getSong().appointed_device_has_listener(self.device_changestate) != 1:
            LiveUtils.getSong().add_appointed_device_listener(self.device_changestate)    

    def remove_devices_listener(self, track, tid, type):

        key = '%s.%s' % (type, tid)
        
        if self.devices_listen.has_key(key) == 1:
            ocb = self.devices_listen[key]
            if track.devices_has_listener(ocb) == 1:
                track.remove_devices_listener(ocb)
            del self.devices_listen[key]

        if self.chaindevicelisten.has_key(key) == 1:
                                                    
            chaindevicelisten = self.chaindevicelisten[key]
                                                    
            for pr in chaindevicelisten:
                if pr != None:
                    ocb = chaindevicelisten[pr]
                    if pr.devices_has_listener(ocb) == 1:
                        pr.remove_devices_listener(ocb)
            del self.chaindevicelisten[key]



    def devices_changed(self, track, tid, type):
                    
        message = "devices changed for track :" + str(tid) + " and type :" + str(type)
        self.ta_logger(message, 4)

        a = Live.Application.get_application().get_major_version()
        
        length_tracks = len(LiveUtils.getSong().tracks)
        for a_tid in range(length_tracks):
            atrack = LiveUtils.getSong().tracks[a_tid]
            if atrack == track:
                tid = a_tid
        
        self.oscServer.sendOSC("/devices_empty", (int(type), int(tid)))


        did = 0
        
        number_of_steps = 0
        i = 0
        indices = []
        
        for device in track.devices:
            
            lis = list(indices)

            self.touchAble.tACommon.send_update_for_device(device, track, tid, did, type, len(track.devices), number_of_steps, lis, -1)

            did = did+1

        self.oscServer.sendOSC('/devices_loaded', (int(type), int(tid)))
        self.add_device_listeners_for_track(track, int(tid), int(type))
    
