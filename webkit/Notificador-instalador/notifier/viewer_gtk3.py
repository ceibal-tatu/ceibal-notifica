#!/usr/bin/python
# -*- coding:utf-8 -*-
from gi.repository import WebKit
from gi.repository import Gtk
from gi.repository import Gdk
import os
import urlparse

from ceibal.notifier import env
from ceibal.notifier.viewer import *
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import * 
from ceibal.notifier.message  import * 



class VentanaBoton(VentanaBotonCommon):

    def __init__(self):
        VentanaBotonCommon.__init__(self)
        self.win = Gtk.Window(title="Notificador de novedades Ceibal")
        
        #Evita que aparezca en la lista de ventanas
        self.win.set_skip_taskbar_hint(True)
        
        self.win.set_decorated(False)

        self.win.set_accept_focus(False)
        self.win.connect("delete-event", Gtk.main_quit)
        self.create_button()
        (pos_h, pos_v) = get_window_pos (Gdk.Screen.get_default().get_width() - self.win.get_size()[0])
        self.win.move(pos_h, pos_v)
        self.win.show_all()
        Gtk.main()

    def create_button(self):
        self.button = Gtk.Button()
        self.button.connect("clicked", self.on_button_clicked)
        self.button.connect("enter", self.on_button_pointer)
        
        self.image_btn = Gtk.Image()
        icon_img = self.get_image_btn()
        self.image_btn.set_from_file(icon_img)
        self.image_btn.show()
        self.button.add(self.image_btn)
        self.win.add(self.button)
    
    def refresh_button(self):
        icon_img = self.get_image_btn()
        self.image_btn.set_from_file(icon_img)
        self.image_btn.show()
    
    def on_button_clicked(self, widget):
        visor = Visor(self)




class Visor(Gtk.Window):
 
    def __init__(self, parent):

        #GObject.threads_init()
        Gtk.Window.__init__(self, title="Visor de novedades Ceibal")
        (self.width, self.height) = get_window_size()
        
        self.ventana_btn = parent
        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        
        # Decorators
        self.set_decorated(False)

        self.resize(self.width,self.height)
        (pos_h, pos_v) = get_window_pos (Gdk.Screen.get_default().get_width() - self.width)
        self.move(pos_h, pos_v)

        self.set_accept_focus(False)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.message_mgr = Messages()
        self.add(self.box) 
        self.tool_bar    = ToolBar(self)
        self.html_viewer = WebViewer(self)
        self.html_viewer.show_msg('first')
        self.show_all()



class WebViewer (WebViewerCommon):

    def __init__ (self,win):
        WebViewerCommon.__init__(self)
        self.win = win
        self.view = WebKit.WebView()
        self.view.connect("navigation-policy-decision-requested",self.navigate)
        self.sw = Gtk.ScrolledWindow()
        self.sw.set_size_request(0,(self.win.height - 20))
        self.sw.add(self.view)
        
        self.btn_leido = self.create_btn_leido()
        
        self.win.box.pack_start(self.sw, True, True, 0)
        self.win.box.pack_start(self.btn_leido, True, True, 0)
        
    def create_btn_leido(self):
        button = Gtk.ToggleButton(label='Marcar como leída')
        button.connect("toggled", self.btn_leido_cb, "Boton leido presionado")
        return button



class ToolBar(ToolBarCommon):
    
    def __init__(self, win):
        self.tbar = Gtk.Toolbar()
        self.tbar.set_style(Gtk.ToolbarStyle.ICONS)
        self.win = win
        self.win.box.pack_start(self.tbar, False, False, 0)
        
        self.back = Gtk.ToolButton(Gtk.STOCK_GO_BACK, label="Anterior")
        self.back.connect("clicked", self.on_back_clicked)
        
        self.next = Gtk.ToolButton(Gtk.STOCK_GO_FORWARD,label="Siguiente")
        self.next.connect("clicked", self.on_next_clicked)
        
        self.close = Gtk.ToolButton(Gtk.STOCK_CLOSE,label="Cerrar")
        self.close.connect("clicked", self.on_close_clicked)
        
        check_item = Gtk.ToolItem ()
        self.check_btn = Gtk.CheckButton ()
        self.check_btn.set_label ('Mostrar todos')
        self.check_btn.connect ('toggled' , self.toggled)
        check_item.add (self.check_btn)

        sep = Gtk.SeparatorToolItem()

        sep.props.draw = False
        sep.set_expand(True)

        msg_counter_item = Gtk.ToolItem()
        self.msg_counter = Gtk.Label() 
        msg_counter_item.add (self.msg_counter)

        self.tbar.insert(self.back, 0)
        self.tbar.insert(msg_counter_item,1)
        self.tbar.insert(self.next, 2)
        self.tbar.insert(sep, 3)
        self.tbar.insert(check_item,4)
        self.tbar.insert(self.close, 5)


