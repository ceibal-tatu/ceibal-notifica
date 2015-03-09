#!/usr/bin/python
# -*- coding:utf-8 -*-
import webkit
import gtk
import os
import subprocess
import urlparse

from ceibal.notifier  import env
from ceibal.notifier.viewer  import *
from ceibal.notifier.message  import * 
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import * 



class VentanaBoton(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.image_btn = os.path.join (env.get_images_root(),NOTIF_IMG_BTN)

        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)

        self.set_decorated(False)
        self.set_accept_focus(False)
        self.connect("delete-event", gtk.main_quit)
        self.create_button()
        self.move(gtk.gdk.screen_width()- self.get_size()[0] ,0)
        self.show_all()
        gtk.main()


    def create_button(self):
        self.button = gtk.Button()
        self.button.connect("clicked", self.on_button_clicked)
        
        image = gtk.Image()
        image.set_from_file(self.image_btn)
        image.show()
        self.button.add(image) 
        
        self.add(self.button)

    def on_button_clicked(self, widget):
        visor = Visor()




class Visor(gtk.Window):
 
    def __init__(self):
        gtk.Window.__init__(self)
        (self.width, self.height) = get_window_size()

        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        
        # Decorators
        self.set_decorated(False)

        self.resize(self.width,self.height)
        self.set_accept_focus(False)
        self.box = gtk.VBox()
        self.add(self.box) 
        self.message_mgr = Messages()
        self.tool_bar    = ToolBar(self)
        self.html_viewer = WebViewer(self)
        self.move(gtk.gdk.screen_width()- self.get_size()[0] ,0)
        self.html_viewer.show_msg('first')
        self.show_all()


class WebViewer (WebViewerCommon):

    def __init__ (self,win):
        WebViewerCommon.__init__(self)
        self.win = win
        self.view = webkit.WebView()
        self.view.connect("navigation-policy-decision-requested",self.navigate)
        #self.view.set_full_content_zoom(True)
  
        self.sw = gtk.ScrolledWindow()
        self.sw.set_size_request(0,(self.win.height - 20))
        self.sw.add(self.view)
        self.btn_leido = self.create_btn_leido() 
        
        self.win.box.pack_start(self.sw, True, True, 0)
        self.win.box.pack_start(self.btn_leido, True, True, 0)
    
    def create_btn_leido(self):
        button = gtk.ToggleButton(label='Marcar como leída')
        button.connect("toggled", self.btn_leido_cb, "Boton leido presionado")
        return button





class ToolBar(ToolBarCommon):
    
    def __init__(self, win):
        self.tbar = gtk.Toolbar()
        self.tbar.set_style(gtk.TOOLBAR_ICONS)
        self.win = win
        self.win.box.pack_start(self.tbar, False, False, 0)
        
        self.back = gtk.ToolButton(gtk.STOCK_GO_BACK)
        self.back.connect("clicked", self.on_back_clicked)
        
        self.next = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        self.next.connect("clicked", self.on_next_clicked)
        
        self.close = gtk.ToolButton(gtk.STOCK_CLOSE)
        self.close.connect("clicked", self.on_close_clicked)
        
        check_item = gtk.ToolItem ()
        self.check_btn = gtk.CheckButton ()
        self.check_btn.set_label ('Mostrar todos')
        self.check_btn.connect ('toggled' , self.toggled)
        check_item.add (self.check_btn)

        sep = gtk.SeparatorToolItem()

        sep.props.draw = False
        sep.set_expand(True)
      
        msg_counter_item = gtk.ToolItem()
        self.msg_counter = gtk.Label() 
        msg_counter_item.add (self.msg_counter)

        self.tbar.insert(self.back, 0)
        self.tbar.insert(msg_counter_item, 1)
        self.tbar.insert(self.next, 2)
        self.tbar.insert(sep, 3)
        self.tbar.insert(check_item,4)
        self.tbar.insert(self.close, 5)

    def on_close_clicked(self, widget):
        self.win.destroy() 
        if self.win.message_mgr.get_first_unread() is None:
            gtk.main_quit()
