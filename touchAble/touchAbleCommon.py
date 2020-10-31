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

class touchAbleCommon:
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
        else:
            return

        self.mlcache = []
        self.mrcache = [] 
        self.mmcache = 0

        self.mlcache = [-3 for i in range(2000)]
        self.mrcache = [-3 for i in range(2000)]
        self.mmcache = -1


    def positions(self):
        tracks = LiveUtils.getSong().tracks
        pos = 0
        ps = 0
        if LiveUtils.getSong().is_playing != 4:
            #self.oscServer.sendOSC("/bundle/start", 1)
            for i in range(len(tracks)):
                track = tracks[i]
                if track.is_foldable != 1:
                    if track.playing_slot_index != -2:
                        if track.playing_slot_index != -1:
                            ps = track.playing_slot_index
                            clip = track.clip_slots[ps].clip
                            playing_pos = 0
                            pos = 0
                            try:
                                playing_pos = clip.playing_position
                                if clip.looping == 1:
                                    if clip.playing_position < clip.loop_start:
                                        #clip.looping = 0
                                        start = clip.loop_start
                                        end = clip.loop_end
                                        #clip.looping = 1
                                        pos = 1 - round((end - clip.playing_position) / end, 6)
                                            #pos = round((clip.loop_start - clip.playing_position) / (clip.loop_start - start), 3)
                                    else:
                                        pos = round((clip.playing_position - clip.loop_start) / (clip.loop_end - clip.loop_start), 6)

                                else:
                                    pos = round((clip.playing_position-clip.loop_start) / (clip.loop_end - clip.loop_start), 6)
                            except:
                                asddd = 1

                            self.oscServer.sendOSC('/clip/playing_position',(i, ps, pos, playing_pos))
                        else:
                            pass
                    else:
                        pass

                else:
                    pass
            #self.oscServer.sendOSC("/bundle/end", (1))

        else:
            pass

            


    def meters(self):
        #self.oscServer.sendOSC("/bundle/start", 1)
        tracks = LiveUtils.getSong().tracks
        vall = 0
        valr = 0
        for i in range (len(tracks)):
            track = tracks[i]
            if track.has_audio_output:
                vall = track.output_meter_left
                valr = track.output_meter_right
            else:
                vall = -1.0 * track.output_meter_level -1.0
                valr = 0
            
            vall = round(vall, 4)
            valr = round(valr, 4)
            sum = vall + valr
            if sum != self.mlcache[i]:
                self.oscServer.sendOSC('/track/meter',(i,vall, valr))
                self.mlcache[i] = sum
            else:
                pass
        #self.oscServer.sendOSC("/bundle/end", (1))


            

    def mastermeters(self):
        tracks = LiveUtils.getSong().return_tracks
        vall = LiveUtils.getSong().master_track.output_meter_left
        valr = LiveUtils.getSong().master_track.output_meter_right
        
        vall = round(vall, 4)
        valr = round(valr, 4)

        if vall != self.mmcache:
            self.oscServer.sendOSC('/master/meter',(vall, valr))
            if vall == 0:
                self.oscServer.sendOSC('/master/meter',(0.0000000001,0000000.1))   
            self.mmcache = vall                    
        i = 0
        for track in tracks:
            vall = track.output_meter_left
            valr = track.output_meter_right

            vall = round(vall, 4)
            valr = round(valr, 4)

            if vall != self.mrcache[i]:
                self.oscServer.sendOSC('/return/meter',(i, vall, valr))
                self.mrcache[i] = vall
            else:
                pass
            i = i+1

        
    def songtime_change(self):
        denom = LiveUtils.getSong().signature_denominator
        numer = LiveUtils.getSong().signature_numerator
        self.oscServer.sendOSC("/set/playing_position", (LiveUtils.getSong().current_song_time,float(numer),float(denom)))





    def send_update_for_device(self, device, track, tid, did, type, num, number_of_steps, indices, i):
        

        message = "send_update_for_device for track: " + str(tid) + " and device: " + str(device.name)
        self.ta_logger(message, 4)

        """
        try:
            self.expand_device(device)
            #message = "expand_device here failed for track: " + str(tid) + " and device: " + str(device.name)
            #self.ta_logger(message, 4)
        except:
            self.error_log("tochAbleCommon failed expanding:" + touchAbleUtils.repr2(device.name))
            pass
        """
        
        if i != -1:
            indices.append(int(i))
            number_of_steps = number_of_steps+1

        elif i == -1 and number_of_steps == 0:
            indic = []
            indices = list(indic)
        
        nm = touchAbleUtils.repr2(device.name)
        params = device.parameters
        onoff = params[0].value
        numParams = len(params)
        cnam = touchAbleUtils.repr2(device.class_name)


        tr = tid
        dev = did
        
        name = track.name
        devicename = device.name
        
        
        is_selected = 0
        
        if device == LiveUtils.getSong().appointed_device:
            is_selected = 1
        
        po = [type]
        po.append(int(tr))
        po.append(int(dev))
        
        
        po2 = [type]
        po2.append(int(tr))
        po2.append(int(dev))
        po2.append(touchAbleUtils.repr2(name))
        po2.append(touchAbleUtils.repr2(devicename))
        po2.append(int(is_selected))
        
        po.append(int(number_of_steps))
        po2.append(int(number_of_steps))



        po4 = [type]
        po4.append(int(tr))
        po4.append(int(dev))
        po4.append(int(number_of_steps))

        po5 = [type]
        po5.append(int(tr))
        po5.append(int(dev))
        po5.append(int(number_of_steps))


        for index in range(number_of_steps * 2):
            po.append(int(indices[index]))
            po2.append(int(indices[index]))
            po4.append(int(indices[index]))
            po5.append(int(indices[index]))

        for j in range(len(params)):
            po.append(params[j].min)
            po.append(params[j].max)
            po.append(params[j].is_quantized+1)
            po2.append(float(params[j].value))
            po2.append(touchAbleUtils.repr2(params[j].name))
            po2.append(touchAbleUtils.repr2(params[j].__str__()))
            po4.append(int(params[j].is_enabled))
            automation_state = 0
            if params[j].automation_state:
                automation_state = params[j].automation_state
            po4.append(int(automation_state))
            reset_value = -13337.0
            if params[j].is_quantized == 0:
                reset_value = float(params[j].default_value)
            po5.append(float(reset_value))
            
        try:
            can_have_chains = device.can_have_chains
        except:
            can_have_chains = 0
        try:
            can_have_drumpads = device.can_have_drum_pads and device.has_drum_pads and device.class_name == 'MultiSampler' or device.class_name == "DrumGroupDevice"
        except:
            can_have_drumpads = 0


        live_pointer = str(device._live_ptr)

        if type == 0:

            po3 = [type, tid, did, nm, onoff, int(num), numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))
            
            if can_have_drumpads or can_have_chains:
                po3.append(int(device.has_macro_mappings))
            
            po3.append(str(live_pointer))

            self.oscServer.sendOSC('/track/device', (tuple(po3)))
            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/track/device/parameters", tuple(po2))
            self.oscServer.sendOSC("/track/device/parameters/enabled", tuple(po4))
            self.oscServer.sendOSC("/track/device/parameters/default_value", tuple(po5))


            if can_have_drumpads:
                drum_pads_tuple = [type, tid, did, number_of_steps]
                for index in range(number_of_steps * 2):
                    drum_pads_tuple.append(int(indices[index]))
                
                drum_pads_tuple.append(int(len(device.drum_pads)))
                
                for drum_pad in device.drum_pads:

                    drum_pads_tuple.append(int(drum_pad.note))
                    drum_pads_tuple.append(touchAbleUtils.repr2(drum_pad.name))
                    drum_pads_tuple.append(int(drum_pad.mute))
                    drum_pads_tuple.append(int(drum_pad.solo))
                    #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("SENDING DRUMPAD"), touchAbleUtils.repr2(drum_pad.name)))

                self.oscServer.sendOSC("/track/device/drumpads", tuple(drum_pads_tuple))
                
        elif type == 2:
            
            po3 = [type, tid, did, nm, onoff, int(num), numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))
                   
            po3.append(live_pointer)

            self.oscServer.sendOSC('/return/device', (tuple(po3)))
            
            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/return/device/parameters", tuple(po2))
            self.oscServer.sendOSC("/return/device/parameters/enabled", tuple(po4))
        
        elif type == 1:
            po3 = [type, 0, did, nm, onoff, int(num), numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))

            po3.append(live_pointer)

            self.oscServer.sendOSC('/master/device', (tuple(po3)))
            
            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/master/device/parameters", tuple(po2))
            self.oscServer.sendOSC("/master/device/parameters/enabled", tuple(po4))

        if device.class_name == 'OriginalSimpler':
            try:
                self.touchAble.tAListener.simplerListener.update_simpler_parameters(device, track, tid, did, type , number_of_steps, indices)
            except:
                self.error_log("tochAbleCommon: update_simpler_parameters failed")


        a_version = Live.Application.get_application().get_major_version()
        
        if a_version >= 10:
            try:
                self.touchAble.tAListener.compressorListener.update_compressor_parameters(device, track, tid, did, type , number_of_steps, indices)
            except:
                self.error_log("tochAbleCommon: update_compressor_parameters failed")
            try:
                self.touchAble.tAListener.wavetableListener.update_wavetable_parameters(device, track, tid, did, type , number_of_steps, indices)
            except:
                self.error_log("tochAbleCommon: update_wavetable_parameters failed")
            try:
                self.touchAble.tAListener.pluginListener.update_plugin_parameters(device, track, tid, did, type , number_of_steps, indices)
            except:
                self.error_log("tochAbleCommon: update_plugin_parameters failed")



        if can_have_chains == 1:
            
            for chain_id in range(len(device.chains)):
                chain = device.chains[chain_id]
                
                
                indis = list(indices)
                indis.append(int(chain_id))
                
                po3 = [type, tid, did, touchAbleUtils.repr2(chain.name), number_of_steps]
                for index in range(number_of_steps * 2 + 1):
                    po3.append(int(indis[index]))
                
                self.oscServer.sendOSC('/device_chain', (tuple(po3)))
                
                
                for device_id in range(len(chain.devices)):
                    dev = chain.devices[device_id]
                    
                    lis = list(indis)
                    self.send_update_for_device(dev, track, tid, did, type, len(chain.devices), number_of_steps, lis, device_id)


    def expand_device(self, device):
                
        if device.class_name == 'OriginalSimpler':
            self.expand_simpler(device)
        elif device.class_name == 'MultiSampler':
            self.expand_multi_sampler(device)      

    def expand_simpler(self, device):
        expand_failed = 0
        try:
            device_parameters = device.parameters
            for parameter in device_parameters:
                if parameter.name == 'Pe On':
                    try:
                        old_value = parameter.value
                        if old_value == 0:
                            parameter.value = 1
                            parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set Pe On")
                        expand_failed = 1
                elif parameter.name == 'L On':
                    try:
                        old_value = parameter.value
                        if old_value == 0:
                            parameter.value = 1
                            parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set L On")
                        expand_failed = 1
                elif parameter.name == 'Fe On':
                    try:
                        old_value = parameter.value
                        if old_value == 0:
                            parameter.value = 1
                            parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set Fe On")
                        expand_failed = 1
                elif parameter.name == 'F On':
                    try:
                        old_value = parameter.value
                        if old_value == 0:
                            parameter.value = 1
                            parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set F On On")
                        expand_failed = 1
                else:
                    pass
        except:
            self.error_log("touchAbleCommon: expand device expand_simpler "+touchAbleUtils.repr2(device.name)+" failed to expand device parameter assignment")

        if expand_failed == 1:
            self.error_log("touchAbleCommon: expand device expand_simpler "+touchAbleUtils.repr2(device.name)+" failed failed at any step")
        elif expand_failed == 0:
            message = 'a message from hell'
            self.ta_logger("touchAbleCommon: expand device expand_simpler "+touchAbleUtils.repr2(device.name)+" succedded at every step", 4)


    def expand_multi_sampler(self, device):
        try:
            device_parameters = device.parameters
            for parameter in device_parameters:
    
                if parameter.name == 'Osc On':
        
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set Osc On")
                
                elif parameter.name == 'Pe On':
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set Pe On")
        
        
                elif parameter.name == 'Shaper On':
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set Shaper On")
                
                elif parameter.name == 'L 1 On':
                    
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set L 1 On")
            
                elif parameter.name == 'L 2 On':
                
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set L 2 On")
                
                elif parameter.name == 'L 3 On':
                    
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set L 3 On")
            
                elif parameter.name == 'Ae On':
                
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set Ae On")
                
                elif parameter.name == 'F On':
                    
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set F On")
            
                elif parameter.name == 'Fe On':
                
                    try:
                        old_value = parameter.value
                        parameter.value = 1
                        parameter.value = old_value
                    except:
                        self.error_log("touchAbleCommon: expand device "+touchAbleUtils.repr2(device.name)+" failed to set Fe On")
                
                else:
                    pass
        except:
            self.error_log("touchAbleCommon: expand device expand_multi_sampler "+touchAbleUtils.repr2(device.name)+" failed to set F On On")


