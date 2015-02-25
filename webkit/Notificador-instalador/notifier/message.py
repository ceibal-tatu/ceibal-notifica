import json
import os
import datetime
import time

from ceibal.notifier import env
from ceibal.notifier.data_base import Db
from ceibal.notifier.constantes import * 
from os.path import expanduser




class Messages:
    db = None

    def __init__(self):
        if Messages.db is None:
            Messages.db = Db(os.path.join(env.get_data_root(),DB_FILE))
        
        self.file_name = os.path.join(expanduser("~"),READ_FILE)    


    def _save_notification_read(self, id):
        try:
            # Cargo el diccionario desde el archivo json
            fp = open(self.file_name, "r")
            notif_read_record = json.load(fp)
            fp.close()
            
            # Borro el archivo json
            open(self.file_name,'w').close()
            fp = open(self.file_name,'r+')
        except:
            # El archivo json no existe, lo creo.
            fp = open(self.file_name, "w+")
            notif_read_record = {}
        
        notif_read_record[id] = 'read'
        json.dump(notif_read_record, fp)
        fp.flush()
        fp.close()
        

    def _check_notification_is_unread (self, message):
        id = str (message['id'])
        
        try:
            fp = open(self.file_name, "r") 
            notif_read_record = json.load(fp)
        except:
            print "No existe el archivo de registro ...."
            return True
          
        if fp is not None:
          fp.close()

        if id in notif_read_record:
            return notif_read_record[id] == 'unread'
        else:
            print "No encuentro id en el registro ..." + id
            return True

    def _date_valid(self,message):
        '''
        @param message: Mensaje a validar.
        
        @summary: Valida si el mensaje ya expiro.
        
        @return: Verdadero si esta vigente el mensaje.
        '''
        expires = message["vencimiento"]
        today = datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
        return today <= expires

    def get_first (self, args={}):
        messages = filter(self._date_valid,Messages.db.get_messages(args))
        
        if len(messages_unread) > 0:
            return messages[0]
        else:
            return None 

    def get_first_unread(self, args={}):
        messages = filter(self._date_valid,Messages.db.get_messages(args))
        messages_unread = filter(self._check_notification_is_unread, messages)
        if len(messages_unread) > 0:
            return messages_unread[0]
        else:
            return None 
    
    def get_next(self, message):
        if message is None:
            return None
        messages = filter(self._date_valid,Messages.db.get_messages({}))
        for msg in messages:
            if msg['id'] > message['id']:
                return msg
        else:
            return None
 
    def get_next_unread(self, message):
        if message is None:
            return None

        messages = filter(self._date_valid,Messages.db.get_messages({}))
        messages_unread = filter(self._check_notification_is_unread, messages)
        
        for msg in messages_unread:
            if msg['id'] > message['id']:
                return msg
        else:
            return None 
    
    def get_prev(self, message):
        if message is None:
            return None
        
        messages = filter(self._date_valid,Messages.db.get_messages({}))
        msg_prev = None 
        for msg in messages:
            if msg['id'] < message['id']:
                msg_prev = msg
            else:
                return msg_prev
        return msg_prev 
    
    def get_prev_unread(self, message):
        if message is None:
            return None
        
        messages = filter(self._date_valid,Messages.db.get_messages({}))
        messages_unread = filter(self._check_notification_is_unread, messages)

        msg_prev = None 
        for msg in messages_unread:
            if msg['id'] < message['id']:
                msg_prev = msg
            else:
                return msg_prev
 
        return msg_prev 
       
   
    def get_all(self):
        return Messages.db.get_messages({})
 
    def get_test_message(self):
        wdir = os.path.dirname(os.path.abspath(__file__))
        return ('file://' + os.path.join(wdir, 'message.html'))
    
    def set_read(self, message):
        self._save_notification_read(message['id'])

