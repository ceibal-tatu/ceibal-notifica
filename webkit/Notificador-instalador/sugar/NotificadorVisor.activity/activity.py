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

winGtk = WinGtk()

class NotificadorVisor(activity.Activity):

    def __init__(self, handle):
        _logger.debug('Start NotificadorActivity')
        activity.Activity.__init__(self,handle)

        self.width  = winGtk.get_screen_with()
        self.height = winGtk.get_screen_height()
        self.web_viewer_height = (self.height - 120)
        self.connect("key-release-event", self.on_key_release)

        self.set_accept_focus(False)
        self.box = winGtk.get_VBox()
        self.message_mgr = Messages()
        self.tool_bar = ToolBar(self)
        self.html_viewer = WebViewer(self)

        self.html_viewer.show_msg('first')
        self.set_canvas(self.box)
        self.box.show_all()
        self.show_all()

    def custom_close(self):
        self.destroy()
        winGtk.quit()

    def on_key_release(self, widget, ev, data=None):
        print "Key pressed"
        if ev.keyval == 65307:  # If Escape pressed, reset text
            print "Escape"
            self.custom_close()

