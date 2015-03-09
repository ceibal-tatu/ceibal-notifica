import json
import os
import datetime
import time

from ceibal.notifier import env
from ceibal.notifier.data_base import Db
from ceibal.notifier.constantes import * 




class Messages:
    db = None

    def __init__(self):
        if Messages.db is None:
            Messages.db = Db(os.path.join(env.get_data_root(), DB_FILE))

    def _save_notification_status(self, id, status):
        Messages.db.run_query('update notifications set estado="{1}" where id="{0}"'.format(id, status))

    def _check_notification_is_unread (self, message):
        id = str (message['id'])
        
        msg = Messages.db.get_messages({'id':id})    
        if msg[0]['estado'] == 'unread':
            return True
        else:
            return False
    
    def _date_valid(self,message):
        '''
        @param message: Mensaje a validar.
        
        @summary: Valida si el mensaje ya expiro.
        
        @return: Verdadero si esta vigente el mensaje.
        '''
        expires = message["vencimiento"]
        today = datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
        return today <= expires

    def get_total (self, mode):
        if mode == 'unread':
            args = {'estado': '"unread"'}
        else:
            args = {}
        messages = filter(self._date_valid,Messages.db.get_messages(args))
        return len(messages)

    def get_pos(self, mode, msg):
        pos = 1
        if mode == 'unread':
            args = {'estado':'"unread"'}
        else:
            args = {}
        messages = filter(self._date_valid,Messages.db.get_messages(args))
        for m in messages:
            if m['id'] == msg['id']:
                return pos
            pos = pos+1    
        return pos
 
    def _get_first (self, args={}):
        messages = filter(self._date_valid,Messages.db.get_messages(args))
        
        if len(messages) > 0:
            return messages[0]
        else:
            return None 

    def get_first (self):
        args = {}
        return self._get_first(args)
    
    def get_first_unread(self, args={}):
        args = {'estado':'"unread"'}
        return self._get_first(args)
    
    def _get_next(self, message, args):
        if message is None:
            return None
        
        messages = filter(self._date_valid,Messages.db.get_messages(args))
        
        for msg in messages:
            if msg['tstamp'] <= message['tstamp'] and msg['id'] <  message['id']:
                print "true"
                return msg
        
        return None

    def get_next(self, message):
        args = {}
        return self._get_next(message, args)
         
    def get_next_unread(self, message):
        args = {'estado':'"unread"'}
        return self._get_next(message, args)

    
    def _get_prev(self, message, args):
        if message is None:
            return None
        messages = filter(self._date_valid,Messages.db.get_messages(args))
        for msg in reversed(messages):
            if msg['tstamp'] >= message['tstamp'] and msg['id'] > message['id']:
                return msg
        return None 
    
    def get_prev(self, message):
        args = {}
        return self._get_prev(message, args)
    
    def get_prev_unread(self, message):
        args = {'estado':'"unread"'}
        return self._get_prev(message, args)
        
    def is_unread(self, msg):
        return self._check_notification_is_unread(msg) 
   
    def get_all(self):
        return Messages.db.get_messages({})
 
    def get_test_message(self):
        wdir = os.path.dirname(os.path.abspath(__file__))
        return ('file://' + os.path.join(wdir, 'message.html'))
    
    def set_read(self, message):
        self._save_notification_status(message['id'], 'read')
    
    def set_unread(self, message):
        self._save_notification_status(message['id'], 'unread')

