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



class WavetableListener:
    __doc__ = "Listener class adding Wavetable Listener for Live"


    wavetable_filter_routing_listener = defaultdict(dict)
    wavetable_modulation_matrix_listener = defaultdict(dict)
    wavetable_mono_poly_listener = defaultdict(dict)
    wavetable_oscillator_1_effect_listener = defaultdict(dict)
    wavetable_oscillator_1_wavetable_category_listener = defaultdict(dict)
    wavetable_oscillator_1_wavetable_index_listener = defaultdict(dict)
    wavetable_oscillator_1_wavetables_listener = defaultdict(dict)
    wavetable_oscillator_2_effect_listener = defaultdict(dict)
    wavetable_oscillator_2_wavetable_category_listener = defaultdict(dict)
    wavetable_oscillator_2_wavetable_index_listener = defaultdict(dict)
    wavetable_oscillator_2_wavetables_listener = defaultdict(dict)
    wavetable_poly_voices_listener = defaultdict(dict)
    wavetable_unison_mode_listener = defaultdict(dict)
    wavetable_unison_voice_count_listener = defaultdict(dict)
    wavetable_visible_modulation_target_names_listener = defaultdict(dict)

    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
        else:
            return

    def add_listener_for_wavetable(self, device, track, tid, did, type, num, number_of_steps, indices):



    
        cb1 = lambda :self.update_wavetable_filter_routing(device, track, tid, did, type , number_of_steps, indices)
        
        
        cb3 = lambda :self.update_wavetable_mono_poly(device, track, tid, did, type , number_of_steps, indices)
        
        cb4 = lambda :self.update_wavetable_oscillator_1_effect(device, track, tid, did, type , number_of_steps, indices)
        
        cb5 = lambda :self.update_wavetable_oscillator_1_wavetable_category(device, track, tid, did, type , number_of_steps, indices)

        cb7 = lambda :self.update_wavetable_oscillator_1_wavetables(device, track, tid, did, type , number_of_steps, indices)

        cb6 = lambda :self.update_wavetable_oscillator_1_wavetable_index(device, track, tid, did, type , number_of_steps, indices)
        
        cb8 = lambda :self.update_wavetable_oscillator_2_effect_enabled(device, track, tid, did, type , number_of_steps, indices)
        
        cb9 = lambda :self.update_wavetable_oscillator_2_wavetable_category_mode(device, track, tid, did, type , number_of_steps, indices)
        
        cb11 = lambda :self.update_wavetable_oscillator_2_wavetables(device, track, tid, did, type , number_of_steps, indices)

        cb10 = lambda :self.update_wavetable_oscillator_2_wavetable_index(device, track, tid, did, type , number_of_steps, indices)


        cb12 = lambda :self.update_wavetable_poly_voices(device, track, tid, did, type , number_of_steps, indices)
        
        cb13 = lambda :self.update_wavetable_unison_mode(device, track, tid, did, type , number_of_steps, indices)
        
        cb14 = lambda :self.update_wavetable_unison_voice_count(device, track, tid, did, type , number_of_steps, indices)
        
        cb15 = lambda :self.update_wavetable_visible_modulation_target_names(device, track, tid, did, type , number_of_steps, indices)
        
        cb2 = lambda :self.update_wavetable_modulation_matrix(device, track, tid, did, type , number_of_steps, indices)

        
        key = '%s.%s' % (type, tid)
        
        wavetable_filter_routing_listener  = self.wavetable_filter_routing_listener[key]
        wavetable_modulation_matrix_listener = self.wavetable_modulation_matrix_listener[key]
        wavetable_mono_poly_listener = self.wavetable_mono_poly_listener[key]
        wavetable_oscillator_1_effect_listener  = self.wavetable_oscillator_1_effect_listener[key]
        wavetable_oscillator_1_wavetable_category_listener = self.wavetable_oscillator_1_wavetable_category_listener[key]
        wavetable_oscillator_1_wavetable_index_listener = self.wavetable_oscillator_1_wavetable_index_listener[key]
        wavetable_oscillator_1_wavetables_listener  = self.wavetable_oscillator_1_wavetables_listener[key]
        wavetable_oscillator_2_effect_listener = self.wavetable_oscillator_2_effect_listener[key]
        wavetable_oscillator_2_wavetable_category_listener = self.wavetable_oscillator_2_wavetable_category_listener[key]
        wavetable_oscillator_2_wavetable_index_listener  = self.wavetable_oscillator_2_wavetable_index_listener[key]
        wavetable_oscillator_2_wavetables_listener = self.wavetable_oscillator_2_wavetables_listener[key]
        wavetable_poly_voices_listener = self.wavetable_poly_voices_listener[key]
        wavetable_unison_mode_listener = self.wavetable_unison_mode_listener[key]
        wavetable_unison_voice_count_listener  = self.wavetable_unison_voice_count_listener[key]
        wavetable_visible_modulation_target_names_listener = self.wavetable_visible_modulation_target_names_listener[key]
    
        wavetable = device
        
        self.update_oscillator_wavetable_categories(wavetable, track, tid, did, type , number_of_steps, indices)

        if wavetable_filter_routing_listener.has_key(device) != 1:
            #self.update_wavetable_filter_routing(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_filter_routing_listener(cb1)
            wavetable_filter_routing_listener[device] = cb1
        

        
        if wavetable_mono_poly_listener.has_key(device) != 1:
            #self.update_wavetable_mono_poly(device, track, tid, did, type , number_of_steps, indices)
            device.add_mono_poly_listener(cb3)
            wavetable_mono_poly_listener[device] = cb3
        
        if wavetable_oscillator_1_effect_listener.has_key(device) != 1:
            #self.update_wavetable_oscillator_1_effect(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_oscillator_1_effect_mode_listener(cb4)
            wavetable_oscillator_1_effect_listener[device] = cb4

        if wavetable_oscillator_1_wavetable_category_listener.has_key(device) != 1:
            #self.update_wavetable_oscillator_1_wavetable_category(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_oscillator_1_wavetable_category_listener(cb5)
            wavetable_oscillator_1_wavetable_category_listener[device] = cb5
        
        if wavetable_oscillator_1_wavetable_index_listener.has_key(device) != 1:
            #self.update_wavetable_oscillator_1_wavetable_index(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_oscillator_1_wavetable_index_listener(cb6)
            wavetable_oscillator_1_wavetable_index_listener[device] = cb6
        
        if wavetable_oscillator_1_wavetables_listener.has_key(device) != 1:
            #self.update_wavetable_oscillator_1_wavetables(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_oscillator_1_wavetables_listener(cb7)
            wavetable_oscillator_1_wavetables_listener[device] = cb7
        
        if wavetable_oscillator_2_effect_listener.has_key(device) != 1:
            #self.update_wavetable_oscillator_2_effect_enabled(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_oscillator_2_effect_mode_listener(cb8)
            wavetable_oscillator_2_effect_listener[device] = cb8

        if wavetable_oscillator_2_wavetable_category_listener.has_key(device) != 1:
            #self.update_wavetable_oscillator_2_wavetable_category_mode(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_oscillator_2_wavetable_category_listener(cb9)
            wavetable_oscillator_2_wavetable_category_listener[device] = cb9
    
        if wavetable_oscillator_2_wavetable_index_listener.has_key(device) != 1:
            #self.update_wavetable_oscillator_2_wavetable_index(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_oscillator_2_wavetable_index_listener(cb10)
            wavetable_oscillator_2_wavetable_index_listener[device] = cb10
        
        if wavetable_oscillator_2_wavetables_listener.has_key(device) != 1:
            #self.update_wavetable_oscillator_2_wavetables(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_oscillator_2_wavetables_listener(cb11)
            wavetable_oscillator_2_wavetables_listener[device] = cb11
        
        if wavetable_poly_voices_listener.has_key(device) != 1:
            #self.update_wavetable_poly_voices(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_poly_voices_listener(cb12)
            wavetable_poly_voices_listener[device] = cb12

        if wavetable_unison_mode_listener.has_key(device) != 1:
            #self.update_wavetable_unison_mode(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_unison_mode_listener(cb13)
            wavetable_unison_mode_listener[device] = cb13

        if wavetable_unison_voice_count_listener.has_key(device) != 1:
            #self.update_wavetable_unison_voice_count(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_unison_voice_count_listener(cb14)
            wavetable_unison_voice_count_listener[device] = cb14
    
        if wavetable_visible_modulation_target_names_listener.has_key(device) != 1:
            #self.update_wavetable_visible_modulation_target_names(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_visible_modulation_target_names_listener(cb15)
            wavetable_visible_modulation_target_names_listener[device] = cb15
                
        if wavetable_modulation_matrix_listener.has_key(device) != 1:
            #self.update_wavetable_modulation_matrix(wavetable, track, tid, did, type , number_of_steps, indices)
            device.add_modulation_matrix_changed_listener(cb2)
            wavetable_modulation_matrix_listener[device] = cb2



    def remove_wavetable_listeners_of_track(self, track, tid, type):
        key = '%s.%s' % (type, tid)

        if self.wavetable_filter_routing_listener.has_key(key) == 1:
            wavetable_filter_routing_listener = self.wavetable_filter_routing_listener[key]
            
            for pr in wavetable_filter_routing_listener:
                if pr != None:
                    ocb = wavetable_filter_routing_listener[pr]
                    try:
                        if pr.filter_routing_has_listener(ocb) == 1:
                            pr.remove_filter_routing_listener(ocb)
                    except:
                        self.oscServer.sendOSC("/NSLOG_REPLACE", "wavetable not found anymore or some shit")
        
            
            
            del self.wavetable_filter_routing_listener[key]

            
        if self.wavetable_modulation_matrix_listener.has_key(key) == 1:
            wavetable_modulation_matrix_listener = self.wavetable_modulation_matrix_listener[key]
            
            for pr in wavetable_modulation_matrix_listener:
                if pr != None:
                    ocb = wavetable_modulation_matrix_listener[pr]
                    if pr.modulation_matrix_changed_has_listener(ocb) == 1:
                        pr.remove_modulation_matrix_changed_listener(ocb)
            
            del self.wavetable_modulation_matrix_listener[key]

        if self.wavetable_mono_poly_listener.has_key(key) == 1:
            wavetable_mono_poly_listener = self.wavetable_mono_poly_listener[key]
    
            for pr in wavetable_mono_poly_listener:
                if pr != None:
                    ocb = wavetable_mono_poly_listener[pr]
                    if pr.mono_poly_has_listener(ocb) == 1:
                        pr.remove_mono_poly_listener(ocb)
            
            del self.wavetable_mono_poly_listener[key]

        if self.wavetable_oscillator_1_effect_listener.has_key(key) == 1:
            wavetable_oscillator_1_effect_listener = self.wavetable_oscillator_1_effect_listener[key]
    
            for pr in wavetable_oscillator_1_effect_listener:
                if pr != None:
                    ocb = wavetable_oscillator_1_effect_listener[pr]
                    if pr.oscillator_1_effect_mode_has_listener(ocb) == 1:
                        pr.remove_oscillator_1_effect_mode_listener(ocb)
            
            del self.wavetable_oscillator_1_effect_listener[key]

        if self.wavetable_oscillator_1_wavetable_category_listener.has_key(key) == 1:
            wavetable_oscillator_1_wavetable_category_listener = self.wavetable_oscillator_1_wavetable_category_listener[key]
    
            for pr in wavetable_oscillator_1_wavetable_category_listener:
                if pr != None:
                    ocb = wavetable_oscillator_1_wavetable_category_listener[pr]
                    if pr.oscillator_1_wavetable_category_has_listener(ocb) == 1:
                        pr.remove_oscillator_1_wavetable_category_listener(ocb)
            
            del self.wavetable_oscillator_1_wavetable_category_listener[key]



        if self.wavetable_oscillator_1_wavetable_index_listener.has_key(key) == 1:
            wavetable_oscillator_1_wavetable_index_listener = self.wavetable_oscillator_1_wavetable_index_listener[key]
    
            for pr in wavetable_oscillator_1_wavetable_index_listener:
                if pr != None:
                    ocb = wavetable_oscillator_1_wavetable_index_listener[pr]
                    if pr.oscillator_1_wavetable_index_has_listener(ocb) == 1:
                        pr.remove_oscillator_1_wavetable_index_listener(ocb)
            
            del self.wavetable_oscillator_1_wavetable_index_listener[key]



        if self.wavetable_oscillator_1_wavetables_listener.has_key(key) == 1:
            wavetable_oscillator_1_wavetables_listener = self.wavetable_oscillator_1_wavetables_listener[key]

            for pr in wavetable_oscillator_1_wavetables_listener:
                if pr != None:
                    ocb = wavetable_oscillator_1_wavetables_listener[pr]
                    if pr.oscillator_1_wavetables_has_listener(ocb) == 1:
                        pr.remove_oscillator_1_wavetables_listener(ocb)
            
            del self.wavetable_oscillator_1_wavetables_listener[key]

        if self.wavetable_oscillator_2_effect_listener.has_key(key) == 1:
            wavetable_oscillator_2_effect_listener = self.wavetable_oscillator_1_effect_listener[key]
    
            for pr in wavetable_oscillator_2_effect_listener:
                if pr != None:
                    ocb = wavetable_oscillator_2_effect_listener[pr]
                    if pr.oscillator_2_effect_mode_has_listener(ocb) == 1:
                        pr.remove_oscillator_2_effect_mode_listener(ocb)
            
            del self.wavetable_oscillator_2_effect_listener[key]
        
        if self.wavetable_oscillator_2_wavetable_category_listener.has_key(key) == 1:
            wavetable_oscillator_2_wavetable_category_listener = self.wavetable_oscillator_2_wavetable_category_listener[key]
            
            for pr in wavetable_oscillator_2_wavetable_category_listener:
                if pr != None:
                    ocb = wavetable_oscillator_2_wavetable_category_listener[pr]
                    if pr.oscillator_2_wavetable_category_has_listener(ocb) == 1:
                        pr.remove_oscillator_2_wavetable_category_listener(ocb)
            
            del self.wavetable_oscillator_2_wavetable_category_listener[key]


        if self.wavetable_oscillator_2_wavetable_index_listener.has_key(key) == 1:
            wavetable_oscillator_2_wavetable_index_listener = self.wavetable_oscillator_2_wavetable_index_listener[key]
        
            for pr in wavetable_oscillator_2_wavetable_index_listener:
                if pr != None:
                    ocb = wavetable_oscillator_2_wavetable_index_listener[pr]
                    if pr.oscillator_2_wavetable_index_has_listener(ocb) == 1:
                        pr.remove_oscillator_2_wavetable_index_listener(ocb)
            
            del self.wavetable_oscillator_2_wavetable_index_listener[key]
        
        
        if self.wavetable_oscillator_2_wavetables_listener.has_key(key) == 1:
            wavetable_oscillator_2_wavetables_listener = self.wavetable_oscillator_2_wavetables_listener[key]
            
            for pr in wavetable_oscillator_2_wavetables_listener:
                if pr != None:
                    ocb = wavetable_oscillator_2_wavetables_listener[pr]
                    if pr.oscillator_2_wavetables_has_listener(ocb) == 1:
                        pr.remove_oscillator_2_wavetables_listener(ocb)

            del self.wavetable_oscillator_2_wavetables_listener[key]

        
        if self.wavetable_poly_voices_listener.has_key(key) == 1:
            wavetable_poly_voices_listener = self.wavetable_poly_voices_listener[key]
            
            for pr in wavetable_poly_voices_listener:
                if pr != None:
                    ocb = wavetable_poly_voices_listener[pr]
                    if pr.poly_voices_has_listener(ocb) == 1:
                        pr.remove_poly_voices_listener(ocb)
            
            del self.wavetable_poly_voices_listener[key]
            
            
        if self.wavetable_unison_mode_listener.has_key(key) == 1:
            wavetable_unison_mode_listener = self.wavetable_unison_mode_listener[key]
            
            for pr in wavetable_unison_mode_listener:
                if pr != None:
                    ocb = wavetable_unison_mode_listener[pr]
                    if pr.unison_mode_has_listener(ocb) == 1:
                        pr.remove_unison_mode_listener(ocb)

            del self.wavetable_unison_mode_listener[key]
        

        if self.wavetable_unison_voice_count_listener.has_key(key) == 1:
            wavetable_unison_voice_count_listener = self.wavetable_unison_voice_count_listener[key]
            
            for pr in wavetable_unison_voice_count_listener:
                if pr != None:
                    ocb = wavetable_unison_voice_count_listener[pr]
                    if pr.unison_voice_count_has_listener(ocb) == 1:
                        pr.remove_unison_voice_count_listener(ocb)
            
            del self.wavetable_unison_voice_count_listener[key]            
            
        
        if self.wavetable_visible_modulation_target_names_listener.has_key(key) == 1:
            wavetable_visible_modulation_target_names_listener = self.wavetable_visible_modulation_target_names_listener[key]
            
            for pr in wavetable_visible_modulation_target_names_listener:
                if pr != None:
                    ocb = wavetable_visible_modulation_target_names_listener[pr]
                    if pr.visible_modulation_target_names_has_listener(ocb) == 1:
                        pr.remove_visible_modulation_target_names_listener(ocb)

            del self.wavetable_visible_modulation_target_names_listener[key]



    def update_wavetable_parameters(self,device, track, tid, did, type , number_of_steps, indices):

        if device.class_name == 'InstrumentVector':
            self.update_oscillator_wavetable_categories(device, track, tid, did, type , number_of_steps, indices)

            self.update_wavetable_filter_routing(device, track, tid, did, type , number_of_steps, indices)
                
            self.update_wavetable_mono_poly(device, track, tid, did, type , number_of_steps, indices)
        
            self.update_wavetable_oscillator_1_effect(device, track, tid, did, type , number_of_steps, indices)
        
            self.update_wavetable_oscillator_1_wavetable_category(device, track, tid, did, type , number_of_steps, indices)

            self.update_wavetable_oscillator_1_wavetables(device, track, tid, did, type , number_of_steps, indices)

            self.update_wavetable_oscillator_1_wavetable_index(device, track, tid, did, type , number_of_steps, indices)
        
            self.update_wavetable_oscillator_2_effect_enabled(device, track, tid, did, type , number_of_steps, indices)
        
            self.update_wavetable_oscillator_2_wavetable_category_mode(device, track, tid, did, type , number_of_steps, indices)

            self.update_wavetable_oscillator_2_wavetables(device, track, tid, did, type , number_of_steps, indices)

            self.update_wavetable_oscillator_2_wavetable_index(device, track, tid, did, type , number_of_steps, indices)
        
            self.update_wavetable_poly_voices(device, track, tid, did, type , number_of_steps, indices)
        
            self.update_wavetable_unison_mode(device, track, tid, did, type , number_of_steps, indices)
        
            self.update_wavetable_unison_voice_count(device, track, tid, did, type , number_of_steps, indices)
        
            self.update_wavetable_visible_modulation_target_names(device, track, tid, did, type , number_of_steps, indices)


    def update_oscillator_wavetable_categories(self, device, track, tid, did, type , number_of_steps, indices):

        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))

        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        play_pos_data.append(int(len(device.oscillator_wavetable_categories)))

        
        for index in range(len(device.oscillator_wavetable_categories)):
            filter_routing = device.oscillator_wavetable_categories[index]
            play_pos_data.append(touchAbleUtils.repr3(filter_routing))
        
        self.oscServer.sendOSC("/device/wavetable/update_oscillator_wavetable_categories", play_pos_data)


    def update_wavetable_filter_routing(self, device, track, tid, did, type , number_of_steps, indices):
    
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
    
        filter_routing = device.filter_routing
        play_pos_data.append(int(filter_routing))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_filter_routing", play_pos_data)


    

    def update_wavetable_modulation_matrix(self, device, track, tid, did, type , number_of_steps, indices):
    
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        

        play_pos_data.append(int(len(device.visible_modulation_target_names) * 5))
        
        for index in range(len(device.visible_modulation_target_names)):
            for index2 in range(5):
                play_pos_data.append(float(device.get_modulation_value(index,index2)))
            

        self.oscServer.sendOSC("/device/wavetable/update_wavetable_modulation_matrix", play_pos_data)


    def update_wavetable_mono_poly(self, device, track, tid, did, type , number_of_steps, indices):
    
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
    
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        mono_poly = device.mono_poly
        play_pos_data.append(int(mono_poly))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_mono_poly", play_pos_data)


    def update_wavetable_oscillator_1_effect(self, device, track, tid, did, type , number_of_steps, indices):
        
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        oscillator_1_effect_mode = device.oscillator_1_effect_mode
        play_pos_data.append(int(oscillator_1_effect_mode))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_oscillator_1_effect", play_pos_data)


    def update_wavetable_oscillator_1_wavetable_category(self, device, track, tid, did, type , number_of_steps, indices):
    
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
    
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        oscillator_1_wavetable_category = device.oscillator_1_wavetable_category
        play_pos_data.append(int(oscillator_1_wavetable_category))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_oscillator_1_wavetable_category", play_pos_data)
            


    def update_wavetable_oscillator_1_wavetable_index(self, device, track, tid, did, type , number_of_steps, indices):
        
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        oscillator_1_wavetable_index = device.oscillator_1_wavetable_index
        play_pos_data.append(int(oscillator_1_wavetable_index))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_oscillator_1_wavetable_index", play_pos_data)



    def update_wavetable_oscillator_1_wavetables(self, device, track, tid, did, type , number_of_steps, indices):
    
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
    
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))

        play_pos_data.append(int(len(device.oscillator_1_wavetables)))

        for index in range(len(device.oscillator_1_wavetables)):
            filter_routing = device.oscillator_1_wavetables[index]
            play_pos_data.append(touchAbleUtils.repr3(filter_routing))

        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_oscillator_1_wavetables", play_pos_data)

    
    def update_wavetable_oscillator_2_effect_enabled(self, device, track, tid, did, type , number_of_steps, indices):
        
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        oscillator_2_effect_mode = device.oscillator_2_effect_mode
        play_pos_data.append(int(oscillator_2_effect_mode))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_oscillator_2_effect_enabled", play_pos_data)


    def update_wavetable_oscillator_2_wavetable_category_mode(self, device, track, tid, did, type , number_of_steps, indices):
    
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
    
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        oscillator_2_wavetable_category = device.oscillator_2_wavetable_category
        play_pos_data.append(int(oscillator_2_wavetable_category))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_oscillator_2_wavetable_category_mode", play_pos_data)



    def update_wavetable_oscillator_2_wavetable_index(self, device, track, tid, did, type , number_of_steps, indices):
        
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        oscillator_2_wavetable_index = device.oscillator_2_wavetable_index
        play_pos_data.append(int(oscillator_2_wavetable_index))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_oscillator_2_wavetable_index", play_pos_data)


    def update_wavetable_oscillator_2_wavetables(self, device, track, tid, did, type , number_of_steps, indices):
    
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
    
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        play_pos_data.append(int(len(device.oscillator_2_wavetables)))

        for index in range(len(device.oscillator_2_wavetables)):
            filter_routing = device.oscillator_2_wavetables[index]
            play_pos_data.append(touchAbleUtils.repr3(filter_routing))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_oscillator_2_wavetables", play_pos_data)

    
    def update_wavetable_poly_voices(self, device, track, tid, did, type , number_of_steps, indices):
        
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        poly_voices = device.poly_voices
        play_pos_data.append(int(poly_voices))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_poly_voices", play_pos_data)





    def update_wavetable_unison_mode(self, device, track, tid, did, type , number_of_steps, indices):
        
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        unison_mode = device.unison_mode
        play_pos_data.append(int(unison_mode))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_unison_mode", play_pos_data)



    def update_wavetable_unison_voice_count(self, device, track, tid, did, type , number_of_steps, indices):
    
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))
    
        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))
        
        unison_voice_count = device.unison_voice_count
        play_pos_data.append(int(unison_voice_count))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_unison_voice_count", play_pos_data)


    def update_wavetable_visible_modulation_target_names(self, device, track, tid, did, type , number_of_steps, indices):
        
        play_pos_data = [int(type)]
        play_pos_data.append(int(tid))
        play_pos_data.append(int(did))
        play_pos_data.append(int(number_of_steps))

        for index in range(number_of_steps * 2):
            play_pos_data.append(int(indices[index]))

        play_pos_data.append(int(len(device.visible_modulation_target_names)))

        for index in range(len(device.visible_modulation_target_names)):
            filter_routing = device.visible_modulation_target_names[index]
            play_pos_data.append(touchAbleUtils.repr3(filter_routing))
        
        self.oscServer.sendOSC("/device/wavetable/update_wavetable_visible_modulation_target_names", play_pos_data)
        self.update_wavetable_modulation_matrix(device, track, tid, did, type , number_of_steps, indices)





