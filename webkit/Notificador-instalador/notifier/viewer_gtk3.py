#!/usr/bin/python
from gi.repository import WebKit
from gi.repository import Gtk
from gi.repository import GObject
import os
import json

import datetime
import time
from ceibal.notifier import env
from ceibal.notifier.data_base import Db
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import READ_FILE,DB_FILE,IMAGEN_NOTOFY,BTN_GENERAL,BTN_LINK,TIME_ENTRE_MSJ, TIME_ESPERA, FUNCIONES_PRIORIDAD



class Messages:
    db = None

    def __init__(self):
        if Messages.db is None:
            db_filename = os.path.join(env.get_data_root(),DB_FILE)        
            Messages.db = Db(db_filename)


    def _save_notification_read(self, id):
        file_name = os.path.join(env.get_data_root(),READ_FILE)    
        try:
            # Cargo el diccionario desde el archivo json
            fp = open(file_name, "r")
            notif_read_record = json.load(fp)
            fp.close()
            
            # Borro el archivo json
            open(file_name,'w').close()
            fp = open(file_name,'r+')
        except:
            # El archivo json no existe, lo creo.
            fp = open(file_name, "w+")
            notif_read_record = {}
        
        notif_read_record[id] = 'read'
        json.dump(notif_read_record, fp)
        fp.flush()
        fp.close()
        

    def _check_notification_is_unread (self, message):
        id = str (message['id'])
        
        file_name = os.path.join(env.get_data_root(),READ_FILE)    
        try:
            fp = open(file_name, "r") 
            notif_read_record = json.load(fp)
        except:
            print "No existe el archivo de registro ...."
            return True
          
        if fp is not None:
          fp.close()

        if id in notif_read_record:
            return notif_read_record[id] == 'unread'
        else:
            print "No encuentro id en el registro ..." + id
            return True

    def _date_valid(self,message):
        '''
        @param message: Mensaje a validar.
        
        @summary: Valida si el mensaje ya expiro.
        
        @return: Verdadero si esta vigente el mensaje.
        '''
        expires = message["vencimiento"]
        today = datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
        return today <= expires


    def get_first_unread(self, args={}):
        messages = filter(self._date_valid,Messages.db.get_messages(args))
        messages_unread = filter(self._check_notification_is_unread, messages)
        if len(messages_unread) > 0:
            return messages_unread[0]
        else:
            return None 
    
    def get_next_unread(self, message):
        messages = filter(self._date_valid,Messages.db.get_messages({}))
        messages_unread = filter(self._check_notification_is_unread, messages)
        
        for msg in messages_unread:
            if msg['id'] > message['id']:
                return msg
        else:
            return None 
    
    def get_prev_unread(self, message):
        messages = filter(self._date_valid,Messages.db.get_messages({}))
        messages_unread = filter(self._check_notification_is_unread, messages)

        msg_prev = None 
        for msg in messages_unread:
            if msg['id'] < message['id']:
                msg_prev = msg
            else:
                return msg_prev
 
        return msg_prev 
       
   
    def get_all(self):
        return Messages.db.get_messages({})
 
    def get_test_message(self):
        wdir = os.path.dirname(os.path.abspath(__file__))
        return ('file://' + os.path.join(wdir, 'message.html'))
    
    def set_read(self, message):
        self._save_notification_read(message['id'])





class VentanaBoton(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Notificador de novedades Ceibal")
        self.message_mgr = Messages()
        
        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        
        if self.message_mgr.get_first_unread() is None:
            return
    
        self.set_decorated(False)
        self.move(950,20)
        self.set_accept_focus(False)
        self.connect("delete-event", Gtk.main_quit)
        self.create_button()
        self.show_all()
        Gtk.main()


    def create_button(self):
        self.button = Gtk.Button(label="Novedades Ceibal")
        self.button.connect("clicked", self.on_button_clicked)
        self.add(self.button)

    def on_button_clicked(self, widget):
        visor = Visor()




class Visor(Gtk.Window):
 
    def __init__(self):
        #GObject.threads_init()
        Gtk.Window.__init__(self, title="Visor de novedades Ceibal")

        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        
        # Decorators
        self.set_decorated(False)

        self.resize(400,300)
        self.move(900,20)
        self.set_accept_focus(False)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box) 
        self.tool_bar    = ToolBar(self)
        self.html_viewer = WebViewer(self)
        self.show_all()



class WebViewer:

    def __init__ (self,win):
        self.win = win
        self.view = WebKit.WebView()
        self.win.box.pack_start(self.view, True, True, 0)
        self.message_mgr = Messages()
        self.current_msg = None
        self.show_msg('first')
         
    def show_msg (self, pos):
        
        if pos == 'next':
            current_msg = self.message_mgr.get_next_unread(self.current_msg)
        elif pos == 'prev':
            current_msg = self.message_mgr.get_prev_unread(self.current_msg)
        elif pos == 'first':
            current_msg = self.message_mgr.get_first_unread()
        else:
            current_msg = None

        if current_msg is not None:
            self.current_msg = current_msg
            self.win.tool_bar.clean_read_check()
            self.view.load_string(self.current_msg['html'], 'text/html', 'UTF-8','/')
    
    def set_msg_read(self):
        self.message_mgr.set_read(self.current_msg)

class ToolBar(Gtk.Toolbar):
    
    def __init__(self, win):
        Gtk.Toolbar.__init__(self)
        self.set_style(Gtk.ToolbarStyle.ICONS)
        self.win = win
        self.win.box.pack_start(self, False, False, 0)
        
        self.back = Gtk.ToolButton(Gtk.STOCK_GO_BACK, label="Anterior")
        self.back.connect("clicked", self.on_back_clicked)
        
        self.next = Gtk.ToolButton(Gtk.STOCK_GO_FORWARD,label="Siguiente")
        self.next.connect("clicked", self.on_next_clicked)
        
        self.close = Gtk.ToolButton(Gtk.STOCK_CLOSE,label="Cerrar")
        self.close.connect("clicked", self.on_close_clicked)
        
        check_item = Gtk.ToolItem ()
        self.check_btn = Gtk.CheckButton ()
        self.check_btn.set_label ('Leido')
        self.check_btn.connect ('toggled' , self.toggled)
        check_item.add (self.check_btn)

        sep = Gtk.SeparatorToolItem()

        sep.props.draw = False
        sep.set_expand(True)

        self.insert(self.back, 0)
        self.insert(self.next, 1)
        self.insert(sep, 2)
        self.insert(check_item,3)
        self.insert(self.close, 4)

    def clean_read_check(self):
        self.check_btn.set_active(False)

    def toggled (self, obj):
         if obj.get_active ():
            self.win.html_viewer.set_msg_read()
 
    def on_next_clicked(self, widget):
        print("Siguiente")
        self.win.html_viewer.show_msg('next')

    def on_back_clicked(self, widget):
        print("Atras")            
        self.win.html_viewer.show_msg('prev')
    
    def on_close_clicked(self, widget):
        print("Goodbye")            
        self.win.destroy() 
        message_mgr = Messages()
        if message_mgr.get_first_unread() is None:
            Gtk.main_quit()


