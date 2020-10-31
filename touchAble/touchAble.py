# LMH
from __future__ import with_statement

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

"""
import struct
import Utils.RemixNet as RemixNet
import Utils.OSC as OSC
import time
import unicodedata
import thread
import config
import Live
import Utils.touchAbleUtils
import Utils.LiveUtils as LiveUtils
import touchAbleCommon
import touchAbleListener
import touchAbleCallbacks

from threading import Timer
from collections import defaultdict
from Utils.Logger import Logger as Logger
#from Utils.SessionComponent import TouchableSessionComponent as TouchableSessionComponent 
#from Utils.SessionRingComponent import SessionRingComponent  # SVH Addition # Zerodebug Addition
from _Generic.util import DeviceAppointer
from _Framework.ControlSurface import ControlSurface

from inspect import currentframe, getframeinfo

class touchAble(ControlSurface):
    __module__ = __name__
    __doc__ = "Main class that establishes the touchAble Component"
    
    # Enable Logging
    _LOG = 0

    # local variables
    updateTime = 0

    # globals used live variables
    onetap = 0
    metermode = 1
    received_midi_cmd = 1
    scene = 0
    track = 0
    width = 16
    session = 0

    # Version variables
    script_version = config.script_version
    app_main_version = config.app_main_version
    app_minor_version = config.app_minor_version
    app_sub_minor_version = config.app_sub_minor_version

    # Script status variables
    did_init_osc_server = 0
    did_init = 0
    listeners_updated = 0

    # Callback and Listener classes
    tACommon = None
    tAListener = None
    tACallbacks = None

    def __init__(self, c_instance):

        self._touchAble__c_instance = c_instance
        ControlSurface.__init__( self, c_instance )

        try:
            self.init_locked_device()
        except:
            self.error_log("init_locked_device failed")

        try:
            self.do_init()
        except:
            self.error_log("do_init failed")  
        
        

        #thread.start_new_thread(self.do_init())

    def init_locked_device(self):

        self.locked_device = LiveUtils.getSong().view.selected_track.view.selected_device
        self.lock_to_device(self.locked_device)
        self._device_appointer = None
        self._device_selection_follows_track_selection = True
        
        if self._device_selection_follows_track_selection == True:
            self.tA_log("devices DO follow track selection..")
        else:
            self.tA_log("devices DO NOT!!! follow track selection..")

        self.show_message("loading touchAble Pro Control Surface..")

        try:
            self._device_appointer = DeviceAppointer(song=LiveUtils.getSong(), appointed_device_setter=self._set_appointed_device)
        except:
            self.error_log("touchAble: DeviceAppointer init failed")
            pass


    def _log( self, msg, force = False ):
        if self._LOG or force:
            self.tA_log( msg )


    def do_init(self):
        if self.did_init_osc_server == 0:
            self.did_init_osc_server = 1

            try:
                self.oscServer = RemixNet.OSCServer(self, '127.0.0.1', 9111, None, 9008)
                self.callbackManager = self.oscServer.callbackManager
            except:
                self.error_log("touchAble: OSCServer init failed")
                self.did_init_osc_server = 0
                pass
            try:
                self.tACommon = touchAbleCommon.touchAbleCommon(self._touchAble__c_instance, self.oscServer, self)
            except:
                self.did_init = 0
                self.error_log("touchAble: tACommon init failed")
                pass
            try:
                self.tAListener = touchAbleListener.touchAbleListener(self._touchAble__c_instance, self.oscServer, self)
            except:
                self.did_init = 0
                self.error_log("touchAble: tAListener init failed")
                pass
            try:
                self.logger = self._LOG and Logger() or 0
                self.tA_log("Logging Enabled")
            except:
                self.error_log("touchAble: Logger init failed")
                pass
            try:
                with self.component_guard():
                    pass
                    #self._session_ring = self._create_session()  # SVH Change # Zerodebug Addition
            except:
                self.error_log("touchAble: _create_session failed")

            self.did_init = 1
        else:
            self.did_init = 0
            pass


    def update_all_listenersCB(self,msg):
        if (self.listeners_updated != 1):
            self.listeners_updated = 1
            self.update_all_listeners()
            #thread.start_new_thread(self.update_all_listeners, ())


    def _create_session(self):
        log_text = "_create_session : v " + str(self.script_version)
        session_ring = SessionRingComponent(  # SVH Addition
            num_tracks=8,
            num_scenes=10,
            is_enabled=True,
            is_root=True,
            register_component=self._register_component,
            song=self.song(),
            set_session_highlight=self._set_session_highlight,
        )
        self._log( "_create_session complete", True )
        return session_ring  # SVH Addition # Zerodebug Change


    def set_lsync_offsets(self,x,y,w,h):
        pass
        #self._log( "set_lsync_offsets: " + str( x ) + ", " + str( y ) + ", " + str( w ) + ", " + str( h ) )
        #self.session._set_lsync_offsets( x, y, w, h )
    

    
    def _send_lsync_coords(self):
        pass
        #self._log( "_send_lsync_coords" )
        #self.session._send_lsync_coords( "6" )
        
    #self.log(str(Live.Application.get_application().view.available_main_views()))
        #LiveUtils.getSong().master_track.create_device(str("EQEight"))
    
    def _set_appointed_device(self, device):
        #self.oscServer.sendOSCUDP("/NSLOG_REPLACE", ("appointed device changed 1"))

        self.unlock_from_device(self.locked_device)
        #self.oscServer.sendOSCUDP("/NSLOG_REPLACE", ("appointed device changed 2"))

        self.lock_to_device(device)
        #self.oscServer.sendOSCUDP("/NSLOG_REPLACE", ("appointed device changed 3"))

        self.locked_device = device
        
        #self.oscServer.sendOSCUDP("/NSLOG_REPLACE", ("appointed device changed 4"))
        
        pass
    
    def loadAllCB(self, msg):
        """Called when a /live/tracks message is received.

        Messages:
        /live/tracks       no argument or 'query'  Returns the total number of scenes

        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            trackTotal = len(LiveUtils.getTracks())
            sceneTotal = len(LiveUtils.getScenes())
            returnsTotal = len(LiveUtils.getSong().return_tracks)
            self.oscServer.sendOSC("/set/size", (trackTotal, sceneTotal, returnsTotal))
            self.oscServer.sendOSC("/NSLOG_REPLACE", "set size load all cb")
            return

    def updateCB(self):
        self.tACommon.positions()
        self.tACommon.mastermeters()
        self.tACommon.meters()
        self.tACommon.songtime_change()
        

    def sendScriptPong(self):

        xx = int(self.oscServer.tcpServer.srcPort)
        c = Live.Application.get_application().get_bugfix_version()
        b = Live.Application.get_application().get_minor_version()
        a = Live.Application.get_application().get_major_version()
        script_versiona = 1556

        self.oscServer.sendOSCUDP("/script/pong", (int(self.script_version), int(xx), int(a), int(b), int(c),int(self.listeners_updated),int(self.received_midi_cmd)))
        self.oscServer.sendOSCUDP("/script/version", self.script_version)

            
######################################################################
# Standard Ableton Methods

    def connect_script_instances(self, instanciated_scripts):
        """
        Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules
        """
        return

    def is_extension(self):
        return False

    def request_rebuild_midi_map(self):
        #self.oscServer.sendOSC('/NSLOG_REPLACE', "refresh_state.")

        """
        To be called from any components, as soon as their internal state changed in a 
        way, that we do need to remap the mappings that are processed directly by the 
        Live engine.
        Dont assume that the request will immediately result in a call to
        your build_midi_map function. For performance reasons this is only
        called once per GUI frame.
        """
        return
    
    def update_display(self):
        """
        This function is run every 100ms, so we use it to initiate our Song.current_song_time
        listener to allow us to process incoming OSC commands as quickly as possible under
        the current listener scheme.
        """
        ######################################################
        # START OSC LISTENER SETUP
        if self.tACallbacks == None and self.did_init == 1:

            # By default we have set tACallbacks to 0 so that we can assign it after
            # initialization. We try to get the current song and if we can we'll
            # connect our tACallbacks callbacks to the listener allowing us to 
            # respond to incoming OSC every 60ms.
            #
            # Since this method is called every 100ms regardless of the song time
            # changing, we use both methods for processing incoming UDP requests
            # so that from a resting state you can initiate play/clip triggering.
            
            try:
                doc = LiveUtils.getSong()
            except:
                self.error_log("could not get song from Live Utils")
                return
            try:
                # LMH

                self.tACallbacks = touchAbleCallbacks.touchAbleCallbacks(self._touchAble__c_instance, self.oscServer, self)
                self.tA_log("initialised tACallbacks..")

                # Commented for stability
                #doc.add_current_song_time_listener(self.oscServer.processIncomingUDP)
                #self.oscServer.sendOSC("/server/refresh", (1))

                
            except:
                self.error_log("could not create touchAbleCallbacks")
                return
    
            
            # If our OSC server is listening, try processing incoming requests.
            # Any 'play' initiation will trigger the current_song_time listener
            # and bump updates from 100ms to 60ms.

        
        
            
        if self.oscServer:
            try:
                #self.oscServer.sendOSC('/processingOSC', (1))
                
                self.oscServer.processIncomingUDP()
                
            except:
                pass
        #self.updateTime = self.updateTime +4
        #if self.updateTime >= 100:

        if self.oscServer:
            self.sendScriptPong()
            #self.tA_log("sent script pong..")

            self.updateCB()
            
        # END OSC LISTENER SETUP
        ######################################################

    def send_midi(self, midi_event_bytes):
        """
        Use this function to send MIDI events through Live to the _real_ MIDI devices 
        that this script is assigned to.
        """
        pass

    def receive_midi(self,midi_bytes):

        if midi_bytes[0] == 240 and self.did_init == 1:
            self.received_midi_cmd = 1
            if midi_bytes[1] == 2:
                self.updateCB()
                #self.oscServer.sendOSC('/midi/received', (midi_bytes))
            elif self.oscServer:
                try:
                    #self.oscServer.sendOSCUDP("/NSLOG_REPLACE", "DATA RECEIVED 0")
                    self.oscServer.processIncomingUDP()
                except:
                    pass
        else:
            pass
        
        
            
    def can_lock_to_devices(self):
        return True
    
    def lock_to_device(self, device):
        ControlSurface.lock_to_device(self, device)
        self.ta_logger("locking to device..",5)
        pass

    def unlock_from_device(self, device):
        ControlSurface.unlock_from_device(self, device)
        self.ta_logger("unlocking from device..",5)
        pass

    def suggest_input_port(self):
        return 'touchAble Script Input'

    def suggest_output_port(self):
        return ''

    def suggest_map_mode(self, cc_no, channel):
        return Live.MidiMap.MapMode.absolute
    
    def __handle_display_switch_ids(self, switch_id, value):
        pass
    
    
######################################################################
# Useful Methods


    def getOSCServer(self):
        return self.oscServer
    
    def application(self):
        """returns a reference to the application that we are running in"""
        return Live.Application.get_application()


    def handle(self):
        """returns a handle to the c_interface that is needed when forwarding MIDI events via the MIDI map"""
        return self._touchAble__c_instance.handle()

    def log(self, msg):
        if self._LOG == 1:
            self.logger.log(msg) 
            
        
######################################################################
# Used Ableton Methods

    def disconnect(self):

        try:
            self.tAListener.remove_all_listeners()            
            self.oscServer.sendOSC('/remix/oscserver/shutdown', 1)
            self.oscServer.shutdown()
        except:
            self.oscServer.sendOSC('/remix/oscserver/shutdown', 1)
            self.oscServer.shutdown()

    def build_midi_map(self, midi_map_handle):
        pass

    def refresh_state(self):
        pass

    def update_all_listeners(self):
        self.tAListener.update_all_listeners()

    def ta_logger(self, msg, number):
        frameinfo = getframeinfo(currentframe())
        return
        self.log_message("#### touchAble " +str(self.script_version)+ " TA LOG: " + " line:"+ str(frameinfo.lineno) + " msg: " + msg + " ###")
        send_to_app = 0
        if send_to_app == 1:
            self.oscServer.sendOSCUDP("/NSLOG_REPLACE", msg)

    def tA_log(self, msg):
        frameinfo = getframeinfo(currentframe())

        self.log_message("#### touchAble " +str(self.script_version)+ " TA LOG: " + " line:"+ str(frameinfo.lineno) + " msg: " + msg + " ###")
        send_to_app = 0
        if send_to_app == 1:
            self.oscServer.sendOSCUDP("/NSLOG_REPLACE", msg)

    def error_logger(self, msg):
        frameinfo = getframeinfo(currentframe())

        self.log_message("*** touchAble " +str(self.script_version)+ " Script Error: " + " line:"+ str(frameinfo.lineno) + " msg: " + msg + " ***")
        send_to_app = 0
        if send_to_app == 1:
            self.oscServer.sendOSCUDP("/NSLOG_REPLACE", msg)

    def error_log(self, msg):
        frameinfo = getframeinfo(currentframe())

        self.log_message("*** touchAble " +str(self.script_version)+ " Script Error: " + " line:"+ str(frameinfo.lineno) + " msg: " + msg + " ***")
        send_to_app = 0
        if send_to_app == 1:
            self.oscServer.sendOSCUDP("/NSLOG_REPLACE", msg)



