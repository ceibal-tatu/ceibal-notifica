#!/usr/bin/python
from gi.repository import WebKit
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
import os
import json

import datetime
import time
from ceibal.notifier import env
from ceibal.notifier.data_base import Db
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import * 
from ceibal.notifier.message  import * 
from os.path import expanduser



class VentanaBoton(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Notificador de novedades Ceibal")
        self.image_btn = os.path.join (expanduser("~"),NOTIF_IMG_BTN)
        
        self.message_mgr = Messages()
        
        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        
        if self.message_mgr.get_first_unread() is None:
            print "No hay mensajes o estan todos leidos ..."
            return
    
        self.set_decorated(False)

        self.set_accept_focus(False)
        self.connect("delete-event", Gtk.main_quit)
        self.create_button()
        self.show_all()
        # especificar un tamanio fijo para la ventana si se quiere
        # mover esta seccion antes del show_all
        self.move(Gdk.Screen.get_default().get_width() - self.get_size()[0] ,0)
        Gtk.main()

    def create_button(self):
        self.button = Gtk.Button()
        self.button.connect("clicked", self.on_button_clicked)
        
        image = Gtk.Image()
        image.set_from_file(self.image_btn)
        image.show()
        self.button.add(image)
        
        self.add(self.button)
    
    def on_button_clicked(self, widget):
        visor = Visor()




class Visor(Gtk.Window):
 
    def __init__(self):
        self.width = 400
        self.height = 300

        #GObject.threads_init()
        Gtk.Window.__init__(self, title="Visor de novedades Ceibal")

        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        
        # Decorators
        self.set_decorated(False)

        self.resize(self.width,self.height)
        self.move(Gdk.Screen.get_default().get_width() - self.get_size()[0] ,0)

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
        self.sw = Gtk.ScrolledWindow()
        self.sw.set_size_request(0,(self.win.height - 20))
        self.sw.add(self.view)
        
        self.btn_leido = self.create_btn_leido()
        
        self.win.box.pack_start(self.sw, True, True, 0)
        self.win.box.pack_start(self.btn_leido, True, True, 0)
        
        
        self.message_mgr = Messages()
        self.current_msg = None
        self.show_msg('first')
        
    def create_btn_leido(self):
        button = Gtk.ToggleButton(label='Marcar como Leido')
        button.connect("toggled", self.btn_leido_cb, "Boton leido presionado")
        return button

    def btn_leido_cb(self, widget, data=None):
        if widget.get_active():
            widget.set_label('Leido')
        else:
            widget.set_label ('Marcar como Leido')

     
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


