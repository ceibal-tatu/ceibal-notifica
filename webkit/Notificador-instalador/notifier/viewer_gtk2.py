#!/usr/bin/python
# -*- coding:utf-8 -*-
import webkit
import gtk
import os
import subprocess
import urlparse

from ceibal.notifier  import env
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


class WebViewer:

    def __init__ (self,win):
        self.mode = 'unread'
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
        
        self.current_msg = None
            
    
    def create_btn_leido(self):
        button = gtk.ToggleButton(label='Marcar como leída')
        button.connect("toggled", self.btn_leido_cb, "Boton leido presionado")
        return button

    def btn_leido_cb(self, widget, data=None):
        if widget.get_active():
            self.win.message_mgr.set_read(self.current_msg)
            widget.set_label('Marcar como no leída')
        else:
            self.win.message_mgr.set_unread(self.current_msg)
            widget.set_label ('Marcar como leída')

    def update_read_button(self, msg):
        if msg is None:
            self.btn_leido.set_sensitive(False)
        else:
            self.btn_leido.set_sensitive(True)
            if self.win.message_mgr.is_unread(msg):
                self.btn_leido.set_active(False)        
            else:     
                self.btn_leido.set_active(True)        
    
    def show_msg (self, pos):
        if self.current_msg is None:
            self.current_msg = self.win.message_mgr.get_first()

        if pos == 'next':
            current_msg = self.win.message_mgr.get_next_unread(self.current_msg) if (self.mode == 'unread') else self.win.message_mgr.get_next(self.current_msg)
        elif pos == 'prev':
            current_msg = self.win.message_mgr.get_prev_unread(self.current_msg) if (self.mode == 'unread') else self.win.message_mgr.get_prev(self.current_msg)
        elif pos == 'first':
            current_msg = self.win.message_mgr.get_first_unread() if (self.mode == 'unread') else self.win.message_mgr.get_first()
        else:
            current_msg = None
            

        if current_msg is not None:
            self.current_msg = current_msg
            self.view.load_string(current_msg['html'], 'text/html', 'UTF-8','/')
            self.win.tool_bar.update_msg_counter(str(self.win.message_mgr.get_pos(self.mode, current_msg)) , str(self.win.message_mgr.get_total(self.mode)))
 
        self.win.tool_bar.update_next_back_buttons(current_msg)
        self.update_read_button(current_msg)
    
    def set_mode(self, mode):
        self.mode = mode

    def navigate(self, view, frame, request, action, decision):
        uri = request.get_uri()
        parts = urlparse.urlsplit(uri)
        if parts.scheme and parts.netloc: 
            open_external_browser(uri)
            return True

        return False




class ToolBar(gtk.Toolbar):
    
    def __init__(self, win):
        gtk.Toolbar.__init__(self)
        self.set_style(gtk.TOOLBAR_ICONS)
        self.win = win
        self.win.box.pack_start(self, False, False, 0)
        
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

        self.insert(self.back, 0)
        self.insert(msg_counter_item, 1)
        self.insert(self.next, 2)
        self.insert(sep, 3)
        self.insert(check_item,4)
        self.insert(self.close, 5)

    def update_msg_counter(self, id, total):
        self.msg_counter.set_text(id + '/' + total)
        

    def toggled (self, obj):
        if obj.get_active ():
            self.win.html_viewer.set_mode('all')
        else: 
            self.win.html_viewer.set_mode('unread')
        self.win.html_viewer.show_msg('first')

    def on_next_clicked(self, widget):
        print("Siguiente")
        self.win.html_viewer.show_msg('next')
        

    def on_back_clicked(self, widget):
        print("Atras")            
        self.win.html_viewer.show_msg('prev')
   
    
    def on_close_clicked(self, widget):
        print("Goodbye")            
        self.win.destroy() 
        if self.win.message_mgr.get_first_unread() is None:
            gtk.main_quit()

    def update_next_back_buttons(self, msg):

        if self.win.html_viewer.mode == 'all':
            if self.win.message_mgr.get_prev(msg) is None:
                self.back.set_sensitive(False)
            else:
                self.back.set_sensitive(True)
            
            if self.win.message_mgr.get_next(msg) is None:
                self.next.set_sensitive(False)
            else:
                self.next.set_sensitive(True)
        else:
            if self.win.message_mgr.get_prev_unread(msg) is None:
                self.back.set_sensitive(False)
            else:
                self.back.set_sensitive(True)
            
            if self.win.message_mgr.get_next_unread(msg) is None:
                self.next.set_sensitive(False)
            else:
                self.next.set_sensitive(True)
