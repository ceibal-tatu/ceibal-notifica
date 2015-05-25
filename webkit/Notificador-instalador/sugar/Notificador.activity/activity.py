#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import logging
import imp

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

os.environ['SUGAR_ACTIVITY_ROOT'] = os.getcwd() + "/"

def find_module(mod):
    try:
        imp.find_module(mod)
    except ImportError:
        return False
    else:
        return True

if find_module('gtk') and find_module('webkit'):
    from ceibal.notifier.viewer_gtk2 import *
    from sugar.activity import activity
else:
    from ceibal.notifier.viewer_gtk3 import *
    from sugar3.activity import activity

import gio

winGtk = WinGtk()

class Notificador(activity.Activity, VentanaBotonCommon):

    def __init__(self, handle):
        _logger.debug('Start NotificadorActivity')

        # Evita modificaciones de Sugar en el gtk.Window
        os.environ.pop('SUGAR_ACTIVITY_ROOT')

        activity.Activity.__init__(self,handle)
        self.mode = 'boton'
        self.visor = None
        self.win = self
        VentanaBotonCommon.__init__(self)

        # Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)
        self.set_decorated(False)
        self.set_accept_focus(False)
        self.box = winGtk.get_VBox()
        self.create_button()
        self.set_canvas(self.box)
        self.resize(60, 80)
        self.box.show()
        self.show_all()
        (pos_h, pos_v) = get_window_pos(winGtk.get_screen_with() - self.get_size()[0])
        self.move(pos_h, pos_v)
        DbWatcher(self)

    def create_button(self):
        self.button = winGtk.get_button()
        self.button.connect("clicked", self.on_button_clicked)
        self.button.connect("enter", self.on_button_pointer_enter)
        self.button.connect("leave", self.on_button_pointer_leave)
        self.image_btn = winGtk.get_image()
        icon_img = self.get_image_btn("out")
        self.image_btn.set_from_file(icon_img)
        self.image_btn.show()
        self.button.add(self.image_btn)
        self.box.pack_start(self.button, True, True, 0)

    def on_button_clicked(self, widget):
        self.visor = Visor(self)

    def update(self,monitor, file1, file2, evt_type):
        file_changed = False
        if evt_type in (gio.FILE_MONITOR_EVENT_CHANGED,):
            file_changed = True
        if file_changed:
            icon_img = self.get_image_btn("out")
            self.refresh_button (icon_img)
            if self.visor is not None:
                self.visor.html_viewer.refresh_tool_bar()



class DbWatcher():

    def __init__(self, boton):
        gfile = gio.File(os.path.join(env.get_data_root(), DB_FILE))
        monitor = gfile.monitor(gio.FILE_MONITOR_NONE)
        monitor.connect("changed", boton.update)