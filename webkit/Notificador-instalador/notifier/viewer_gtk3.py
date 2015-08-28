#!/usr/bin/python
# -*- coding:utf-8 -*-
from gi.repository import Gtk, Gdk, GdkPixbuf, WebKit
import os
import urlparse

from ceibal.notifier import env
from ceibal.notifier.viewer import *
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import * 
from ceibal.notifier.message  import * 
from ceibal.notifier import __version__


class WinGtk:

    def quit(self):
        Gtk.main_quit()

    def get_screen_with(self):
        return Gdk.Screen.get_default().get_width()

    def get_screen_height(self):
        return Gdk.Screen.get_default().get_height()

    def get_VBox(self):
        return Gtk.VBox()


class VentanaBoton(VentanaBotonCommon, dbus.service.Object):

    def __init__(self, bus, path, mode='boton'):
        self.visor = None
        self.mode = mode
        VentanaBotonCommon.__init__(self)
        dbus.service.Object.__init__(self, bus, path)
        self.win = Gtk.Window(title="Notificador de novedades Ceibal")
        #self.win = VentanaBotonWindow(self)
        #Evita que aparezca en la lista de ventanas
        self.win.set_skip_taskbar_hint(True)
        self.win.set_decorated(False)
        self.win.set_accept_focus(False)
        self.win.add_events(Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.create_button()
        (pos_h, pos_v) = get_window_pos (Gdk.Screen.get_default().get_width() - self.win.get_size()[0])
        self.win.move(pos_h, pos_v)

        if (self.mode == 'visor'):
            print "En modo visor"
            self.visor = Visor(self)
        else:
            if self.message_mgr.get_total('unread') > 0:
                self.win.show_all()
            else:
                print "En modo boton: no hay notificaciones sin leer"
        self.main()

    @dbus.service.method('edu.ceibal.UpdateInterface',in_signature='', out_signature='')
    def update(self):
        print "Update signal received"
        icon_img = self.get_image_btn("out")
        self.refresh_button (icon_img)
        if self.visor is not None:
            print "Refreshing toolbar"
            self.visor.html_viewer.refresh_tool_bar()
            self.visor.tool_bar.get_notif.set_sensitive(True)

    def create_button(self):
        self.button = Gtk.Button()
        self.button.connect("button-release-event", self.on_button_clicked)
        self.button.connect("button-press-event", self.on_button_press)
        self.button.connect("enter", self.on_button_pointer_enter)
        self.button.connect("leave", self.on_button_pointer_leave)
        
        self.image_btn = Gtk.Image()
        icon_img = self.get_image_btn("out")
        self.image_btn.set_from_file(icon_img)
        self.image_btn.show()
        self.button.add(self.image_btn)
        self.win.add(self.button)
    
    def on_button_clicked(self, widget, event):
        if event.button == 1:
            self.visor = Visor(self)
        return True

    def on_button_press(self, widget, event):
        if event.button == 2 or event.button == 3:
            self.win.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
        return True
    
    def bye(self):
        Gtk.main_quit()

    def main(self):
        Gtk.main()


class Visor(Gtk.Window):
 
    def __init__(self, parent):
        Gtk.Window.__init__(self, title="Visor de novedades Ceibal")
        (self.width, self.height) = get_window_size()
        self.web_viewer_height = self.height - 20
        self.connect("key-release-event", self.on_key_release) 
        
        self.ventana_btn = parent
        #Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        
        # Decorators
        self.set_decorated(False)

        self.resize(self.width,self.height)
        (pos_h, pos_v) = get_window_pos (Gdk.Screen.get_default().get_width() - self.width)
        self.move(pos_h, pos_v)

        #self.set_accept_focus(False)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.message_mgr = Messages()
        self.add(self.box) 
        self.tool_bar    = ToolBar(self)
        self.html_viewer = WebViewer(self)
        self.html_viewer.show_msg('first')
        self.show_all()
    
    def custom_close(self):
        self.ventana_btn.custom_close()
        self.destroy()


    def on_key_release(self, widget, ev, data=None):
        print "Key pressed"
        if ev.keyval == 65307: #If Escape pressed, reset text
            print "Escape"
            self.custom_close()


class WebViewer (WebViewerCommon):

    def __init__(self, win):
        WebViewerCommon.__init__(self)
        self.win = win
        self.view = WebKit.WebView()
        self.view.connect("navigation-policy-decision-requested",self.navigate)
        self.sw = Gtk.ScrolledWindow()
        self.sw.set_size_request(0,self.win.web_viewer_height)
        self.sw.add(self.view)
        self.btn_leido = self.create_btn_leido()

        self.check_btn = Gtk.CheckButton()
        self.check_btn.set_label ('Mostrar todos')
        self.check_btn.connect('toggled' , self.toggled)
        # Alineo el check a la derecha
        self.check_btn.props.halign = Gtk.Align.END

        # Tabla con 3 columnas.
        # Columna izq: nada
        # Columna central: Boton maracar como leida
        # Columna derecha: check de mostar todas
        table = Gtk.Table(1, 3, True)

        table.attach(self.btn_leido, 1,2,0,1)
        table.attach(self.check_btn, 2,3,0,1)

        self.win.box.pack_start(self.sw, True, True, 0)
        self.win.box.pack_start(table, True, True, 0)

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

        self.get_notif = Gtk.ToolButton(Gtk.STOCK_REFRESH, label="Actualizar")
        self.get_notif.connect("clicked", self.on_get_notif_clicked)

        self.about = Gtk.ToolButton(Gtk.STOCK_ABOUT, label="Acerca")
        self.about.connect("clicked", self.on_about_clicked)

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
        self.tbar.insert(self.get_notif,4)
        self.tbar.insert(self.about ,5)
        self.tbar.insert(self.close, 6)

    def on_about_clicked(self, widget):
        about = Gtk.AboutDialog()
        about.set_program_name("Notificador de Ceibal")
        about.set_version(__version__)
        about.set_copyright("(c) Ceibal")
        about.set_comments("Recibe y muestra notificaciones enviadas por el Plan Ceibal")
        about.set_website("http://www.ceibal.edu.uy")
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file(env.get_images_root()+"/planceibal.png"))
        about.run()
        about.destroy()
