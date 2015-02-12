#! /usr/bin/python
# -*- coding:utf-8 -*-
#__init__.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
#-----------------------------------------------------------------------------
# Ubicacion de la clase principal del Notificador.
# Toma las Notificaciones de la DB y las muestra tanto para Sugar como Gnome.
#-----------------------------------------------------------------------------

import os
import datetime
import time

from ceibal.notifier import env
from ceibal.notifier.data_base import Db
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import DB_FILE,IMAGEN_NOTOFY,BTN_GENERAL,BTN_LINK,TIME_ENTRE_MSJ, TIME_ESPERA, FUNCIONES_PRIORIDAD

class Notifier:
    def __init__(self, db_filename=os.path.join(env.get_data_root(),DB_FILE)):
        self.db_filename = db_filename
        self.images = os.path.join(env.get_images_root(), IMAGEN_NOTOFY)

    def _get_messages(self, args={}):
        '''
        @param args: Lista de condiciones para la consulta.
        
        @summary: Abrimos conexion a la base de datos, obtenemos los mensajes y luego filtramos por
        los mensajes que no esten vencidos.
        
        @return: Lista de Notificaciones vigentes.
        '''
        db = Db(self.db_filename)
        messages = filter(self._date_valid,db.get_messages(args))
        return messages

    def _date_valid(self,message):
        '''
        @param message: Mensaje a validar.
        
        @summary: Valida si el mensaje ya expiro.
        
        @return: Verdadero si esta vigente el mensaje.
        '''
        expires = message["vencimiento"]
        today = datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
        return today <= expires
    
    def show_messages_from_shell(self):
        '''
        @summary: Funcion que muestra los mensajes en el ambiente de Sugar.
        '''
        from jarabe.frame import get_view
        frame = get_view()
        for message in self._get_messages():
            frame.add_message(body=message['texto']+"\n"+"LINK:"+"\n"+message['accion'], summary=message['titulo'])

    def show_messages_from_python(self):
        '''
        @summary: Funcion que muestra los mensajes en el ambiente de Gnome.
        '''
        mensajes=self._get_messages()
        for dic in mensajes:
            # Se redimensionan los textos porque el servicio que despliega las notificaciones
            #tiene un error con la resolucion y muestra los mensajes cortados.
            titulo = redimensionar_texto(35,dic['titulo'])
            texto = redimensionar_texto(45,dic['texto'])
            
            icono = self.images
            prioridad = dic['funcion']
            url = dic['accion']
            
            if prioridad == FUNCIONES_PRIORIDAD[0]:
                self.notify_send(titulo, texto, icono)
            else:
                if prioridad == FUNCIONES_PRIORIDAD[1]:
                    self.notify_send(titulo, texto, icono, url, BTN_GENERAL)
                else:
                    self.notify_send(titulo, texto, icono, url, BTN_LINK)
            
            time.sleep(TIME_ENTRE_MSJ)
    
    def notify_send(self, titulo, texto, icono=None, url=None, texto_link=None):
        '''
        @param titulo: El titulo de la Notificacion.
        @param texto: El texto de la Notificacion.
        @param icono: EL icono de la Notificacion. Puede no tener.
        @param url: La url vinculada a la Notificacion. Puede no tener.
        @param texto_link: Texto que tendrá el vinculo.
        
        @summary: Funcion especifica a mandar al servicio la notificacion.
        '''
        
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
    n = Notifier()
    n.show_messages_from_python()
