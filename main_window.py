import sys
import os
from PyQt5 .QtWidgets import (QApplication ,QMainWindow ,QWidget ,QVBoxLayout ,
QHBoxLayout ,QLabel ,QSlider ,QPushButton ,
QCheckBox ,QComboBox ,QGroupBox ,QScrollArea ,
QListWidget ,QListWidgetItem ,QMessageBox ,QFrame )
from PyQt5 .QtCore import Qt ,QTimer ,pyqtSignal
from PyQt5 .QtGui import QIcon
import pystray
from PIL import Image ,ImageDraw
from audio_controller import AudioController
from config_manager import ConfigManager
from discord_monitor import DiscordVoiceMonitor
from telegram_monitor import TelegramVoiceMonitor
from dotenv import load_dotenv
import time
class ProgramWidget (QWidget ):
    volume_changed =pyqtSignal (str ,int )
    enabled_changed =pyqtSignal (str ,bool )
    removed =pyqtSignal (str )
    def __init__ (self ,process_name :str ,config :dict ,parent =None ):
        super ().__init__ (parent )
        self .process_name =process_name
        self .init_ui (config )
    def init_ui (self ,config :dict ):
        layout =QHBoxLayout ()
        layout .setContentsMargins (5 ,5 ,5 ,5 )
        self .enabled_checkbox =QCheckBox ()
        self .enabled_checkbox .setChecked (config .get ('enabled',True ))
        self .enabled_checkbox .stateChanged .connect (self ._on_enabled_changed )
        layout .addWidget (self .enabled_checkbox )
        self .name_label =QLabel (self .process_name )
        self .name_label .setMinimumWidth (150 )
        layout .addWidget (self .name_label )
        self .volume_slider =QSlider (Qt .Horizontal )
        self .volume_slider .setMinimum (0 )
        self .volume_slider .setMaximum (100 )
        self .volume_slider .setValue (config .get ('volume_percent',50 ))
        self .volume_slider .setTickPosition (QSlider .TicksBelow )
        self .volume_slider .setTickInterval (10 )
        self .volume_slider .valueChanged .connect (self ._on_volume_changed )
        layout .addWidget (self .volume_slider ,1 )
        self .value_label =QLabel (f"{self .volume_slider .value ()}%")
        self .value_label .setMinimumWidth (40 )
        layout .addWidget (self .value_label )
        self .remove_button =QPushButton ("✕")
        self .remove_button .setMaximumWidth (30 )
        self .remove_button .clicked .connect (self ._on_remove )
        layout .addWidget (self .remove_button )
        self .setLayout (layout )
    def _on_volume_changed (self ,value :int ):
        self .value_label .setText (f"{value }%")
        self .volume_changed .emit (self .process_name ,value )
    def _on_enabled_changed (self ,state :int ):
        enabled =state ==Qt .Checked
        self .enabled_changed .emit (self .process_name ,enabled )
    def _on_remove (self ):
        self .removed .emit (self .process_name )
class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .audio_controller =AudioController ()
        self .config_manager =ConfigManager ()
        self .discord_monitor =None
        self .telegram_monitor =None
        self .tray_icon =None
        self .is_speaking_active =False
        self .restore_timer =QTimer ()
        self .restore_timer .setSingleShot (True )
        self .restore_timer .timeout .connect (self ._restore_volumes )
        load_dotenv ()
        self .init_ui ()
        self .load_programs ()
        self .setup_monitors ()
        self .update_timer =QTimer ()
        self .update_timer .timeout .connect (self .refresh_audio_sessions )
        self .update_timer .start (5000 )
    def init_ui (self ):
        self .setWindowTitle ("Автоматический микшер громкости")
        self .setGeometry (100 ,100 ,700 ,600 )
        central_widget =QWidget ()
        self .setCentralWidget (central_widget )
        main_layout =QVBoxLayout (central_widget )
        status_group =QGroupBox ("Status")
        status_layout =QVBoxLayout ()
        self .discord_status_label =QLabel ("Дискорд: Отключено")
        self .telegram_status_label =QLabel ("Телеграмма: Отключена")
        self .speaking_status_label =QLabel ("Голосовая активность: нет")
        status_layout .addWidget (self .discord_status_label )
        status_layout .addWidget (self .telegram_status_label )
        status_layout .addWidget (self .speaking_status_label )
        status_group .setLayout (status_layout )
        main_layout .addWidget (status_group )
        settings_group =QGroupBox ("Settings")
        settings_layout =QVBoxLayout ()
        discord_layout =QHBoxLayout ()
        self .discord_enabled_checkbox =QCheckBox ("Включить мониторинг Discord")
        self .discord_enabled_checkbox .setChecked (self .config_manager .get ('discord_enabled',False ))
        self .discord_enabled_checkbox .stateChanged .connect (self ._on_discord_enabled_changed )
        discord_layout .addWidget (self .discord_enabled_checkbox )
        settings_layout .addLayout (discord_layout )
        telegram_layout =QHBoxLayout ()
        self .telegram_enabled_checkbox =QCheckBox ("Включить мониторинг Telegram")
        self .telegram_enabled_checkbox .setChecked (self .config_manager .get ('telegram_enabled',False ))
        self .telegram_enabled_checkbox .stateChanged .connect (self ._on_telegram_enabled_changed )
        telegram_layout .addWidget (self .telegram_enabled_checkbox )
        settings_layout .addLayout (telegram_layout )
        smooth_layout =QHBoxLayout ()
        self .smooth_transition_checkbox =QCheckBox ("Плавные переходы громкости")
        self .smooth_transition_checkbox .setChecked (self .config_manager .get ('smooth_transition',True ))
        self .smooth_transition_checkbox .stateChanged .connect (self ._on_smooth_transition_changed )
        smooth_layout .addWidget (self .smooth_transition_checkbox )
        settings_layout .addLayout (smooth_layout )
        settings_group .setLayout (settings_layout )
        main_layout .addWidget (settings_group )
        programs_group =QGroupBox ("Programs")
        programs_layout =QVBoxLayout ()
        add_layout =QHBoxLayout ()
        add_layout .addWidget (QLabel ("Добавить программу:"))
        self .program_combo =QComboBox ()
        self .program_combo .setEditable (True )
        add_layout .addWidget (self .program_combo ,1 )
        self .add_button =QPushButton ("Add")
        self .add_button .clicked .connect (self ._on_add_program )
        add_layout .addWidget (self .add_button )
        self .refresh_button =QPushButton ("🔄 Обновить")
        self .refresh_button .clicked .connect (self .refresh_audio_sessions )
        add_layout .addWidget (self .refresh_button )
        programs_layout .addLayout (add_layout )
        scroll_area =QScrollArea ()
        scroll_area .setWidgetResizable (True )
        scroll_area .setMinimumHeight (200 )
        self .programs_container =QWidget ()
        self .programs_layout =QVBoxLayout (self .programs_container )
        self .programs_layout .addStretch ()
        scroll_area .setWidget (self .programs_container )
        programs_layout .addWidget (scroll_area )
        programs_group .setLayout (programs_layout )
        main_layout .addWidget (programs_group ,1 )
        button_layout =QHBoxLayout ()
        self .test_button =QPushButton ("Уменьшение тестового объема")
        self .test_button .clicked .connect (self ._on_test )
        button_layout .addWidget (self .test_button )
        self .restore_button =QPushButton ("Восстановить все тома")
        self .restore_button .clicked .connect (self ._on_restore_all )
        button_layout .addWidget (self .restore_button )
        button_layout .addStretch ()
        self .minimize_button =QPushButton ("Свернуть в трей")
        self .minimize_button .clicked .connect (self .hide_to_tray )
        button_layout .addWidget (self .minimize_button )
        main_layout .addLayout (button_layout )
        self .refresh_audio_sessions ()
    def setup_monitors (self ):
        if self .config_manager .get ('discord_enabled',False ):
            discord_token =os .getenv ('DISCORD_TOKEN')
            if discord_token :
                try :
                    self .discord_monitor =DiscordVoiceMonitor (
                    discord_token ,
                    self ._on_speaking_start ,
                    self ._on_speaking_end
                    )
                    self .discord_monitor .start ()
                    self .discord_status_label .setText ("Дискорд: Соединение...")
                    QTimer .singleShot (3000 ,lambda :self .discord_status_label .setText ("Дискорд: подключено"))
                except Exception as e :
                    self .discord_status_label .setText (f"Discord: Error - {str (e )}")
        if self .config_manager .get ('telegram_enabled',False ):
            api_id =os .getenv ('TELEGRAM_API_ID')
            api_hash =os .getenv ('TELEGRAM_API_HASH')
            phone =os .getenv ('TELEGRAM_PHONE')
            if api_id and api_hash and phone :
                try :
                    self .telegram_monitor =TelegramVoiceMonitor (
                    api_id ,api_hash ,phone ,
                    self ._on_speaking_start ,
                    self ._on_speaking_end
                    )
                    self .telegram_monitor .start ()
                    self .telegram_status_label .setText ("Телеграм: Подключение...")
                    QTimer .singleShot (3000 ,lambda :self .telegram_status_label .setText ("Телеграмма: На связи"))
                except Exception as e :
                    self .telegram_status_label .setText (f"Telegram: Error - {str (e )}")
    def load_programs (self ):
        programs =self .config_manager .get_all_programs ()
        for process_name ,config in programs .items ():
            self ._add_program_widget (process_name ,config )
    def refresh_audio_sessions (self ):
        sessions =self .audio_controller .get_all_audio_sessions ()
        current_items =[self .program_combo .itemText (i )for i in range (self .program_combo .count ())]
        for process_name ,volume in sessions :
            if process_name and process_name not in current_items :
                self .program_combo .addItem (process_name )
    def _add_program_widget (self ,process_name :str ,config :dict ):
        widget =ProgramWidget (process_name ,config )
        widget .volume_changed .connect (self ._on_program_volume_changed )
        widget .enabled_changed .connect (self ._on_program_enabled_changed )
        widget .removed .connect (self ._on_program_removed )
        self .programs_layout .insertWidget (self .programs_layout .count ()-1 ,widget )
    def _on_add_program (self ):
        process_name =self .program_combo .currentText ().strip ()
        if not process_name :
            return
        programs =self .config_manager .get_all_programs ()
        if process_name in programs :
            QMessageBox .warning (self ,"Warning",f"{process_name } is already in the list")
            return
        self .config_manager .add_program (process_name )
        self .config_manager .save ()
        config =self .config_manager .get_program_config (process_name )
        self ._add_program_widget (process_name ,config )
    def _on_program_volume_changed (self ,process_name :str ,volume :int ):
        self .config_manager .update_program_setting (process_name ,'volume_percent',volume )
        self .config_manager .save ()
    def _on_program_enabled_changed (self ,process_name :str ,enabled :bool ):
        self .config_manager .update_program_setting (process_name ,'enabled',enabled )
        self .config_manager .save ()
    def _on_program_removed (self ,process_name :str ):
        reply =QMessageBox .question (
        self ,'Подтвердить удаление',
        f'Remove {process_name } from the list?',
        QMessageBox .Yes |QMessageBox .No
        )
        if reply ==QMessageBox .Yes :
            self .config_manager .remove_program (process_name )
            self .config_manager .save ()
            for i in range (self .programs_layout .count ()):
                widget =self .programs_layout .itemAt (i ).widget ()
                if isinstance (widget ,ProgramWidget )and widget .process_name ==process_name :
                    self .programs_layout .removeWidget (widget )
                    widget .deleteLater ()
                    break
    def _on_discord_enabled_changed (self ,state :int ):
        enabled =state ==Qt .Checked
        self .config_manager .set ('discord_enabled',enabled )
        self .config_manager .save ()
        if enabled and not self .discord_monitor :
            self .setup_monitors ()
        elif not enabled and self .discord_monitor :
            self .discord_monitor .stop ()
            self .discord_monitor =None
            self .discord_status_label .setText ("Дискорд: отключен")
    def _on_telegram_enabled_changed (self ,state :int ):
        enabled =state ==Qt .Checked
        self .config_manager .set ('telegram_enabled',enabled )
        self .config_manager .save ()
        if enabled and not self .telegram_monitor :
            self .setup_monitors ()
        elif not enabled and self .telegram_monitor :
            self .telegram_monitor .stop ()
            self .telegram_monitor =None
            self .telegram_status_label .setText ("Телеграмма: отключена")
    def _on_smooth_transition_changed (self ,state :int ):
        enabled =state ==Qt .Checked
        self .config_manager .set ('smooth_transition',enabled )
        self .config_manager .save ()
    def _on_speaking_start (self ):
        print ("Обнаружена речь – уменьшение громкости")
        self .is_speaking_active =True
        self .speaking_status_label .setText ("Голосовая активность: обнаружена речь")
        if self .restore_timer .isActive ():
            self .restore_timer .stop ()
        self ._reduce_volumes ()
    def _on_speaking_end (self ):
        print ("Говорение закончилось - восстановлю тома")
        self .speaking_status_label .setText ("Голосовая активность: Тишина")
        delay =self .config_manager .get ('restore_delay_seconds',2 )*1000
        self .restore_timer .start (delay )
    def _reduce_volumes (self ):
        programs =self .config_manager .get_all_programs ()
        duration =self .config_manager .get ('transition_duration_ms',500 )
        smooth =self .config_manager .get ('smooth_transition',True )
        for process_name ,config in programs .items ():
            if config .get ('enabled',True ):
                target_volume =config .get ('volume_percent',50 )
                if smooth :
                    self .audio_controller .smooth_volume_change (
                    process_name ,target_volume ,duration ,save_original =True
                    )
                else :
                    self .audio_controller .set_volume (process_name ,target_volume )
    def _restore_volumes (self ):
        if self .is_speaking_active :
            print ("Восстановление томов")
            self .is_speaking_active =False
            self .speaking_status_label .setText ("Голосовая активность: нет")
            duration =self .config_manager .get ('transition_duration_ms',500 )
            self .audio_controller .restore_all_volumes (duration )
    def _on_test (self ):
        self ._on_speaking_start ()
        QTimer .singleShot (3000 ,self ._on_speaking_end )
    def _on_restore_all (self ):
        self .restore_timer .stop ()
        self ._restore_volumes ()
    def hide_to_tray (self ):
        if not self .tray_icon :
            self .setup_tray_icon ()
        self .hide ()
        if self .tray_icon :
            self .tray_icon .visible =True
    def setup_tray_icon (self ):
        icon_image =self ._create_icon ()
        menu =pystray .Menu (
        pystray .MenuItem ("Show",self .show_from_tray ),
        pystray .MenuItem ("Exit",self .quit_application )
        )
        self .tray_icon =pystray .Icon ("AutoVolumeMixer",icon_image ,"Автоматический микшер громкости",menu )
        import threading
        threading .Thread (target =self .tray_icon .run ,daemon =True ).start ()
    def _create_icon (self ):
        width =64
        height =64
        image =Image .new ('RGBA',(width ,height ),(0 ,0 ,0 ,0 ))
        dc =ImageDraw .Draw (image )
        dc .rectangle ([10 ,20 ,25 ,44 ],fill ='white')
        dc .polygon ([25 ,20 ,45 ,10 ,45 ,54 ,25 ,44 ],fill ='white')
        dc .arc ([48 ,15 ,60 ,27 ],start =300 ,end =60 ,fill ='white',width =3 )
        dc .arc ([48 ,37 ,60 ,49 ],start =60 ,end =300 ,fill ='white',width =3 )
        return image
    def show_from_tray (self ):
        self .show ()
        self .activateWindow ()
        if self .tray_icon :
            self .tray_icon .visible =False
    def quit_application (self ):
        self .audio_controller .restore_all_volumes (0 )
        if self .discord_monitor :
            self .discord_monitor .stop ()
        if self .telegram_monitor :
            self .telegram_monitor .stop ()
        if self .tray_icon :
            self .tray_icon .stop ()
        QApplication .quit ()
    def closeEvent (self ,event ):
        if self .config_manager .get ('minimize_to_tray',True ):
            event .ignore ()
            self .hide_to_tray ()
        else :
            self .quit_application ()