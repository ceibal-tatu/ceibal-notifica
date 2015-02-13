#! /usr/bin/python
# -*- coding:utf-8 -*-
#notificador.py V2.0
# Author: Matias Bass <mbasso@plan.ceibal.edu.uy> 
#-----------------------------------------------------------------------------
# Soporte para distintos tipos de notificadores.
#-----------------------------------------------------------------------------

import sys
import subprocess
import logging

log = logging.getLogger("notificador")

def notificar(title, body, icon, actions=None, kind=None):
    notifier = create_notifier(title, body, icon, actions, kind)
    notifier.show()
    return notifier

def create_notifier(title, body, icon, actions, kind=None): 
    if kind == 'gobjects' or ((kind is None or kind == 'daemon') and supports_gobjects()):
        log.debug("Using gobjects notifier")
        return GObjectsNotifier(title, body, icon, actions)
    elif kind == 'pynotify' or ((kind is None or kind == 'daemon') and supports_pynotify()):
        log.debug("Using pynotify notifier")
        return PyNotifyNotifier(title, body, icon, actions)
    elif kind == 'notify-send':
        log.debug("Using notify-send")
        return NotifySendNotifier(title, body, icon, actions)
    raise Exception("No hay sistema de notificacion disponible")

def supports_pynotify():
    try:
        import pynotify
        return True
    except:
        return False

def supports_gobjects():
    try:
        from gi.repository import Notify
        return True
    except:
        return False

class BaseNotifier(object):
    def __init__(self, title, body, icon, actions):
        self.title = title
        self.body = body
        self.actions = {}

        if actions:
            count = 0
            for action_label in actions.keys():
                count = count + 1
                action_key = "action_%i" % count
                self.actions[action_key] = {
                    'label': action_label,
                    'command': actions[action_label]
                }

        self.icon = icon
        self.__loop = None
     
    def show(self):
        self.__init_gtk()
        try:
            self._do_show()
            self.__run_gtk()
        except:
            log.exception("Show notification failed")
            self.__terminate_gtk()

    def _close(self, e):
        try:
            self._do_close()
        finally:
            self.__terminate_gtk()

    def _run_action(self, notification, action_key, action_data=None):
        try:
            action = self.actions[action_key]
            if action and action['command']:
                subprocess.Popen(action['command'], shell=True)
        except:
            log.exception("Run action failed")
        finally:
            self._close(None)

    def __init_gtk(self):
        self.__loop = self._get_loop()

    def __run_gtk(self):
        self.__loop.run()

    def __terminate_gtk(self):
        if self.__loop:
            self.__loop.quit()

class GObjectsNotifier(BaseNotifier):
    def __init__(self, title, body, icon, actions):
        super(GObjectsNotifier, self).__init__(title, body, icon, actions)
        self._notification = None

    def _get_loop(self):
        from gi.repository import GObject
        return GObject.MainLoop()

    def _do_show(self):
        from gi.repository import Notify
        if not Notify.is_initted():
            Notify.init("ceibal-notifica")
        
        notification = Notify.Notification.new(self.title, self.body, self.icon or "dialog-information")
        notification.connect("closed", self._close)
        for action_key in self.actions.keys():
            action = self.actions[action_key]
            notification.add_action(action_key, action['label'], self._run_action, None)
        notification.show()
        self._notification = notification

    def _do_close(self):
        if self._notification:
            self._notification.close()

class PyNotifyNotifier(BaseNotifier):
    def __init__(self, title, body, icon, actions):
        super(PyNotifyNotifier, self).__init__(title, body, icon, actions)
        self._notification = None

    def _get_loop(self):
        import gobject
        return gobject.MainLoop()

    def _do_show(self):
        import pynotify
        if not pynotify.is_initted():
            pynotify.init("ceibal-notifica")
        
        notification = pynotify.Notification(self.title, self.body, self.icon or "dialog-information")
        notification.connect("closed", self._close)
        for action_key in self.actions.keys():
            action = self.actions[action_key]
            notification.add_action(action_key, action['label'], self._run_action, None)
        notification.show()
        self._notification = notification

    def _do_close(self):
        if self._notification:
            self._notification.close()

class NotifySendNotifier(object):
    def __init__(self, title, text, icon, actions):
        self.title = title
        self.text = text
        self.icon = icon
        self.actions = actions

    def show(self):
        url = None
        texto_link = None
        actions = self.actions
        if actions:
            keys = actions.keys()
            if keys and actions[keys[0]]:
                url = keys[0]
                texto_link = actions[url]

        self.notify_send(self.title, self.text, self.icon, url, texto_link)
        
    def notify_send(self, titulo, texto, icono=None, url=None, texto_link=None):
        '''
        @param titulo: El titulo de la Notificacion.
        @param texto: El texto de la Notificacion.
        @param icono: EL icono de la Notificacion. Puede no tener.
        @param url: La url vinculada a la Notificacion. Puede no tener.
        @param texto_link: Texto que tendrá el vinculo.
        
        @summary: Funcion especifica a mandar al servicio la notificacion.
        '''
        import os
        
        # Comando Bash que comunica la notificacion la servicio "notification-daemon"
        comando="notify-send "
        
        if icono:
            if url:
                comando = comando + str("--icon="+icono) + " \"" + str(titulo) + "\" \"" + str(texto) + "\n" + str(" <a href='"+url+"'>"+texto_link+"</a>\"")
            else:
                comando = comando + str("--icon="+icono) + " \"" + str(titulo) + "\" \"" + str(texto) + "\""
        else:
            if url:
                comando = comando + "\"" + str(titulo) + "\" \"" + str(texto) + "\n" + str(" <a href='"+url+"'>"+texto_link+"</a>\"")
            else:
                comando = comando + "\"" + str(titulo) + "\" \"" + str(texto) + "\""
        os.system(comando)

if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    kind = len(sys.argv) > 1 and sys.argv[1] or None
    notificar('Prueba', "<b>Esto</b> una <i>prueba</i>", 'dialog-warning', { 
        'Firefox': '/usr/bin/firefox',
        'Wall': 'wall foo'
    }, kind)
