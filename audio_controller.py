import threading
import time
from typing import Dict ,Optional
from ctypes import POINTER ,cast
from comtypes import CLSCTX_ALL
from pycaw .pycaw import AudioUtilities ,IAudioEndpointVolume ,ISimpleAudioVolume
class AudioController :
    def __init__ (self ):
        self .original_volumes :Dict [str ,float ]={}
        self .transition_threads :Dict [str ,threading .Thread ]={}
        self ._lock =threading .Lock ()
    def get_session_by_name (self ,process_name :str )->Optional [ISimpleAudioVolume ]:
        sessions =AudioUtilities .GetAllSessions ()
        for session in sessions :
            if session .Process and session .Process .name ().lower ()==process_name .lower ():
                volume =session ._ctl .QueryInterface (ISimpleAudioVolume )
                return volume
        return None
    def get_all_audio_sessions (self )->list :
        sessions =AudioUtilities .GetAllSessions ()
        result =[]
        for session in sessions :
            if session .Process :
                try :
                    volume =session ._ctl .QueryInterface (ISimpleAudioVolume )
                    current_vol =volume .GetMasterVolume ()
                    result .append ((session .Process .name (),current_vol *100 ))
                except :
                    pass
        return result
    def get_volume (self ,process_name :str )->Optional [float ]:
        session =self .get_session_by_name (process_name )
        if session :
            try :
                return session .GetMasterVolume ()*100
            except :
                return None
        return None
    def set_volume (self ,process_name :str ,volume :float ):
        session =self .get_session_by_name (process_name )
        if session :
            try :
                volume_normalized =max (0.0 ,min (1.0 ,volume /100.0 ))
                session .SetMasterVolume (volume_normalized ,None )
            except Exception as e :
                print (f"Error setting volume for {process_name }: {e }")
    def smooth_volume_change (self ,process_name :str ,target_volume :float ,
    duration_ms :int =500 ,save_original :bool =True ):
        with self ._lock :
            if process_name in self .transition_threads :
                pass
            thread =threading .Thread (
            target =self ._transition_worker ,
            args =(process_name ,target_volume ,duration_ms ,save_original ),
            daemon =True
            )
            self .transition_threads [process_name ]=thread
            thread .start ()
    def _transition_worker (self ,process_name :str ,target_volume :float ,
    duration_ms :int ,save_original :bool ):
        try :
            session =self .get_session_by_name (process_name )
            if not session :
                return
            current_volume =session .GetMasterVolume ()*100
            if save_original and process_name not in self .original_volumes :
                self .original_volumes [process_name ]=current_volume
            steps =max (10 ,duration_ms //50 )
            step_delay =duration_ms /1000.0 /steps
            volume_step =(target_volume -current_volume )/steps
            for i in range (steps ):
                new_volume =current_volume +volume_step *(i +1 )
                session .SetMasterVolume (new_volume /100.0 ,None )
                time .sleep (step_delay )
            session .SetMasterVolume (target_volume /100.0 ,None )
        except Exception as e :
            print (f"Error in volume transition for {process_name }: {e }")
        finally :
            with self ._lock :
                if process_name in self .transition_threads :
                    del self .transition_threads [process_name ]
    def restore_volume (self ,process_name :str ,duration_ms :int =500 ):
        if process_name in self .original_volumes :
            original =self .original_volumes [process_name ]
            self .smooth_volume_change (process_name ,original ,duration_ms ,save_original =False )
            del self .original_volumes [process_name ]
    def restore_all_volumes (self ,duration_ms :int =500 ):
        processes =list (self .original_volumes .keys ())
        for process_name in processes :
            self .restore_volume (process_name ,duration_ms )