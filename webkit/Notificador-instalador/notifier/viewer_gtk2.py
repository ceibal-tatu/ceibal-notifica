#!/usr/bin/python
# -*- coding:utf-8 -*-
import webkit
import gtk
import os
import subprocess
import urlparse

from ceibal.notifier import env
from ceibal.notifier.viewer import *
from ceibal.notifier.message import *
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import *
from ceibal.notifier import __version__

class WinGtk:

    def quit(self):
        gtk.mainquit()

    def get_screen_with(self):
        return gtk.gdk.screen_width()

    def get_screen_height(self):
        print 'height: '+ str(gtk.gdk.screen_height())
        return gtk.gdk.screen_height()

    def get_VBox(self):
        return gtk.VBox()


class VentanaBoton(VentanaBotonCommon, dbus.service.Object):

    def __init__(self, bus, path, mode='boton'):
        self.visor = None
        self.mode = mode
        VentanaBotonCommon.__init__(self)
        dbus.service.Object.__init__(self, bus, path)
        self.win = gtk.Window()
        # Evita que aparezca en la lista de ventanas
        self.win.set_skip_taskbar_hint(True)
        self.win.set_decorated(False)
        self.win.set_accept_focus(False)
        self.create_button()
        (pos_h, pos_v) = get_window_pos(gtk.gdk.screen_width() - self.win.get_size()[0])
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
            self.visor.html_viewer.refresh_tool_bar()

    def create_button(self):
        self.button = gtk.Button()
        self.button.connect("clicked", self.on_button_clicked)
        self.button.connect("enter", self.on_button_pointer_enter)
        self.button.connect("leave", self.on_button_pointer_leave)

        self.image_btn = gtk.Image()
        icon_img = self.get_image_btn("out")
        self.image_btn.set_from_file(icon_img)
        self.image_btn.show()
        self.button.add(self.image_btn)
        self.win.add(self.button)

    def on_button_clicked(self, widget):
        self.visor = Visor(self)

    def bye(self):
        gtk.mainquit()

    def main(self):
        gtk.main()


class Visor(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        (self.width, self.height) = get_window_size()
        self.web_viewer_height = self.height - 20
        self.connect("key-release-event", self.on_key_release)
        self.ventana_btn = parent
        # Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)

        # Decorators
        self.set_decorated(False)

        self.resize(self.width, self.height)
        #self.set_accept_focus(False)
        self.box = gtk.VBox()
        self.add(self.box)
        self.message_mgr = Messages()
        self.tool_bar = ToolBar(self)
        self.html_viewer = WebViewer(self)
        (pos_h, pos_v) = get_window_pos(gtk.gdk.screen_width() - self.get_size()[0])
        self.move(pos_h, pos_v)
        self.html_viewer.show_msg('first')
        self.show_all()

    def custom_close(self):
        self.ventana_btn.custom_close()
        self.destroy()

    def on_key_release(self, widget, ev, data=None):
        print "Key pressed"
        if ev.keyval == 65307:  # If Escape pressed, reset text
            print "Escape"
            self.custom_close()


class WebViewer(WebViewerCommon):
    def __init__(self, win):
        WebViewerCommon.__init__(self)
        self.win = win
        self.view = webkit.WebView()
        self.view.connect("navigation-policy-decision-requested", self.navigate)
        # self.view.set_full_content_zoom(True)

        self.sw = gtk.ScrolledWindow()
        self.sw.set_size_request(0,self.win.web_viewer_height)
        self.sw.add(self.view)
        self.btn_leido = self.create_btn_leido()
        self.check_btn = gtk.CheckButton()
        self.check_btn.set_label('Mostrar todos')
        self.check_btn.connect('toggled', self.toggled)

        # Alineo el check a la derecha
        halign = gtk.Alignment(1, 0, 0, 0)
        halign.add(self.check_btn)

        # Tabla con 3 columnas.
        # Columna izq: nada
        # Columna central: Boton maracar como leida
        # Columna derecha: check de mostar todas
        table = gtk.Table(1, 3, True)

        table.attach(self.btn_leido, 1, 2, 0, 1)
        table.attach(halign, 2, 3, 0, 1)

        self.win.box.pack_start(self.sw, True, True, 0)
        self.win.box.pack_start(table, True, True, 0)

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

        self.get_notif = gtk.ToolButton(gtk.STOCK_REFRESH)
        self.get_notif.connect("clicked", self.on_get_notif_clicked)

        self.about = gtk.ToolButton(gtk.STOCK_ABOUT)
        self.about.connect("clicked", self.on_about_clicked)

        sep = gtk.SeparatorToolItem()

        sep.props.draw = False
        sep.set_expand(True)

        msg_counter_item = gtk.ToolItem()
        self.msg_counter = gtk.Label()
        msg_counter_item.add(self.msg_counter)

        self.tbar.insert(self.back, 0)
        self.tbar.insert(msg_counter_item, 1)
        self.tbar.insert(self.next, 2)
        self.tbar.insert(sep, 3)
        self.tbar.insert(self.get_notif, 4)
        self.tbar.insert(self.about, 5)
        self.tbar.insert(self.close, 6)

    def on_about_clicked(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name("Notificador de Ceibal")
        about.set_version(__version__)
        about.set_copyright("(c) Ceibal")
        about.set_comments("Recibe y muestra notificaciones enviadas por el Plan Ceibal")
        about.set_website("http://www.ceibal.edu.uy")
        about.set_logo(gtk.gdk.pixbuf_new_from_file(env.get_images_root() + "/planceibal.png"))
        about.run()
        about.destroy()

