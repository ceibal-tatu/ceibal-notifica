#! /usr/bin/python
# -*- coding:utf-8 -*-
# web_service_conexion.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
#---------------------------------------------------------------------------------
# Genera la conexion al Web service de Ceibal para solicitar las Notificaciones.
#---------------------------------------------------------------------------------

import urllib2
import json
from ceibal.notifier.store import Store
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import TMP_JSON,JSON_KEYS,DIC_KEYS,IMAGEN_NOTOFY,WEB_SERVICE_URL,ALERTA_SN,ALERTA_ERROR

class W_S_Conexion:
    def __init__(self, url):
        """
        @param url: URL al cual se va a generar conexion.
        @summary: Inicializamos la clase con la URL al Web Service.
        """
        self.url = url
    
    def _concatenar_parametros_url(self):
        '''
        @summary: Conecta los parametros a la URL de la conexion al Web Service.
        '''
        try:
            parametros=obtener_parametros()
            if parametros[1]:
                self.url=self.url+"?cedula="+str(parametros[0])+"&serie="+str(parametros[1])+"&modelo="+str(parametros[2])+"&imagen="+str(parametros[3])
            else:
                notificacion(ALERTA_SN)
        except:
            notificacion(ALERTA_ERROR)
            
    def _concatenar_nuevos_parametros_url(self):
        '''
        @summary: Conecta los parametros a la URL de la conexion al Web Service.
        '''
        from ceibalmipc.laptops.laptopFactory import LaptopFactory

        laptop = LaptopFactory()

        noHayParametro = False

        try:
            if laptop.get_ceibal_user is not None and laptop.get_id is not None and laptop.get_model is not None \
                and laptop.get_build is not None and laptop.get_firmware is not None and laptop.get_plazo_bloqueo is not None \
                and laptop.get_boot_count_bloqueo is not None and laptop.get_last_update is not None \
                and laptop.get_free_space_porc is not None:
                self.url += "?cedula=" + laptop.get_ceibal_user
                self.url += "&serie=" + laptop.get_id
                self.url += "&modelo=" + laptop.get_model
                self.url += "&imagen=" + laptop.get_build
                #self.url += "&fechaReporte=" + 
                self.url += "&firmware=" + laptop.get_firmware
                self.url += "&plazoBloqueo=" + laptop.get_plazo_bloqueo
                self.url += "&bootCountBloqueo=" + laptop.get_boot_count_bloqueo
                self.url += "&fechaUltActualizacion=" + laptop.get_last_update
                self.url += "&espacioLibrePorcentaje=" + laptop.get_free_space_porc
                self.url += "&datosExtra=" + "{'datos' : 'clave'}"
            else:
                print ('Faltan parametros para construir la URL')
        except:
            notificacion(ALERTA_ERROR)
        
    
    def _conectar(self, url):
        """
        @param url: Url del Web Service.
        @summary: Conecta al Web Service y devuelve la consulta.
        @requires: Devuelve el resultado de la conexion al Web Service.
        """
        try:
            self.conexion = urllib2.urlopen(url)
        except Exception, e:
            print str(e)

        return self.conexion.read()
    
    def _guardar_en_archivo(self,texto):
        """
        @param texto: Texto a guardar en archivo.
        @summary: Guarda en un archivo de la carpeta temporal el atributo texto (resultado de la consulta al Web Serice)
        """
        try:
            self.archivo = open(TMP_JSON,"wb")
            self.archivo.write(texto)
            self.archivo.close()
        except Exception, e:
            print str(e)
    
    def _parse_json(self):
        """
        @summary: Lee en formato JSON el archivo guardado en la carpeta temporal. Recorre cada atributo 
         de los objetos del JSON para guardarlos en una Lista de Diccionarios.
        @return: Devuelve una Lista de Diccionarios que representan cada objeto del JSON.
        @deprecated: Esta funcion fue remplazada por el proceso de Store de esa clase.
        """
        contenido = json.loads(open(TMP_JSON).read())
        self.lista_notify=[]

        for x in xrange(int(contenido['cantidad'])):
            self.lista_notify.append({})
            for y in xrange(len(JSON_KEYS)):
                self.lista_notify[x][DIC_KEYS[y]]=contenido['data'][x][JSON_KEYS[y]]
                print ""
                print self.lista_notify[x][DIC_KEYS[y]]
            # Insertamos la imagen por defecto de la notificacion.
            self.lista_notify[x][DIC_KEYS[y+1]]=IMAGEN_NOTOFY
        return self.lista_notify
    
    def Obtener_notificaciones(self, on_demand):
        """
        @param on_demand: Parametro que determina si la conexion al Web-Servis es demandada por el usuario.
        @summary: Funcion publica para consumir el Web Service.
        """
        # Concatenamos los parametros a la URL.
        self._concatenar_parametros_url()
        
        # Conecta a la URL del web Service y guarda el contenido en un archivo.
        json_response = self._conectar(self.url)

        try:
            json.loads(json_response)
        except ValueError, e:
            print("Respuesta invalida")
            return None

        self._guardar_en_archivo(json_response)
        
        # Conectamos a la Base de Datos.
        base_de_datos = Store()
        
        # Cargamos las Notificaciones a la Base de Datos.
        base_de_datos.Cargar_notificaciones()

        return json_response

if __name__ == "__main__":
    # Creamos la conexion al Web-Service.
    web=W_S_Conexion(WEB_SERVICE_URL)
    
    # Obtenemos las notificaciones correspondientes.
    web.Obtener_notificaciones(False)