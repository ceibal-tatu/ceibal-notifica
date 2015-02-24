#!/usr/bin/python
import webkit
import gtk
import gobject
import os
import json

from ceibal.notifier.message  import * 
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import * 
from os.path import expanduser



class VentanaBoton(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.image_btn = os.path.join (expanduser("~"),NOTIF_IMG_BTN)

        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)

        self.message_mgr = Messages()
        if self.message_mgr.get_first_unread() is None:
            print "No hay mensajes o estan todos leidos ..."
            return
    
        self.set_decorated(False)
        self.set_accept_focus(False)
        self.connect("delete-event", gtk.main_quit)
        self.create_button()
        self.show_all()
        self.move(gtk.gdk.screen_width()- self.get_size()[0] ,0)
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
        self.width  = 400
        self.height = 300
        #GObject.threads_init()
        gtk.Window.__init__(self)

        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        
        # Decorators
        self.set_decorated(False)

        self.resize(self.width,self.height)
        self.set_accept_focus(False)
        self.box = gtk.VBox()
        self.add(self.box) 
        self.tool_bar    = ToolBar(self)
        self.html_viewer = WebViewer(self)
        self.move(gtk.gdk.screen_width()- self.get_size()[0] ,0)
        self.show_all()



class WebViewer:

    def __init__ (self,win):
        self.win = win
        self.view = webkit.WebView()
         
        self.sw = gtk.ScrolledWindow()
        self.sw.set_size_request(0,(self.win.height - 20))
        self.sw.add(self.view)
        self.btn_leido = self.create_btn_leido() 
        
        self.win.box.pack_start(self.sw, True, True, 0)
        self.win.box.pack_start(self.btn_leido, True, True, 0)
        
        self.message_mgr = Messages()
        self.current_msg = None
        self.show_msg('first')
    
    def create_btn_leido(self):
        button = gtk.ToggleButton(label='Marcar como Leido')
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
        return current_msg
    
    def is_there_next_msg (self, pos):
        
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
        return current_msg
    
    def set_msg_read(self):
        self.message_mgr.set_read(self.current_msg)

class ToolBar(gtk.Toolbar):
    
    def __init__(self, win):
        self.message_mgr = Messages()
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
        self.check_btn.set_label ('Leido')
        self.check_btn.connect ('toggled' , self.toggled)
        check_item.add (self.check_btn)

        sep = gtk.SeparatorToolItem()

        sep.props.draw = False
        sep.set_expand(True)

        self.insert(self.back, 0)
        self.insert(self.next, 1)
        self.insert(sep, 2)
        self.insert(check_item,3)
        self.insert(self.close, 4)

    def is_there_next_msg


    def clean_read_check(self):
        self.check_btn.set_active(False)

    def toggled (self, obj):
         if obj.get_active ():
            self.win.html_viewer.set_msg_read()
 
    def on_next_clicked(self, widget):
        print("Siguiente")
        msg = self.win.html_viewer.show_msg('next')
        if msg is not None:
            if self.message_mgr.get_next_unread(msg) is None:
                widget.set_sensitive(False)
        else:
            widget.set_sensitive(False)

    def on_back_clicked(self, widget):
        print("Atras")            
        msg = self.win.html_viewer.show_msg('prev')
        if msg is not None:
            if self.message_mgr.get_prev_unread(msg) is None:
                widget.set_sensitive(False)
        else:
            widget.set_sensitive(False)
           
    
    def on_close_clicked(self, widget):
        print("Goodbye")            
        self.win.destroy() 
        message_mgr = Messages()
        if message_mgr.get_first_unread() is None:
            gtk.main_quit()


