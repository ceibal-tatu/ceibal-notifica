#! /usr/bin/python
# -*- coding:utf-8 -*-
# store.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
#---------------------------------------------------------------------------------------
# Guarda los mensajes obtenidos desde un Web Service.
# Actualmente se guardan en una base de datos sqlite3 y los archivos vienen en json.
#---------------------------------------------------------------------------------------

import json
from ceibal.notifier.data_base import Db
from ceibal.notifier.constantes import TMP_JSON,JSON_KEYS,DIC_KEYS,IMAGEN_NOTOFY

class Store:
    def __init__(self, db_filename=None):
        """
        @summary: Iniciamos el almacenamiento de las Notificaciones.
        """
        # Abrimos la DB.
        self.db = Db(db_filename)
        
        # Eliminamos todas las Notificacions que su fecha de vencimiento sea inferior a la fecha actual.
        self.db.clean_db()

    def _traducir_parametro(self, key, value):

        if key == 'prioridad':
            if value == 'institucional':
                return 1
            else:
                return 2
        else:
            return value

    def Cargar_notificaciones(self):
        """
        @summary: Cargamos desde un archivo JSON las Notificaciones.
        """
        contenido = json.loads(open(TMP_JSON).read())
        msgs=[]
        
        for x in xrange(int(contenido['cantidad'])):
            msgs.append({})
            for y in xrange(len(JSON_KEYS)):
		        msgs[x][DIC_KEYS[y]]= self._traducir_parametro (DIC_KEYS[y], contenido['data'][x][JSON_KEYS[y]])
            # Insertamos la imagen por defecto de la notificacion.
            msgs[x][DIC_KEYS[y+1]]=IMAGEN_NOTOFY

        # Ordeno las respuestas por fecha de vencimiento
        msgs.sort(key=lambda k: k['vencimiento'])

        for msg in msgs:
            self._save_message(msg)


    def _save_message(self, msg):
        """
        @param msg: Diccionario de mensajes.
        @summary: Procesa los mensajes que vienen en el diccionario msg. Desmenusa el diccionario en Keys
         y valores para ser insertados en la DB.
        """
        print "Procesando Notificacion con Id: %s" % msg["id"]
        keys = msg.keys()
        values = []
        for item in keys:
            try:
                values.append(str(msg[item]))
            except:
                values.append(msg[item])
        self.db.add_message(keys, values)

if __name__ == "__main__":
    notification = Store('messages.db')
    
    # Cargamos las Notificacions y las guardamos en la DB.
    notification.Cargar_notificaciones()
