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


class NotificadorVisor(activity.Activity):

    def __init__(self, handle):
        _logger.debug('Start NotificadorActivity')
        activity.Activity.__init__(self,handle)

        (self.width, self.height) = get_window_size()
        self.connect("key-release-event", self.on_key_release)
        # Evita que aparezca en la lista de ventanas
        self.set_skip_taskbar_hint(True)

        # Decorators
        self.set_decorated(False)

        self.resize(self.width, self.height)
        self.set_accept_focus(False)
        self.box = gtk.VBox()
        self.message_mgr = Messages()
        self.tool_bar = ToolBar(self)
        self.html_viewer = WebViewer(self)
        (pos_h, pos_v) = get_window_pos(gtk.gdk.screen_width() - self.get_size()[0])
        self.move(pos_h, pos_v)
        self.html_viewer.show_msg('first')
        self.set_canvas(self.box)
        self.box.show_all()
        self.show_all()

    def custom_close(self):
        self.destroy()
        gtk.mainquit()

    def on_key_release(self, widget, ev, data=None):
        print "Key pressed"
        if ev.keyval == 65307:  # If Escape pressed, reset text
            print "Escape"
            self.custom_close()

