#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import subprocess
import urlparse

from ceibal.notifier  import env
from ceibal.notifier.message  import * 
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import * 



class VentanaBotonCommon:
    
    icon_btn_file_name = {0: 'boton_no_more_notifications.jpeg', 
                          1: 'boton_1.jpeg',
                          2: 'boton_2.jpeg',
                          3: 'boton_3.jpeg',
                          4: 'boton_4.jpeg',
                          5: 'boton_5.jpeg', 
                          6: 'boton_6.jpeg', 
                          7: 'boton_7.jpeg', 
                          8: 'boton_8.jpeg', 
                          9: 'boton_9.jpeg', 
                          10: 'boton_further_more.jpeg'}

    def __init__(self):
        self.message_mgr = Messages()
    
    def get_image_btn(self):

        total = self.message_mgr.get_total('unread')
        if total < len(VentanaBotonCommon.icon_btn_file_name)-1:
            idx = total
        else:
            idx = len(VentanaBotonCommon.icon_btn_file_name)-1
        print "file imagen del boton: " +  VentanaBotonCommon.icon_btn_file_name[idx]

        return os.path.join (env.get_images_root(), VentanaBotonCommon.icon_btn_file_name[idx])


class WebViewerCommon:

    def __init__ (self):
        self.mode = 'unread'
        self.current_msg = None
        self.direction = 'forward'
        self.updating_read_button = False
 
    def btn_leido_cb(self, widget, data=None):
        if widget.get_active():
            self.win.message_mgr.set_read(self.current_msg)
            widget.set_label('Marcar como no leída')
        else:
            self.win.message_mgr.set_unread(self.current_msg)
            widget.set_label ('Marcar como leída')
        
        if self.updating_read_button == False:      
            if self.direction == 'backward':
                self.show_msg('prev')
            else: 
                self.show_msg('next')
            
        

    def update_read_button(self, msg):
        self.updating_read_button = True
        if msg is None:
            self.btn_leido.set_sensitive(False)
        else:
            self.btn_leido.set_sensitive(True)
            if self.win.message_mgr.is_unread(msg):
                self.btn_leido.set_active(False)        
            else:     
                self.btn_leido.set_active(True)        
        self.updating_read_button = False
    
    def show_msg (self, pos):
        if self.current_msg is None:
            self.current_msg = self.win.message_mgr.get_first(self.mode)

        if pos == 'next':
            current_msg = self.win.message_mgr.get_next(self.current_msg, self.mode) 
        elif pos == 'prev':
            current_msg = self.win.message_mgr.get_prev(self.current_msg, self.mode) 
        elif pos == 'first':
            current_msg = self.win.message_mgr.get_first(self.mode) 
        else:
            current_msg = None

        if current_msg is not None:
            self.current_msg = current_msg
            self.view.load_string(current_msg['html'], 'text/html', 'UTF-8','/')
            self.win.tool_bar.update_msg_counter(str(self.win.message_mgr.get_pos(self.mode, current_msg)) , str(self.win.message_mgr.get_total(self.mode)))
        else:
            self.win.tool_bar.update_msg_counter('0', '0')
            self.load_no_more_notification()
    
             
        self.update_read_button(current_msg)
        self.win.tool_bar.update_next_back_buttons(current_msg)
            

    def load_no_more_notification(self):
        self.view.open(os.path.join(env.get_data_root(),'no_more_notifications.html'))
    
    def set_mode(self, mode):
        self.mode = mode
    
    def set_direction(self, direction):
        self.direction = direction

    def set_move_by_row(self, val):
        self.move_by_row = val

    def navigate(self, view, frame, request, action, decision):
        uri = request.get_uri()
        parts = urlparse.urlsplit(uri)
        if parts.scheme and parts.netloc: 
            open_external_browser(uri)
            return True

        return False


class ToolBarCommon:
    
    def update_msg_counter(self, id, total):
        self.msg_counter.set_text(id + '/' + total)

    def toggled (self, obj):
        if obj.get_active ():
            self.win.html_viewer.set_mode('all')
        else: 
            self.win.html_viewer.set_mode('unread')
        self.win.html_viewer.show_msg('first')

    def on_next_clicked(self, widget):
        self.win.html_viewer.set_direction('forward')
        self.win.html_viewer.show_msg('next')
        

    def on_back_clicked(self, widget):
        self.win.html_viewer.set_direction('backward')
        self.win.html_viewer.show_msg('prev')
   
    def update_next_back_buttons(self, msg):
        if self.win.message_mgr.get_prev(msg, self.win.html_viewer.mode) is None:
            self.back.set_sensitive(False)
            self.win.html_viewer.set_direction('forward')
        else:
            self.back.set_sensitive(True)
        
        if self.win.message_mgr.get_next(msg, self.win.html_viewer.mode) is None:
            self.next.set_sensitive(False)
            self.win.html_viewer.set_direction('backward')
        else:
            self.next.set_sensitive(True)

    def on_close_clicked(self, widget):
        print("Goodbye")            
        self.win.ventana_btn.refresh_button()
        self.win.destroy() 
