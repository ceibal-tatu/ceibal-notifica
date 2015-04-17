#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import subprocess
import urlparse

from ceibal.notifier  import env
from ceibal.notifier.notificador_obtener import *
from ceibal.notifier.message import *
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import * 



class VentanaBotonCommon:
    
    icons_over={0: 'not_0hover.png', 
                1: 'not_1hover.png',
                2: 'not_2hover.png',
                3: 'not_3hover.png',
                4: 'not_4hover.png',
                5: 'not_5hover.png', 
                6: 'not_6hover.png', 
                7: 'not_7hover.png', 
                8: 'not_8hover.png', 
                9: 'not_9hover.png', 
                10: 'not_10hover.png', 
                11: 'not_10mashover.png'}
    
    icons_out ={0: 'not_0.png', 
                1: 'not_1.png',
                2: 'not_2.png',
                3: 'not_3.png',
                4: 'not_4.png',
                5: 'not_5.png', 
                6: 'not_6.png', 
                7: 'not_7.png', 
                8: 'not_8.png', 
                9: 'not_9.png', 
                10: 'not_10.png', 
                11: 'not_10mas.png'}

    def __init__(self):
        self.message_mgr = Messages()
    
    def get_image_btn(self, mouse_pinter):

        if mouse_pinter == "over":
            icons = VentanaBotonCommon.icons_over
        else:
            icons = VentanaBotonCommon.icons_out

        total = self.message_mgr.get_total('unread')
        if total < len(icons)-1:
            idx = total
        else:
            idx = len(icons)-1
        print "file imagen del boton: " +  icons[idx]

        return os.path.join(env.get_images_root(), icons[idx])
    
    def on_button_pointer_enter(self, widget):
        print "mouse pointer enter detected ..."
        icon_img = self.get_image_btn("over")        
        self.refresh_button (icon_img)

    def on_button_pointer_leave(self, widget):
        print "mouse pointer exit detected ..."
        icon_img = self.get_image_btn("out")        
        self.refresh_button (icon_img)
    
    def refresh_button(self, icon_img):
        self.image_btn.set_from_file(icon_img)
        self.image_btn.show()


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
        icon_img = self.win.ventana_btn.get_image_btn("out")        
        self.win.ventana_btn.refresh_button(icon_img)
        self.win.destroy() 

    def on_get_notif_clicked(self, widget):
        print("Getting new notifications ... ")
        NotificadorObtener(onDemand=True)
