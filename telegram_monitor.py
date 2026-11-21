import asyncio
import threading
from typing import Callable ,Optional
from telethon import TelegramClient ,events
from telethon .tl .types import UpdateGroupCall ,UpdateGroupCallParticipants ,GroupCallParticipant
class TelegramVoiceMonitor :
    def __init__ (self ,api_id :str ,api_hash :str ,phone :str ,
    on_speaking_start :Callable ,on_speaking_end :Callable ):
        self .api_id =api_id
        self .api_hash =api_hash
        self .phone =phone
        self .on_speaking_start =on_speaking_start
        self .on_speaking_end =on_speaking_end
        self .client :Optional [TelegramClient ]=None
        self .loop :Optional [asyncio .AbstractEventLoop ]=None
        self .thread :Optional [threading .Thread ]=None
        self .is_running =False
        self .speaking_users =set ()
        self .active_calls ={}
    def start (self ):
        if self .is_running :
            return
        self .is_running =True
        self .thread =threading .Thread (target =self ._run_client ,daemon =True )
        self .thread .start ()
    def stop (self ):
        self .is_running =False
        if self .loop and self .client :
            asyncio .run_coroutine_threadsafe (self .client .disconnect (),self .loop )
    def _run_client (self ):
        try :
            self .loop =asyncio .new_event_loop ()
            asyncio .set_event_loop (self .loop )
            self .client =TelegramClient ('auto_volume_mixer',self .api_id ,self .api_hash )
            @self .client .on (events .Raw (types =[UpdateGroupCall ]))
            async def handle_group_call (event ):
                if hasattr (event ,'call'):
                    call_id =event .call .id
                    self .active_calls [call_id ]=event .call
                    print (f"Group call update: {call_id }")
            @self .client .on (events .Raw (types =[UpdateGroupCallParticipants ]))
            async def handle_participants (event ):
                try :
                    call_id =event .call .id
                    for participant in event .participants :
                        user_id =participant .peer .user_id if hasattr (participant .peer ,'user_id')else None
                        if not user_id :
                            continue
                        is_muted =participant .muted if hasattr (participant ,'muted')else True
                        if not is_muted and user_id not in self .speaking_users :
                            self .speaking_users .add (user_id )
                            print (f"User {user_id } started speaking in call {call_id }")
                            if len (self .speaking_users )==1 :
                                self .on_speaking_start ()
                        elif is_muted and user_id in self .speaking_users :
                            self .speaking_users .remove (user_id )
                            print (f"User {user_id } stopped speaking in call {call_id }")
                            if len (self .speaking_users )==0 :
                                self .on_speaking_end ()
                        if hasattr (participant ,'left')and participant .left :
                            if user_id in self .speaking_users :
                                self .speaking_users .remove (user_id )
                                if len (self .speaking_users )==0 :
                                    self .on_speaking_end ()
                            print (f"User {user_id } left call {call_id }")
                except Exception as e :
                    print (f"Error handling Telegram participants: {e }")
            async def main ():
                await self .client .start (phone =self .phone )
                print ("Клиент Telegram подключен")
                await self .client .run_until_disconnected ()
            self .loop .run_until_complete (main ())
        except Exception as e :
            print (f"Telegram client error: {e }")
            self .is_running =False