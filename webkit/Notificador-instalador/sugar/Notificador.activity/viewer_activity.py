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



class NotificadorActivity(activity.Activity):
    def __init__(self, handle):
        _logger.debug('Start NotificadorActivity')
        super(NotificadorActivity, self).__init__(handle)

        # Start DBus Service
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()
        name = dbus.service.BusName("edu.ceibal.NotificadorService", session_bus)
        VentanaBoton(session_bus, "/Update", mode='boton')

        self.close()
        self.destroy()
