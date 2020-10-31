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

class WavetableCallbacks:
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


        self.callbackManager.add(self.set_filter_routing, "/device/wavetable/set_filter_routing")
        self.callbackManager.add(self.set_mono_poly, "/device/wavetable/set_mono_poly")
        self.callbackManager.add(self.set_oscillator_1_effect, "/device/wavetable/set_oscillator_1_effect")
        self.callbackManager.add(self.set_oscillator_1_wavetable_category, "/device/wavetable/set_oscillator_1_wavetable_category")
        self.callbackManager.add(self.set_oscillator_1_wavetable_index, "/device/wavetable/set_oscillator_1_wavetable_index")
        self.callbackManager.add(self.set_oscillator_2_effect, "/device/wavetable/set_oscillator_2_effect")
        self.callbackManager.add(self.set_oscillator_2_wavetable_category, "/device/wavetable/set_oscillator_2_wavetable_category")
        self.callbackManager.add(self.set_oscillator_2_wavetable_index, "/device/wavetable/set_oscillator_2_wavetable_index")
        self.callbackManager.add(self.set_poly_voices, "/device/wavetable/set_poly_voices")
        self.callbackManager.add(self.set_unison_mode, "/device/wavetable/set_unison_mode")
        self.callbackManager.add(self.set_unison_voice_count, "/device/wavetable/set_unison_voice_count")
        self.callbackManager.add(self.set_modulation_value, "/device/wavetable/set_modulation_value")
        self.callbackManager.add(self.get_modulation_value, "/device/wavetable/get_modulation_value")
        self.callbackManager.add(self.get_modulation_targe_parameter_name, "/device/wavetable/get_modulation_targe_parameter_name")
        self.callbackManager.add(self.add_parameter_to_modulation, "/device/wavetable/add_parameter_to_modulation")
        self.callbackManager.add(self.get_modulation_matrix, "/device/wavetable/get_modulation_matrix")


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

    def set_filter_routing(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        filter_routing = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.filter_routing = filter_routing

    def set_mono_poly(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        mono_poly = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.mono_poly = mono_poly


    def set_oscillator_1_effect(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        effect_mode = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.oscillator_1_effect_mode = effect_mode



    def set_oscillator_1_wavetable_category(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        oscillator_1_wavetable_category = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.oscillator_1_wavetable_category = oscillator_1_wavetable_category

    def set_oscillator_1_wavetable_index(self, msg):
    

        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        oscillator_1_wavetable_index = msg[new_index]

        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.oscillator_1_wavetable_index = oscillator_1_wavetable_index


    def set_oscillator_2_effect(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        effect_mode = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.oscillator_2_effect_mode = effect_mode



    def set_oscillator_2_wavetable_category(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        oscillator_2_wavetable_category = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.oscillator_2_wavetable_category = oscillator_2_wavetable_category

    def set_oscillator_2_wavetable_index(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        oscillator_2_wavetable_index = msg[new_index]
        a_version = Live.Application.get_application().get_major_version()

        if device.class_name == 'InstrumentVector' and a_version >= 10:
            wavetable = device
            wavetable.oscillator_2_wavetable_index = oscillator_2_wavetable_index

    def set_input_routing_channel(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        input_routing_channel = msg[new_index]
        a_version = Live.Application.get_application().get_major_version()

        if device.class_name == 'Compressor2' and a_version >= 10:
            compressor = device
            compressor.input_routing_channel = compressor.available_input_routing_channels[input_routing_channel]

    def set_input_routing_type(self, msg):
    

        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        input_routing_type = msg[new_index]
        a_version = Live.Application.get_application().get_major_version()
        if device.class_name == 'Compressor2' and a_version >= 10:
            compressor = device
            compressor.input_routing_type = compressor.available_input_routing_types[input_routing_type]

    def set_poly_voices(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        poly_voices = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.poly_voices = poly_voices


    def set_unison_mode(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        unison_mode = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.unison_mode = unison_mode

    def set_unison_voice_count(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        unison_voice_count = msg[new_index]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.unison_voice_count = unison_voice_count


    def set_modulation_value(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        target = msg[new_index]
        source = msg[new_index + 1]
        value = msg[new_index + 2]

        if device.class_name == 'InstrumentVector':
            wavetable = device
            wavetable.set_modulation_value(target, source, value)


    def get_modulation_value(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        target = msg[new_index]
        source = msg[new_index + 1]
    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            mod_val = wavetable.get_modulation_value(target,source)
        
            play_pos_data = [int(type)]
            play_pos_data.append(int(tid))
            play_pos_data.append(int(did))
            play_pos_data.append(int(number_of_steps))
        
            for index in range(number_of_steps * 2):
                play_pos_data.append(int(indices[index]))
        
            play_pos_data.append(float(mod_val))
        
            self.oscServer.sendOSC("/device/wavetable/set_modulation_value", play_pos_data)


    def get_modulation_targe_parameter_name(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        unison_voice_count = msg[new_index]
        target = msg[new_index]

        if device.class_name == 'InstrumentVector':
            wavetable = device
            mod_name = wavetable.get_modulation_target_parameter_name(target)


            play_pos_data = [int(type)]
            play_pos_data.append(int(tid))
            play_pos_data.append(int(did))
            play_pos_data.append(int(number_of_steps))
    
            for index in range(number_of_steps * 2):
                play_pos_data.append(int(indices[index]))
            
            play_pos_data.append(touchAbleUtils.repr3(mod_name))
        
            self.oscServer.sendOSC("/device/wavetable/set_modulation_targe_parameter_name", play_pos_data)

    def add_parameter_to_modulation(self, msg):
    
    
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        parameter_inx = msg[new_index]

    
        if device.class_name == 'InstrumentVector':
            wavetable = device
            parameter = wavetable.parameters[parameter_inx]
            wavetable.add_parameter_to_modulation_matrix(parameter)

    def get_modulation_matrix(self,msg):
            
        
        device = self.get_device_for_message(msg)
        number_of_steps = msg[5]
        new_index = 6+(number_of_steps)*2
        target = msg[new_index]
        source = msg[new_index + 1]
        
        if device.class_name == 'InstrumentVector':
            wavetable = device
            mod_val = wavetable.get_modulation_value(target,source)
            
            play_pos_data = [int(type)]
            play_pos_data.append(int(tid))
            play_pos_data.append(int(did))
            play_pos_data.append(int(number_of_steps))
            
            for index in range(number_of_steps * 2):
                play_pos_data.append(int(indices[index]))
        
            play_pos_data.append(float(mod_val))
    
            self.oscServer.sendOSC("/device/wavetable/set_modulation_value", play_pos_data)



