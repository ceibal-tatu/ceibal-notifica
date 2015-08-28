#! /usr/bin/python
# -*- coding:utf-8 -*-
# web_service_conexion.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
# Last Modified by: Francisco Cobas <fcobas@plan.ceibal.edu.uy>
# Last Modified date: 2015/05
#---------------------------------------------------------------------------------
# Genera la conexion al Web service de Ceibal para solicitar las Notificaciones.
#---------------------------------------------------------------------------------

import urllib2
import urllib
import json
from ceibal.notifier.store import Store
from ceibal.notifier.utilidades import *
from ceibal.notifier.constantes import TMP_JSON,JSON_KEYS,DIC_KEYS,IMAGEN_NOTOFY,WEB_SERVICE_URL,ALERTA_SN,ALERTA_ERROR,VERSION


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
        @deprecada: Se usa la nueva funcion _concatenar_nuevos_parametros_url
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
        program_version = VERSION

        from ceibalmipc.laptops.laptopFactory import LaptopFactory

        l = LaptopFactory().get_laptop()
        
        datosLaptop = { 
            "ceibal-user": str(l.get_ceibal_user()),
            "id": str(l.get_id()),
            "model": str(l.get_model()), 
            "build": str(l.get_build()),
            "firmware": str(l.get_firmware()),
            "plazo-bloqueo": str(l.get_plazo_bloqueo()),
            "boot-count-bloqueo": str(l.get_boot_count_bloqueo()),
            "last-update": str(l.get_last_update()),
            "free-space-porc": str(l.get_free_space_porc()),
            "version": program_version,
            "installed-update": str(l.get_date_installed_update()),
            "last-update-especial": str(l.get_last_update_especial())
        }

        registroDatosFaltantes = "Los datos faltantes son los siguientes:\n"

        for dato, valor in datosLaptop.iteritems():
            if valor is None:
                datosLaptop[dato] = ""
                registroDatosFaltantes += " - " + str(dato) + '\n'
            elif valor is "":
                registroDatosFaltantes += " - " + str(dato) + "\n"
            else:
                datosLaptop[dato] = str.replace(datosLaptop[dato], ' ', '%20')

        try:
            self.url += "?cedula=" + datosLaptop["ceibal-user"]
            self.url += "&serie=" + datosLaptop["id"]
            self.url += "&modelo=" + datosLaptop["model"]
            self.url += "&imagen=" + datosLaptop["build"]
            #self.url += "&fechaReporte=" + # Es una fecha que se guarda del lado del servidor 
            self.url += "&firmware=" + datosLaptop["firmware"]
            self.url += "&plazo_bloqueo=" + datosLaptop["plazo-bloqueo"]
            self.url += "&boot_count_bloqueo=" + datosLaptop["boot-count-bloqueo"]
            self.url += "&ult_actualizacion=" + datosLaptop["last-update"]
            self.url += "&espacio_libre=" + datosLaptop["free-space-porc"]
            self.url += "&version=" + datosLaptop["version"]
            self.url += "&installed_update=" + datosLaptop["installed-update"]
            self.url += "&datos_extra=" + urllib.quote_plus(json.dumps({'last_update_especial': datosLaptop["last-update-especial"]}))
        except:
            notificacion(ALERTA_ERROR)

        return registroDatosFaltantes
        
    
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
            return "{'error': " + str(e) + "}"

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
        datos_faltantes = self._concatenar_nuevos_parametros_url()

        # Conecta a la URL del web Service y guarda el contenido en un archivo.
        json_response = self._conectar(self.url)

        try:
            json_response = str.replace(json_response, '\n', '')
            json.loads(json_response)
        except ValueError, e:
            print("Respuesta invalida")
            return None

        self._guardar_en_archivo(json_response)
        
        # Conectamos a la Base de Datos.
        base_de_datos = Store()
        
        # Cargamos las Notificaciones a la Base de Datos.
        base_de_datos.Cargar_notificaciones()
        
        respuesta = { "datos-faltantes": datos_faltantes, "respuesta-servidor": json.loads(json_response) }

        return respuesta

if __name__ == "__main__":
    # Creamos la conexion al Web-Service.
    web=W_S_Conexion(WEB_SERVICE_URL)
    
    # Obtenemos las notificaciones correspondientes.
    web.Obtener_notificaciones(False)