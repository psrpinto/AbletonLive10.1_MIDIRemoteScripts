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

class ClipCallbacks:
    # LMH

    noteBuffers = defaultdict(list)

    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
            self.error_log = touchAble.error_log
            self.ta_logger = touchAble.ta_logger
            self.error_logger = touchAble.error_logger
            self.noteListeners = touchAble.tAListener.clipListener.noteListeners
            self.clipListener = touchAble.tAListener.clipListener
            self.tA_log = touchAble.tA_log
        else:
            return

        self.callbackManager.add(self.setClipNotes, "/clip/set_notes")
        self.callbackManager.add(self.duplicateClipTo, "/clip/duplicate_to")
        self.callbackManager.add(self.createClip, "/clip/create")
        self.callbackManager.add(self.deleteClip, "/clip/delete")
        self.callbackManager.add(self.duplicateClip, "/clip/duplicate")
        self.callbackManager.add(self.loopclipCB, "/loopclip")
        self.callbackManager.add(self.quantizeclipCB, "/quantizeclip")
        self.callbackManager.add(self.renameclipCB, "/renameclip")
        self.callbackManager.add(self.loopInfo, "/clip/loop_info")
        self.callbackManager.add(self.playClipCB, "/live/play/clip")
        self.callbackManager.add(self.changeGain, "/clip/gain")
        self.callbackManager.add(self.changePlayingPosition, "/clip/playing_position")
        self.callbackManager.add(self.convertToSimpler, "/converttosimpler")
        self.callbackManager.add(self.toggleStopButton, "/clip/has_stop_button")
        self.callbackManager.add(self.clipstuff, "/clipstuff")
        self.callbackManager.add(self.loopStateCB, "/live/clip/loopstate")
        self.callbackManager.add(self.loopStateCB, "/live/clip/loopstate_id")
        self.callbackManager.add(self.pitchCB, "/live/pitch")
        self.callbackManager.add(self.viewClipCB, "/live/clip/view")
        self.callbackManager.add(self.detailViewCB, "/live/detail/view")
        self.callbackManager.add(self.muteclipCB, "/muteclip")

        self.callbackManager.add(self.clipInsertStepAutomation, "/clip/insert_automation")
        self.callbackManager.add(self.clipInsertStepAutomationMixer, "/clip/insert_automation_mixer")
        self.callbackManager.add(self.clipReqAutomation, "/clip/request_automation")
        self.callbackManager.add(self.clipClearAutomation, "/clip/clear_automation")
        self.callbackManager.add(self.clipClearAutomationMixer, "/clip/clear_automation_mixer")
        self.callbackManager.add(self.clipReqAutomationMixer, "/clip/request_automation_mixer")

        self.callbackManager.add(self.playClipSlotCB, "/live/play/clipslot")
        self.callbackManager.add(self.releaseClipSlotCB, "/live/release/clipslot")


        self.callbackManager.add(self.rammodeclipCB, "/live/clip/ram_mode")
        self.callbackManager.add(self.warpmodeclipCB, "/live/clip/warp_mode")
        self.callbackManager.add(self.warpingCB, "/live/clip/warping")

        self.callbackManager.add(self.colorindexclipCB, "/live/clip/color_index")

        self.callbackManager.add(self.clipstartposCB, "/clipstart")
        self.callbackManager.add(self.clipendposCB, "/clipend")

        self.callbackManager.add(self.startposCB, "/loopstart")
        self.callbackManager.add(self.endposCB, "/loopend")

        self.callbackManager.add(self.changeMarkerStartCB, "/markerstart")
        self.callbackManager.add(self.changeMarkerEndCB, "/markerend")
        

        self.callbackManager.add(self.pitchcoarseCB, "/pitch")
        self.callbackManager.add(self.detuneCB, "/detune")


        self.callbackManager.add(self.clipQuantization, "/clip/view/set_quantization")
        self.callbackManager.add(self.clipCrop, "/clip/crop")
        self.callbackManager.add(self.clipIsTriplet, "/clip/view/set_is_triplet")
        self.callbackManager.add(self.clipSelected, "/clip/clip_selected")
        self.callbackManager.add(self.backFromClip, "/clip/clip_deselected")
        self.callbackManager.add(self.setNoteVelocity, "/clip/set_note_velocity")
        self.callbackManager.add(self.addNote, "/clip/add_note2")
        self.callbackManager.add(self.addNotes, "/clip/add_notes2")
        self.callbackManager.add(self.updateNote, "/clip/update_note")
        self.callbackManager.add(self.updateNoteVelocity, "/clip/update_note_property")
        self.callbackManager.add(self.removeNote, "/clip/remove_note")
        self.callbackManager.add(self.removeNotes, "/clip/remove_notes")
        self.callbackManager.add(self.stretchNotes, "/clip/stretch_notes")
        self.callbackManager.add(self.clearNoteBuffer, "/clip/clear_notes")
        self.callbackManager.add(self.addNotesToBuffer, "/clip/add_notes")
        self.callbackManager.add(self.replaceCurrentNotesWithBuffer, "/clip/replace_notes")

        self.callbackManager.add(self.jumpForwardCB, "/jumpForward")
        self.callbackManager.add(self.jumpBackwardCB, "/jumpBackward")
        self.callbackManager.add(self.jumpLoopForward, "/jumpLoopForward")
        self.callbackManager.add(self.jumpLoopBackward, "/jumpLoopBackward")

        self.callbackManager.add(self.keepLoop, "/keepLoop")
        self.callbackManager.add(self.clearHiddenLoops, "/clearLoops")
        self.callbackManager.add(self.getActiveLoops, "/getLoops")
        self.callbackManager.add(self.changeLoopCB, "/loopChange")
        self.callbackManager.add(self.clip_loopstats2, "/get/clip/loopstats")
        self.callbackManager.add(self.request_loop_data, "/clip/request_loop_data")

    def setClipNotes(self, msg):
        track = msg[2]
        scene = msg[3]
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
        
        clip.select_all_notes()
        newClipNotes = []
        
        noteCount = (len(msg)-4)/5

        newNotes = []
        for i in range(noteCount):
            noteDescription = []
            ind = 4 + (i*5)
            pitch = msg[(ind+0)]
            time = msg[(ind+1)]
            length = msg[(ind+2)]
            velocity = msg[(ind+3)]
            mute = msg[(ind+4)]

            noteDescription.append(int(pitch))
            noteDescription.append(float(time))
            noteDescription.append(float(length))
            noteDescription.append(float(velocity))
            noteDescription.append(bool(mute))            

            newClipNotes.append(noteDescription)

            
        clip.replace_selected_notes(tuple(newClipNotes))
        clip.deselect_all_notes()

    def duplicateClipTo(self, msg):
        track = msg[2]
        scene = msg[3]
        
        
        target_track = msg[4]
        target_scene = msg[5]

        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
        target_clipSlot = LiveUtils.getSong().tracks[target_track].clip_slots[target_scene]

        clipSlot.duplicate_clip_to(target_clipSlot)

    def createClip(self, msg):
        track = msg[2]
        scene = msg[3]
        length = msg[4]
        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
        clipSlot.create_clip(float(length))
        if clipSlot.has_clip != true and track.is_midi_track == true:
            clipSlot.create_clip(float(length))

    
    def deleteClip(self, msg):
        track = msg[2]
        scene = msg[3]
        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
        clipSlot.delete_clip()
        
    
    def duplicateClip(self, msg):
        track = msg[2]
        scene = msg[3]
        track = LiveUtils.getTrack(track)
        track.duplicate_clip_slot(scene)


    def loopclipCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        looping = msg[4]
        LiveUtils.getClip(trackNumber, clipNumber).looping = looping
    
    def quantizeclipCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        quantize = msg[4]
        quantization = msg[5]
        LiveUtils.getClip(trackNumber, clipNumber).quantize(int(quantization),1)

    def renameclipCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        new_name = msg[4]
        LiveUtils.getClip(trackNumber, clipNumber).name = new_name

    def loopInfo(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        clip = LiveUtils.getClip(trackNumber, clipNumber)

        looping = clip.looping
        loop_start = 0
        loop_end = 0
        start = 0
        end = 0
        
        if looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
            clip.looping = 0

    def playClipCB(self, msg):
        """Called when a /live/play/clip message is received.

        Messages:
        /live/play/clip     (int track, int clip)   Launches clip number clip in track number track
        """
        if len(msg) == 4:
            track = msg[2]
            clip = msg[3]
            LiveUtils.launchClip(track, clip)

    def changeGain(self, msg):
        

        track = msg[2]
        scene = msg[3]
        gain = msg[4]

        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]

        clip = clipSlot.clip
        gain_str = ''
        try:
            clip.gain = gain
            gain_str = touchAbleUtils.repr2(clip.gain_display_string)
            self.oscServer.sendOSC("/clip/gain", (int(track), int(scene), gain_str))

        except:
            self.error_log("ClippCallbacks: change gain failed")
            pass

    def changePlayingPosition(self, msg):
    
    
        track = msg[2]
        scene = msg[3]
        playing_position = msg[4]
        
        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
        
        clip = clipSlot.clip
        try:
            clip.move_playing_pos(playing_position)
        
        except:
            self.error_log("ClippCallbacks: changePlayingPosition failed")
            pass


    def convertToSimpler(self, msg):

        track = msg[2]
        scene = msg[3]
    
        clip = LiveUtils.getClip(track, scene)

        Live.Conversions.create_midi_track_with_simpler(LiveUtils.getSong(), clip)

    def toggleStopButton(self, msg):
        
        track = msg[2]
        scene = msg[3]

        has_stop_button = msg[4]
        
        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
        clipSlot.has_stop_button = int(has_stop_button)

    def clipstuff(self, msg):
        self.ta_logger("clipstuff",5)
        trackNumber = msg[2]
        clipNumber = msg[3]



        self.ta_logger("clipstuff get clip",4)
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        if clip != None:
            nm = clip.name
            pitch_coarse = 0
            pitch_fine = 0
            is_audio_clip = 0
            warping = 0
            gain = 2
            gain_str = ''

            if clip.is_audio_clip:
                pitch_coarse = clip.pitch_coarse
                pitch_fine = clip.pitch_fine
                warping = clip.warping
                is_audio_clip = 1
                


                try:
                    gain = clip.gain
                    gain_str = clip.gain_display_string
                    self.touchAble.tAListener.clipListener.clip_gain_changed(clip,trackNumber,clipNumber)
                    self.touchAble.tAListener.clipListener.clip_gain_str_changed(clip,trackNumber,clipNumber)
                    self.touchAble.tAListener.clipListener.clip_coarse_changed(clip,trackNumber,clipNumber)
                    self.touchAble.tAListener.clipListener.clip_fine_changed(clip,trackNumber,clipNumber)
                except:
                    self.error_log("ClippCallbacks: touchAble.tAListener.clipListener.clip_gain_changed failed")

            self.ta_logger("clipstuff get gain",4)


            if clip.looping:
                loop_start = clip.loop_start
                loop_end = clip.loop_end
                clip.looping = 0
                end = clip.loop_end
                start = clip.loop_start
                clip.looping = 1
            else:
                end = clip.loop_end
                start = clip.loop_start
                clip.looping = 1
                loop_start = clip.loop_start
                loop_end = clip.loop_end
                clip.looping = 0
            if clip.is_audio_clip:
                clip.warping = warping

            self.ta_logger("clipstuff got gain",4)

            length = clip.length
            mute = clip.muted
            loop = clip.looping
            color = clip.color
            signature_denominator = clip.signature_denominator
            signature_numerator = clip.signature_numerator
            
            is_looping = clip.looping
            
            grid_quant = clip.view.grid_quantization
            grid_triplet = clip.view.grid_is_triplet
            grid_triplet_int = 0
            
            if grid_triplet:
                grid_triplet_int = 1
            else:
                grid_triplet_int = 0

            self.ta_logger("clipstuff got else",4)

            self.oscServer.sendOSC("/clip/grid_quantization",(int(trackNumber), int(clipNumber),str(grid_quant),int(grid_triplet_int+1)))
            
            self.ta_logger("clipstuff got else 1",4)


            self.oscServer.sendOSC("/clipstuff", (int(trackNumber), int(clipNumber), touchAbleUtils.repr2(nm), int(loop), int(mute), float(pitch_coarse), float(pitch_fine), float(start), float(end), float(length), int(color), int(is_audio_clip), int(signature_denominator), int(signature_numerator), int(warping), float(loop_start), float(loop_end), float(gain), touchAbleUtils.repr2(gain_str)))
            
            self.ta_logger("clipstuff got else 2",4)

            self.oscServer.sendOSC("/clip/looping", (int(trackNumber), int(clipNumber), int(is_looping)))

            self.ta_logger("clipstuff got else 3",4)


            if clip.is_audio_clip:
                path = clip.file_path
                self.ta_logger("clipstuff is audio",4)


                warp_mode = clip.warp_mode
                self.oscServer.sendOSC("/clip/warp_mode", (trackNumber, clipNumber,  int(warp_mode)))
                
                reset_data = [int(trackNumber), int(clipNumber), touchAbleUtils.repr2(path), float(0.0), float(1.0)]

                self.oscServer.sendOSC("/clip/reset_waveform", (tuple(reset_data)))
                if clip.warping:
                    try:
                        waveform_data = [int(trackNumber)]
                        waveform_data.append(int(clipNumber))
                        waveform_data.append(float(clip.sample_to_beat_time(clip.sample_length)))
                            
                        self.oscServer.sendOSC("/clip/sample_length", (tuple(waveform_data)))
                    except:
                        self.oscServer.sendOSC("/clip/sample_length_failed", 1)
                        pass
                else:
                    self.oscServer.sendOSC("/clip/clip_not_warped", 1)
                    pass

        else:
            nm = "aNo Clip selected"
            loop = 0
            mute = 0
            pitch = 0
            start = 0
            end = 0
            length = 0
            color = 0
            self.oscServer.sendOSC("/clipstuff", (int(trackNumber), int(clipNumber), touchAbleUtils.repr2(nm), int(loop), int(mute), float(pitch), float(start), float(end), float(length), int(color)))


    def loopStateCB(self, msg):
        type = msg[0] == '/clip/loopstate_id' and 1 or 0
    
        trackNumber = msg[2]
        clipNumber = msg[3]
    
        if len(msg) == 4:
            if type == 1:
                self.oscServer.sendOSC("/clip/loopstate", (trackNumber, clipNumber, int(LiveUtils.getClip(trackNumber, clipNumber).looping)))
            else:
                self.oscServer.sendOSC("/clip/loopstate", (int(LiveUtils.getClip(trackNumber, clipNumber).looping)))    
        
        elif len(msg) == 5:
            loopState = msg[4]
            LiveUtils.getClip(trackNumber, clipNumber).looping =  loopState


    def pitchCB(self, msg):
        """Called when a /live/pitch message is received.

        Messages:
        /live/pitch     (int track, int clip)                                               Returns the pan of track number track as: /live/pan (int track, int clip, int coarse(-48 to 48), int fine (-50 to 50))
        /live/pitch     (int track, int clip, int coarse(-48 to 48), int fine (-50 to 50))  Sets clip number clip in track number track's pitch to coarse / fine

        """
        if len(msg) == 6:
            track = msg[2]
            clip = msg[3]
            coarse = msg[4]
            fine = msg[5]
            LiveUtils.clipPitch(track, clip, coarse, fine)
        if len(msg) ==4:
            track = msg[2]
            clip = msg[3]
            self.oscServer.sendOSC("/pitch", LiveUtils.clipPitch(track, clip))

    def viewClipCB(self, msg):
        """Called when a /live/clip/view message is received.
        
        Messages:
        /live/clip/view     (int track, int clip)      Selects a track to view
        """
        track = LiveUtils.getSong().tracks[msg[2]]
        scene = LiveUtils.getSong().scenes[msg[3]]

        if len(msg) == 4:
            clip  = msg[3]
        else:
            clip  = 0
        
        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.selected_scene = scene

        LiveUtils.getSong().view.detail_clip = track.clip_slots[clip].clip
        Live.Application.get_application().view.show_view("Detail/Clip")  


    def detailViewCB(self, msg):
        """Called when a /live/detail/view message is received. Used to switch between clip/track detail

        Messages:
        /live/detail/view (int) Selects view where 0=clip detail, 1=track detail
        """
        if len(msg) == 3:
            if msg[2] == 0:
                Live.Application.get_application().view.show_view("Detail/Clip")
            elif msg[2] == 1:
                Live.Application.get_application().view.show_view("Detail/DeviceChain")


    def muteclipCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        muted = msg[4]
        LiveUtils.getClip(trackNumber, clipNumber).muted = muted


    def clipClearAutomation(self, msg):
    
        number_of_steps = msg[2]
        
        type = msg[3]
        tid = msg[4]
        device_id = msg[5]
        clip_inx = msg[6]
        parameter_inx = msg[7]
        
        live_track = LiveUtils.getSong().master_track
        
        if type == 0:
            live_track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            live_track = LiveUtils.getSong().return_tracks[tid]
        
        device = live_track.devices[device_id]
        
        for i in range(number_of_steps):
            chain_id = msg[8+i*2]
            device_id = msg[9+i*2]
            
            live_track = device.chains[chain_id]
            device = live_track.devices[device_id]
        
        
        clipSlot = live_track.clip_slots[clip_inx]
        clip = clipSlot.clip
        parameter = device.parameters[parameter_inx]
        clip.clear_envelope(parameter)

    def clipClearAutomationMixer(self, msg):
        type = msg[2]
        tid = msg[3]
        clip_inx = msg[4]
        parameter_inx = msg[5]
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "get clip mixer automation for para " + str(parameter_inx + 1))
        
        
        real_live_track = LiveUtils.getSong().master_track
        
        if type == 0:
            real_live_track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            real_live_track = LiveUtils.getSong().return_tracks[tid]
    
        clipSlot = real_live_track.clip_slots[clip_inx]
        clip = clipSlot.clip
        
        """ for obj_string in dir(live_track.mixer_device):
            self.oscServer.sendOSC("/NSLOG_REPLACE", touchAbleUtils.repr2(obj_string)) """

        if parameter_inx == 0:
            parameter = clip.muted
            self.oscServer.sendOSC("/NSLOG_REPLACE", "got muted " + touchAbleUtils.repr2(parameter))
        elif parameter_inx == 1:
            parameter = live_track.mixer_device.panning
        elif parameter_inx == 2:
            parameter = live_track.mixer_device.volume
        elif parameter_inx == 3:
            parameter = live_track.mixer_device.crossfade_assign
            self.oscServer.sendOSC("/NSLOG_REPLACE", "got crossfader assign " + touchAbleUtils.repr2(parameter))
        elif parameter_inx > 3:
            send_number = parameter_inx - 4
            parameter = live_track.mixer_device.sends[send_number]
        

        envelope = clip.clear_envelope(parameter)
        

    def clipReqAutomation(self, msg):
        number_of_steps = msg[2]
        self.tA_log("start bla")
        type = msg[3]
        tid = msg[4]
        device_id = msg[5]
        clip_inx = msg[6]
        parameter_inx = msg[7]

        real_live_track = LiveUtils.getSong().master_track

        if type == 0:
            real_live_track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            real_live_track = LiveUtils.getSong().return_tracks[tid]

        device = real_live_track.devices[device_id]
        self.tA_log("start bla 2")
        for i in range(number_of_steps):
            chain_id = msg[8+i*2]
            device_id = msg[9+i*2]

            live_track = device.chains[chain_id]
            device = live_track.devices[device_id]

        clipSlot = real_live_track.clip_slots[clip_inx]
        clip = clipSlot.clip

        parameter = device.parameters[parameter_inx]

        envelope = clip.automation_envelope(parameter)





        cid = clip_inx
        envelope_data = [int(tid)]
        envelope_data.append(int(cid))


        if parameter.automation_state == 0:
            self.tA_log("no Envelope found")
            envelope_data.append(int(0))
            self.oscServer.sendOSC("/clip/update_envelope",(tuple(envelope_data)))

        count = 0
        length = clip.end_marker - clip.start_marker
        max_count = 127
        add = length/128.
        time = add
        envelope_data.append(int(max_count))

        while count < max_count:
            float_val = envelope.value_at_time(time)
            envelope_data.append(float_val)
            count = count + 1
            time = time + add

            if count == 128:
                float_val = envelope.value_at_time(length)
                envelope_data.append(float_val)
                envelope_data = [int(tid)]
                envelope_data.append(int(cid))

                    
        self.oscServer.sendOSC("/clip/update_envelope", (tuple(envelope_data)))

    def clipReqAutomationMixer(self, msg):
        type = msg[2]
        tid = msg[3]
        clip_inx = msg[4]
        parameter_inx = msg[5]


        live_track = LiveUtils.getSong().master_track
        
        if type == 0:
            live_track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            live_track = LiveUtils.getSong().return_tracks[tid]
        
        clipSlot = live_track.clip_slots[clip_inx]
        clip = clipSlot.clip

        if parameter_inx == 0:
            parameter = clip.muted
            self.oscServer.sendOSC("/NSLOG_REPLACE", "got muted " + touchAbleUtils.repr2(parameter))
        elif parameter_inx == 1:
            parameter = live_track.mixer_device.panning
        elif parameter_inx == 2:
            parameter = live_track.mixer_device.volume
        elif parameter_inx == 3:
            parameter = live_track.mixer_device.crossfade_assign
            self.oscServer.sendOSC("/NSLOG_REPLACE", "got crossfader assign " + touchAbleUtils.repr2(parameter))
        elif parameter_inx > 3:
            send_number = parameter_inx - 4
            parameter = live_track.mixer_device.sends[send_number]

        envelope = clip.automation_envelope(parameter)

        self.oscServer.sendOSC("/NSLOG_REPLACE", "got envelope")

        if parameter.automation_state == 0:
            self.tA_log("no Envelope found")
            envelope_data.append(int(0))
            self.oscServer.sendOSC("/clip/update_envelope",(tuple(envelope_data)))

        cid = clip_inx
        envelope_data = [int(tid)]
        envelope_data.append(int(cid))
        count = 0
        length = clip.end_marker - clip.start_marker
        max_count = 127
        add = length/128.
        time = add
        envelope_data.append(int(max_count))


        while count < max_count:
            float_val = envelope.value_at_time(time)
            envelope_data.append(float_val)
            count = count + 1
            time = time + add
            
            if count == 128:
                float_val = envelope.value_at_time(length)
                envelope_data.append(float_val)
                envelope_data = [int(tid)]
                envelope_data.append(int(cid))
        
        self.oscServer.sendOSC("/clip/update_envelope", (tuple(envelope_data)))


    def clipInsertStepAutomationMixer(self, msg):
        
        type = msg[2]
        tid = msg[3]
        clip_inx = msg[4]
        parameter_inx = msg[5]
        time_stamp = msg[6]
        time_range = msg[7]
        value = msg[8]
        
        live_track = LiveUtils.getSong().master_track
        if type == 0:
            live_track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            live_track = LiveUtils.getSong().return_tracks[tid]
        
        clipSlot = live_track.clip_slots[clip_inx]
        
        clip = clipSlot.clip
        
        if parameter_inx == 0:
            parameter = live_track.mute
        elif parameter_inx == 1:
            parameter = live_track.mixer_device.panning
        elif parameter_inx == 2:
            parameter = live_track.mixer_device.volume
        elif parameter_inx == 3:
            parameter = live_track.mixer_device.crossfade_assign
        elif parameter_inx > 3:
            send_number = parameter_inx - 4
            parameter = live_track.mixer_device.sends[send_number]
        
        envelope = clip.automation_envelope(parameter)
        
        envelope.insert_step(time_stamp, time_range, value)

    def clipInsertStepAutomation(self, msg):
    
        number_of_steps = msg[2]
        
        type = msg[3]
        tid = msg[4]
        device_id = msg[5]
        clip_inx = msg[6]
        parameter_inx = msg[7]
        time_stamp = msg[8]
        time_range = msg[9]
        value = msg[10]

        real_live_track = LiveUtils.getSong().master_track
        if type == 0:
            real_live_track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            real_live_track = LiveUtils.getSong().return_tracks[tid]

        device = real_live_track.devices[device_id]

        for i in range(number_of_steps):
            chain_id = msg[11+i*2]
            device_id = msg[12+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]

        clipSlot = real_live_track.clip_slots[clip_inx]


        clip = clipSlot.clip
        parameter = device.parameters[parameter_inx]
        envelope = clip.automation_envelope(parameter)

        envelope.insert_step(time_stamp, time_range, value)
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "create audio at: " + str(live_track))


    def playClipSlotCB(self, msg):
        """Called when a /live/play/clipslot message is received.
        
        Messages:
        /live/play/clipslot     (int track, int clip)   Launches clip number clip in track number track
        """
        if len(msg) == 4:
            track_num = msg[2]
            clip_num = msg[3]
            track = LiveUtils.getTrack(track_num)
            clipslot = track.clip_slots[clip_num]
            try:
                clipslot.set_fire_button_state(True)
            except:
                clipslot.fire()
            
            if clipslot.clip == None:
                if track.arm == 1:
                    self.oscServer.sendOSC('/clip/playing_status', (track_num, clip_num, 4))
                else:
                    if track.playing_slot_index != -2:
                        if track.playing_slot_index != -1: 
                            self.oscServer.sendOSC('/clip/playing_status', (track_num, clip_num, 5))
                        else:
                            pass
                    else:
                        pass
            else:
                if track.arm == 1 and clip.is_audio_clip == 0 and LiveUtils.getSong().overdub == 1:
                    self.oscServer.sendOSC('/clip/playing_status', (track_num, clip_num, 4))
                else:
                    self.oscServer.sendOSC('/clip/playing_status', (track_num, clip_num, 2))


    def releaseClipSlotCB(self, msg):
        if len(msg) == 4:
            track_num = msg[2]
            clip_num = msg[3]
            track = LiveUtils.getTrack(track_num)
            clipslot = track.clip_slots[clip_num]
            try:
                clipslot.set_fire_button_state(False)
            except:
                pass

    def rammodeclipCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        ram_mode = msg[4]
        LiveUtils.getClip(trackNumber, clipNumber).ram_mode = ram_mode

    def warpmodeclipCB(self, msg):
        """ Called when a /live/clip/warping message is recieved
        """
        track = msg[2]
        clip = msg[3]
        warp_mode = msg[4]
            
        LiveUtils.getSong().tracks[track].clip_slots[clip].clip.warp_mode = warp_mode


    def warpingCB(self, msg):
        """ Called when a /live/clip/warping message is recieved
        """
        track = msg[2]
        clip = msg[3]
        
        
        if len(msg) == 4:
            state = LiveUtils.getSong().tracks[track].clip_slots[clip].clip.warping
            self.oscServer.sendOSC("/live/clip/warping", (track, clip, int(state)))
        
        elif len(msg) == 5:
            LiveUtils.getSong().tracks[track].clip_slots[clip].clip.warping = msg[4]


    def colorindexclipCB(self, msg):

        track = msg[2]
        clip = msg[3]
        color_index = msg[4]
                        
        LiveUtils.getSong().tracks[track].clip_slots[clip].clip.color_index = color_index


    def clipstartposCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        start = msg[4]
        
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        isLoop = clip.looping
        clip.looping = 0
        clip.loop_start = start
        clip.looping = isLoop
    
    def clipendposCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        end = msg[4]
        
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        isLoop = clip.looping
        clip.looping = 0
        clip.loop_end = end
        clip.looping = isLoop

    def startposCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        start = msg[4]
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        isLoop = clip.looping
        #isWarping = clip.warping
        
        clip.looping = 1
        clip.loop_start = start
        clip.looping = isLoop
        #clip.warping = isWarping

    def endposCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        end = msg[4]
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        isLoop = clip.looping
        #isWarping = clip.warping
        
        clip.looping = 1
        clip.loop_end = end
        clip.looping = isLoop
        #clip.warping = isWarping



    def changeMarkerStartCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        start = msg[4]
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        clip.start_marker = start
        

    def changeMarkerEndCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        end = msg[4]
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        clip.end_marker = end

    def pitchcoarseCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        pitch = int(msg[4])
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        if clip.is_audio_clip == 1:
            clip.pitch_coarse = int(pitch)
        

    def detuneCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        pitch = msg[4]
        clip = LiveUtils.getClip(trackNumber, clipNumber)

        if clip.is_audio_clip == 1:
            clip.pitch_fine = float(pitch)


    def clipQuantization(self, msg):
        
        track = msg[2]
        scene = msg[3]
        quant = msg[4]
        trk = LiveUtils.getSong().tracks[track]
        clip = trk.clip_slots[scene].clip
        


        if quant == 0:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_8_bars
        if quant == 1:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_4_bars
        if quant == 2:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_2_bars
        if quant == 3:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_bar
        if quant == 4:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_half
        if quant == 5:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_quarter
        if quant == 6:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_eighth
        if quant == 7:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth
        if quant == 8:
            clip.view.grid_quantization = Live.Clip.GridQuantization.g_thirtysecond
        if quant == 9:
            clip.view.grid_quantization = Live.Clip.GridQuantization.no_grid
                


    def clipIsTriplet(self, msg):
        
        track = msg[2]
        scene = msg[3]
        is_triplet = msg[4]
        trk = LiveUtils.getSong().tracks[track]
        clip = trk.clip_slots[scene].clip
    
        clip.view.grid_is_triplet = bool(is_triplet)

    def clipSelected(self, msg):

        track = msg[2]
        scene = msg[3]
        length = msg[4]
        trk = LiveUtils.getSong().tracks[track]
        clip = trk.clip_slots[scene].clip
        
        
        
        if clip == None:
            a = Live.Application.get_application().get_major_version()
            if a >= 9:
                clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
                clipSlot.create_clip(float(length))
                clip = clipSlot.clip
                if clip.name != None:
                    nm = cut_string(clip.name)
                else:
                    nm = " "
                self.oscServer.sendOSC("/clip", (track, scene, touchAbleUtils.repr3(nm), clip.color, int(0),int(0)))

            else:
                pass



        key = '%s.%s' % (track, scene)

        cb = lambda :self.notesChanged(track, scene, clip)
        if self.noteListeners.has_key(clip) != 1:
            clip.add_notes_listener(cb)
            self.noteListeners[clip] = cb

        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
                    
        LiveUtils.getSong().view.selected_track = trk
        LiveUtils.getSong().view.detail_clip = clip
        Live.Application.get_application().view.show_view("Detail/Clip")

        
        notes = [int(track)]
        notes.append(int(scene))
        count = 0
        
        clip.select_all_notes()
        
        clipNotes = clip.get_selected_notes()
        clip.deselect_all_notes()
        loopstart = 0
        looplength = 0
        start = 0
        end = 0
        looping = clip.looping
        
        if looping == 1:
            
            loopstart = clip.loop_start
            loopend = clip.loop_end
            
            clip.looping = 0            
            start = clip.loop_start
            end = clip.loop_end
            clip.looping = 1
        
        else:
            start = clip.loop_start
            end = clip.loop_end
            
            clip.looping = 1
            
            loopstart = clip.loop_start
            loopend = clip.loop_end
            clip.looping = 0
                    
        try:
            start = clip.start_marker
            end = clip.end_marker
        except:
            pass
        #self.oscServer.sendOSC("/bundle/start", (1))

        self.oscServer.sendOSC("/clip/requested_loop_stats", (int(track), int(scene), float(start), float(end), float(loopstart), float(loopend)))

        self.oscServer.sendOSC("/clip/start_receiving_notes", (int(track), int(scene)))
        
        noteBuffer = self.noteBuffers[key]

                
        for note in clipNotes:
            noteBuffer.append(note)
            for var in note:
                notes.append(float(var))
            count = count+1
            if count == 128:
                self.oscServer.sendOSC("/clip/receive_notes", tuple(notes))
                count = 0
                notes = [int(track)]
                notes.append(int(scene))
        
        self.oscServer.sendOSC("/clip/receive_notes", tuple(notes))
        self.oscServer.sendOSC("/clip/end_receiving_notes", (int(track), int(scene)))
        self.oscServer.sendOSC("/finish_loading", (1))
        #self.oscServer.sendOSC("/bundle/end", (1))


    def clipCrop(self, msg):
    
        track = msg[2]
        scene = msg[3]

        trk = LiveUtils.getSong().tracks[track]
        clip = trk.clip_slots[scene].clip
        clip.crop()



    def clearNoteBuffer(self, msg):
        track = msg[2]
        scene = msg[3]
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip

        key = '%s.%s' % (track, scene)
        self.noteBuffers[key] = []
            


    
    def addNotesToBuffer(self, msg):
        track = msg[2]
        scene = msg[3]
        noteCount = (len(msg)-4)/5
        key = '%s.%s' % (track, scene)

        
        noteBuffer = self.noteBuffers[key]

            
        for i in range(noteCount):
            noteDescription = []
            ind = 4 + (i*5)
            pitch = msg[(ind+0)]
            time = msg[(ind+1)]
            length = msg[(ind+2)]
            velocity = msg[(ind+3)]
            mute = msg[(ind+4)]
            
            noteDescription.append(int(pitch))
            noteDescription.append(float(time))
            noteDescription.append(float(length))
            noteDescription.append(float(velocity))
            noteDescription.append(bool(mute))
            
            noteBuffer.append(noteDescription)
            


    def replaceCurrentNotesWithBuffer(self, msg):
        track = msg[2]
        scene = msg[3]
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
        clip.select_all_notes()
        key = '%s.%s' % (track, scene)
                    
        noteBuffer = self.noteBuffers[key]

       
        clip.replace_selected_notes(tuple(noteBuffer))
        clip.deselect_all_notes()


    def setNoteVelocity(self, msg):

        track = msg[2]
        scene = msg[3]

        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        velocity = float(msg[7])
        mute = bool(msg[8])
        
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
        
        #clip.remove_notes(time, pitch, length, 1)
        
        newClipNotes = []
        noteDescription = []

        noteDescription.append(pitch)
        noteDescription.append(time)
        noteDescription.append(length)
        noteDescription.append(velocity)
        noteDescription.append(mute)
        
        newClipNotes.append(noteDescription)
        clip.set_notes(tuple(newClipNotes))


            
    def addNote(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        velocity = float(msg[7])
        mute = bool(msg[8])
       
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
                
        newClipNotes = []
        noteDescription = []
        
        noteDescription.append(pitch)
        noteDescription.append(time)
        noteDescription.append(length)
        noteDescription.append(velocity)
        noteDescription.append(mute)
        
        newClipNotes.append(noteDescription)
        clip.set_notes(tuple(newClipNotes))
    
    
    def addNotes(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        noteCount = (len(msg)-4)/5
        
        newClipNotes = []

        for i in range(noteCount):
            noteDescription = []
            ind = 4 + (i*5)
            pitch = int(msg[(ind+0)])
            time = float(msg[(ind+1)])
            length = float(msg[(ind+2)])
            velocity = float(msg[(ind+3)])
            mute = bool(msg[(ind+4)])
        
            noteDescription.append(pitch)
            noteDescription.append(time)
            noteDescription.append(length)
            noteDescription.append(velocity)
            noteDescription.append(mute)
        
            newClipNotes.append(noteDescription)
        
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
        clip.set_notes(tuple(newClipNotes))


    def selectNotes(self, msg):
    
        track = msg[2]
        scene = msg[3]
        
        pitch_min = int(msg[4])
        pitch_max = int(msg[5])

        time = float(msg[6])
        length = float(msg[7])
        
        velocity = float(msg[8])

        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
    
    
        clip.remove_notes(time, pitch_min, length, pitch_max)
        clip.set_notes(time, pitch_min, length, pitch_max)
    
    
    def deselectNote(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch_min = int(msg[4])
        pitch_max = int(msg[5])
        
        time = float(msg[6])
        length = float(msg[6])
        
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
        
        clip.get_notes(time, pitch_min, length, 127)

    def updateNoteVelocity(self, msg):

        track = msg[2]
        scene = msg[3]

        noteCount = (len(msg)-4)/5
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip

        newSelectedNotes = []
        
        stringstring = str(noteCount)
        

        for i in range(noteCount):
            ind = 4 + (i*5)
            pitch = int(msg[(ind+0)])
            time = float(msg[(ind+1)])
            length = float(msg[(ind+2)])
            velocity = float(msg[(ind+3)])
            mute = bool(msg[(ind+4)])
            selectedNotes = []
            
            """ a_string = "pitch " + str(pitch) + " time: " + str(time) + " length: " + str(length) + " vel: " + str(velocity) +  " sasdasd"
        
            self.oscServer.sendOSC("/NSLOG_REPLACE", a_string) """

            selectedNotes = clip.get_notes(time - 0.001, pitch, length + 0.001, 1)
            
            a_length = len(selectedNotes)
            aNote = selectedNotes[0]
            lst = list(aNote)
            lst[3] = velocity
            lst[4] = mute
            aaNote = tuple(lst)
            newSelectedNotes.append(aaNote)

        clip.set_notes(tuple(newSelectedNotes))


    def updateNote(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        velocity = float(msg[7])
        mute = bool(msg[8])
        
        oldpitch = int(msg[9])
        oldtime = float(msg[10])
        oldlength = float(msg[11])
        
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
        
        clip.remove_notes(oldtime - 0.001, oldpitch, oldlength - 0.002, 1)
        
        newClipNotes = []
        noteDescription = []
        
        noteDescription.append(pitch)
        noteDescription.append(time)
        noteDescription.append(length)
        noteDescription.append(velocity)
        noteDescription.append(mute)
        
        newClipNotes.append(noteDescription)
        clip.set_notes(tuple(newClipNotes))

    
    
    def removeNote(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
        clip.remove_notes(time - 0.001, pitch, length - 0.002, 1)
    
    def removeNotes(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip
        clip.remove_notes(time - 0.001, pitch, length - 0.002, 1)
    
    
    
    def stretchNotes(self, msg):
        
        track = msg[2]
        scene = msg[3]
        factor = msg[4]
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip

        clipLength = 0
        looping = 0
        if clip.looping:
            clip.looping = 0

            clip.loop_end = (clip.loop_end-clip.loop_start)*factor + clip.loop_start
            
            clip.looping = 1
            looping = 1
            clip.loop_end = (clip.loop_end-clip.loop_start)*factor + clip.loop_start

        else:
            clip.loop_end = (clip.loop_end-clip.loop_start)*factor + clip.loop_start
            
            clip.looping = 1
            clip.loop_end = (clip.loop_end-clip.loop_start)*factor + clip.loop_start
            clip.looping = 0
    

        
        clip.select_all_notes()
        notes = clip.get_selected_notes()


        newClipNotes = []
        
        for note in notes:
            noteDescription = []

            pitch = int(note[0])
            time = float(note[1])
            length = float(note[2])
            velocity = float(note[3])
            mute = bool(note[4])


            length = length*factor
            time = time*factor
            
            noteDescription.append(pitch)
            noteDescription.append(time)
            noteDescription.append(length)
            noteDescription.append(velocity)
            noteDescription.append(mute)
        
            newClipNotes.append(noteDescription)

    
        clip.replace_selected_notes(tuple(newClipNotes))
    
        
        is_audio_clip = int(0)
        warp = 0
        start = 0
        end = 0
        loop_start = 0
        loop_end = 0
            

        if clip.looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
            
            clip.looping = int(0)
            start = clip.loop_start
            end = clip.loop_end
        else:
            start = clip.loop_start
            end = clip.loop_end
            
            clip.looping = 1
            loop_start = clip.loop_start
            loop_end = clip.loop_end

        if looping == 1:
            clip.looping = 1
        else:
            clip.looping = 0

        self.oscServer.sendOSC("/clip/loopstats", (int(track), int(scene), looping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))

    def notesChanged2(self, track, scene, clip):
        notes = [int(track)]
        notes.append(int(scene))
        count = 0
        clip = LiveUtils.getSong().tracks[int(track)].clip_slots[int(scene)].clip

        clipNotes = []
        clipNotes = clip.get_selected_notes()
    
        start = clip.start_marker
        end = clip.end_marker
        loopstart = clip.loop_start
        loopend = clip.loop_end
        self.oscServer.sendOSC("/clip/requested_loop_stats", (int(track), int(scene), float(start), float(end), float(loopstart), float(loopend)))
        
        self.oscServer.sendOSC("/clip/start_updating_notes", 1)

        key = '%s.%s' % (track, scene)
    
        noteBuffer = []
        self.noteBuffers[key] = noteBuffer
        
        for note in clipNotes:
            
            for var in note:
                notes.append(float(var))
        
            noteBuffer.append(note)
            
            count = count+1
            if count == 128:
                self.oscServer.sendOSC("/clip/update_notes", tuple(notes))
                count = 0
                notes = [int(track)]
                notes.append(int(scene))
            

        self.oscServer.sendOSC("/clip/update_notes", tuple(notes))
        self.oscServer.sendOSC("/clip/end_updating_notes", 1)



    def notesChanged(self, track, scene, clip):
        notes = [int(track)]
        notes.append(int(scene))
        count = 0
        clip = LiveUtils.getSong().tracks[int(track)].clip_slots[int(scene)].clip
        a = Live.Application.get_application().get_major_version()
        clipNotes = []
        
        #if a >= 9:
        clipNotes = clip.get_notes(float(0), int(0), float(100000), int(127))
        #else:

        
        
        """ clipNotes2 = []



        clip.deselect_all_notes()
        clip.select_all_notes()
        
        clipNotes = clip.get_selected_notes()
        
        clip.deselect_all_notes() """
        
        loopstart = 0
        looplength = 0
        start = 0
        end = 0
        looping = 0
        loopend = 0
        version = 0
            
        
        #self.oscServer.sendOSC("/bundle/start", (1))
        start = clip.start_marker
        end = clip.end_marker
        loopstart = clip.loop_start
        loopend = clip.loop_end
        self.oscServer.sendOSC("/clip/requested_loop_stats", (int(track), int(scene), float(start), float(end), float(loopstart), float(loopend)))

        self.oscServer.sendOSC("/clip/start_receiving_notes", (int(track), int(scene)))



        key = '%s.%s' % (track, scene)

        noteBuffer = []
        self.noteBuffers[key] = noteBuffer

        for note in clipNotes:

            for var in note:
                notes.append(float(var))
            
            noteBuffer.append(note)

            count = count+1
            if count == 128:
                self.oscServer.sendOSC("/clip/receive_notes", tuple(notes))
                count = 0
                notes = [int(track)]
                notes.append(int(scene))

        self.oscServer.sendOSC("/clip/receive_notes", tuple(notes))
        self.oscServer.sendOSC("/clip/end_receiving_notes", (int(track), int(scene)))

        #self.oscServer.sendOSC("/finish_loading", (1))
        #self.oscServer.sendOSC("/bundle/end", (1))

        clipNotes2 = clip.get_selected_notes()
        if len(clipNotes2) >= 1:
            self.notesChanged2(track, scene, clip)
            return


    def backFromClip(self, msg):
                
        track = msg[2]
        scene = msg[3]
        
        key = '%s.%s' % (track, scene)
        clip = LiveUtils.getSong().tracks[track].clip_slots[scene].clip

        if clip.notes_has_listener(self.noteListeners[clip]) == 1:
            clip.remove_notes_listener(self.noteListeners[clip])
            del self.noteListeners[clip]
       
                
        
    def request_loop_data(self, msg):
        track = msg[2]
        scene = msg[3]
        clip = LiveUtils.getSong().tracks[int(track)].clip_slots[int(scene)].clip
        loopstart = 0
        start = 0
        end = 0
        loopend = 0
            
        looping = clip.looping
            
        if looping == 1:
            
            loopstart = clip.loop_start
            loopend = clip.loop_end
            
            clip.looping = 0
            start = clip.loop_start
            end = clip.loop_end
            clip.looping = 1
        
        else:
            start = clip.loop_start
            end = clip.loop_end
            
            clip.looping = 1
            
            loopstart = clip.loop_start
            loopend = clip.loop_end
            clip.looping = 0
        
        try:
            start = clip.start_marker
            end = clip.end_marker
        except:
            pass
                
        self.oscServer.sendOSC("/clip/requested_loop_stats", (int(track), int(scene), float(start), float(end), float(loopstart), float(loopend)))


    

    def loopStartCB(self, msg):
        
        track = msg[2]
        scene = msg[3]
        self.oscServer.sendOSC("/clip/loopstart", 1)
        clip = LiveUtils.getSong().tracks[int(track)].clip_slots[int(scene)].clip

        loopStart = msg[4]
        clip.loop_start = loopStart
        self.oscServer.sendOSC("/clip/loopstart", 2)
    
    
    def loopEndCB(self, msg):
        
        track = msg[2]
        scene = msg[3]
        self.oscServer.sendOSC("/clip/loopend", 1)

        clip = LiveUtils.getSong().tracks[int(track)].clip_slots[int(scene)].clip

        loopEnd = msg[4]
        self.oscServer.sendOSC("/clip/loopend", 1)
        
        clip.loop_end = loopEnd
        self.oscServer.sendOSC("/clip/loopend", 2)


    def jumpForwardCB(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        clip = LiveUtils.getClip(tr, cl)
        
        clip.move_playing_pos(length)
    
    def jumpBackwardCB(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        clip = LiveUtils.getClip(tr, cl)
        
        clip.move_playing_pos(length)
    
    
    def jumpLoopForward(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        
        clip = LiveUtils.getClip(tr, cl)
        clip.looping = 1
        start = clip.loop_start
        
        clip.loop_end = clip.loop_end + length
        clip.move_playing_pos(length)
        clip.loop_start = start + length    
    
    def jumpLoopBackward(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        clip = LiveUtils.getClip(tr, cl)
        start = clip.loop_start
        
        clip.looping = 1
        
        size = clip.loop_end - start
        
        if start+length > 0:
            clip.loop_start = start + length
            #clip.move_playing_pos(size)
            clip.loop_end = clip.loop_end + length
            #start = clip.loop_start
        else:
            clip.loop_start = 0
            clip.loop_end = size
            #start = 0
        clip.move_playing_pos(length)


    def getActiveLoops(self, msg):

        for clip in self.clipListener.oldloop_start:
            if clip != None:
                tr = int(self.clipListener.trackid[clip])
                cl = int(self.clipListener.clipid[clip])
                ll = float(self.clipListener.loop_length[clip])
                self.oscServer.sendOSC('/clip/hotlooping', (int(tr), int(cl), 1, float(ll)))
                
            
    def clearHiddenLoops(self, msg):
        for clip in self.clipListener.oldloop_start:
            if clip != None:
                if clip.is_playing == 1:
                    clip.looping = 0
                    
                    clip.loop_end = float(self.clipListener.oldplay_end[clip])
                    clip.loop_start = float(self.clipListener.oldplay_start[clip])
                    
                    clip.looping = 1
                    
                    clip.loop_end = float(self.clipListener.oldloop_end[clip])
                    clip.loop_start = float(self.clipListener.oldloop_start[clip])
                    
                    if clip.loop_end > float(self.clipListener.oldloop_end[clip]):
                        clip.loop_end = float(self.clipListener.oldloop_end[clip])
                    else:
                        pass
                    
                    if clip.loop_end < float(self.clipListener.oldloop_end[clip]):
                        clip.loop_end = float(self.clipListener.oldloop_end[clip])
                    else:
                        pass
                    
                    clip.looping = int(self.clipListener.oldlooping[clip])
                    
                    tr = int(self.clipListener.trackid[clip])
                    cl = int(self.clipListener.clipid[clip])

                    del self.clipListener.oldplay_start[clip]
                    del self.clipListener.oldplay_end[clip]
                    del self.clipListener.oldloop_start[clip]
                    del self.clipListener.oldloop_end[clip]
                    del self.clipListener.oldlooping[clip]
                    del self.clipListener.hotlooping[clip]
                    del self.clipListener.loop_length[clip]
                    del self.clipListener.trackid[clip]
                    del self.clipListener.clipid[clip]
                    self.oscServer.sendOSC('/clip/hotlooping', (int(tr), int(cl), 0, float(4)))
                else:
                    pass
            else:
                pass
            
   
    
    def changeLoopCB(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        
        clip2 = LiveUtils.getClip(tr, cl)
        clip2.loop_end = clip2.loop_start + length
        clip2.looping = 0
        clip2.loop_end = clip2.loop_start + length
        clip2.looping = 1
        for clip in self.loop_length:
            if clip != None:
                if clip == clip2:
                    self.loop_length[clip] = float(length)
        
        self.oscServer.sendOSC('/clip/hotlooping', (int(tr), int(cl), 1, float(length)))

                    
    def clip_loopstats(self, clip, tid, cid):
        
        clip = LiveUtils.getClip(tid, cid)
        isLooping = int(clip.looping)
        self.oscServer.sendOSC('/clip/sdsd', (tid, cid))

        if clip.looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
            
            clip.looping = 0
            start = clip.loop_start
            end = clip.loop_end
        else:
            start = clip.loop_start
            end = clip.loop_end
            
            clip.looping = 1
            loop_start = clip.loop_start
            loop_end = clip.loop_end
        
        clip.looping = isLooping
        self.oscServer.sendOSC('/clip/loopstats', (tid, cid, isLooping, start, end, loop_start, loop_end))
    

    def clip_loopstats2(self, msg):
                    
        tid = msg[2]
        cid = msg[3]
                                                
        clip = LiveUtils.getClip(tid, cid)
            
        isLooping = int(clip.looping)
        
        if clip.looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
                            
            clip.looping = int(0)
            start = clip.loop_start
            end = clip.loop_end
        else:
            start = clip.loop_start
            end = clip.loop_end
                            
            clip.looping = 1
            loop_start = clip.loop_start
            loop_end = clip.loop_end
                        
        clip.looping = isLooping
        self.oscServer.sendOSC('/clip/loopstats', (tid, cid, isLooping, start, end, loop_start, loop_end))

    
    #self.oscServer.sendOSC('/oldLoopData', (track, clip, looping, loopStart, loopLength))

    def keepLoop(self, msg):
        tr = msg[2]
        cl = msg[3]
        clip2 = LiveUtils.getClip(tr, cl)
        for clip in self.clipListener.oldloop_start:
            if clip != None:
                if clip == clip2:
                    del self.clipListener.oldplay_start[clip]
                    del self.clipListener.oldplay_end[clip]
                    del self.clipListener.oldloop_start[clip]
                    del self.clipListener.oldloop_end[clip]
                    del self.clipListener.oldlooping[clip]
                    del self.clipListener.hotlooping[clip]
                    del self.clipListener.loop_length[clip]
                    del self.clipListener.trackid[clip]
                    del self.clipListener.clipid[clip]
                    self.oscServer.sendOSC('/clip/hotlooping', (int(tr), int(cl), 0, float(4)))




