import discord
import asyncio
from typing import Callable ,Optional
import threading
class DiscordVoiceMonitor :
    def __init__ (self ,token :str ,on_speaking_start :Callable ,on_speaking_end :Callable ):
        self .token =token
        self .on_speaking_start =on_speaking_start
        self .on_speaking_end =on_speaking_end
        self .client :Optional [discord .Client ]=None
        self .loop :Optional [asyncio .AbstractEventLoop ]=None
        self .thread :Optional [threading .Thread ]=None
        self .is_running =False
        self .speaking_users =set ()
    def start (self ):
        if self .is_running :
            return
        self .is_running =True
        self .thread =threading .Thread (target =self ._run_bot ,daemon =True )
        self .thread .start ()
    def stop (self ):
        self .is_running =False
        if self .loop and self .client :
            asyncio .run_coroutine_threadsafe (self .client .close (),self .loop )
    def _run_bot (self ):
        intents =discord .Intents .default ()
        intents .voice_states =True
        intents .guilds =True
        intents .members =True
        self .client =discord .Client (intents =intents )
        @self .client .event
        async def on_ready ():
            print (f'Discord bot connected as {self .client .user }')
        @self .client .event
        async def on_voice_state_update (member ,before ,after ):
            if before .channel !=after .channel :
                if after .channel :
                    print (f'{member .name } joined voice channel: {after .channel .name }')
                elif before .channel :
                    print (f'{member .name } left voice channel: {before .channel .name }')
                    if member .id in self .speaking_users :
                        self .speaking_users .remove (member .id )
                        if len (self .speaking_users )==0 :
                            self .on_speaking_end ()
            if before .self_mute !=after .self_mute :
                if after .self_mute :
                    print (f'{member .name } muted themselves')
                    if member .id in self .speaking_users :
                        self .speaking_users .remove (member .id )
                        if len (self .speaking_users )==0 :
                            self .on_speaking_end ()
                else :
                    print (f'{member .name } unmuted themselves')
            if before .self_deaf !=after .self_deaf or before .deaf !=after .deaf :
                pass
        @self .client .event
        async def on_voice_update (member ,before ,after ):
            pass
        try :
            self .loop =asyncio .new_event_loop ()
            asyncio .set_event_loop (self .loop )
            self .loop .run_until_complete (self .client .start (self .token ))
        except Exception as e :
            print (f"Discord bot error: {e }")
            self .is_running =False
class DiscordUserMonitor :
    def __init__ (self ,on_speaking_start :Callable ,on_speaking_end :Callable ):
        self .on_speaking_start =on_speaking_start
        self .on_speaking_end =on_speaking_end
        self .speaking =False
        self .check_interval =0.5
        self .is_running =False
    def start (self ):
        self .is_running =True
        print ("Мониторинг учетных записей пользователей не реализован (согласно Discord ToS)")
        print ("Using bot-based monitoring instead (limited to voice state changes)")
    def stop (self ):
        self .is_running =False