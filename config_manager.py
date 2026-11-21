import json
import os
from typing import Dict ,Any
class ConfigManager :
    def __init__ (self ,config_file :str ="config.json"):
        self .config_file =config_file
        self .config :Dict [str ,Any ]=self ._load_default_config ()
        self .load ()
    def _load_default_config (self )->Dict [str ,Any ]:
        return {
        "programs":{},
        "smooth_transition":True ,
        "transition_duration_ms":500 ,
        "restore_delay_seconds":2 ,
        "discord_enabled":False ,
        "telegram_enabled":False ,
        "minimize_to_tray":True ,
        "start_minimized":False
        }
    def load (self ):
        if os .path .exists (self .config_file ):
            try :
                with open (self .config_file ,'r',encoding ='utf-8')as f :
                    loaded_config =json .load (f )
                    self .config .update (loaded_config )
                print (f"Configuration loaded from {self .config_file }")
            except Exception as e :
                print (f"Error loading configuration: {e }")
                print ("Использование конфигурации по умолчанию")
        else :
            print ("Файл конфигурации не найден, используются настройки по умолчанию")
    def save (self ):
        try :
            with open (self .config_file ,'w',encoding ='utf-8')as f :
                json .dump (self .config ,f ,indent =4 ,ensure_ascii =False )
            print (f"Configuration saved to {self .config_file }")
        except Exception as e :
            print (f"Error saving configuration: {e }")
    def get (self ,key :str ,default :Any =None )->Any :
        return self .config .get (key ,default )
    def set (self ,key :str ,value :Any ):
        self .config [key ]=value
    def add_program (self ,process_name :str ,enabled :bool =True ,
    volume_percent :int =50 ,original_volume :float =100 ):
        if "programs"not in self .config :
            self .config ["programs"]={}
        self .config ["programs"][process_name ]={
        "enabled":enabled ,
        "volume_percent":volume_percent ,
        "original_volume":original_volume
        }
    def remove_program (self ,process_name :str ):
        if "programs"in self .config and process_name in self .config ["programs"]:
            del self .config ["programs"][process_name ]
    def get_program_config (self ,process_name :str )->Dict [str ,Any ]:
        if "programs"not in self .config :
            self .config ["programs"]={}
        return self .config ["programs"].get (process_name ,{
        "enabled":True ,
        "volume_percent":50 ,
        "original_volume":100
        })
    def get_all_programs (self )->Dict [str ,Dict [str ,Any ]]:
        return self .config .get ("programs",{})
    def update_program_setting (self ,process_name :str ,key :str ,value :Any ):
        if "programs"not in self .config :
            self .config ["programs"]={}
        if process_name not in self .config ["programs"]:
            self .config ["programs"][process_name ]={
            "enabled":True ,
            "volume_percent":50 ,
            "original_volume":100
            }
        self .config ["programs"][process_name ][key ]=value