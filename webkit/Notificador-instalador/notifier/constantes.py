#! /usr/bin/python
# -*- coding:utf-8 -*-
# constantes.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
#-----------------------------------------------------------------------------------
# Guarda los mensajes obtenidos desde un Web Service.
# Actualmente se guardan en una base de datos sqlite3 y los archivos vienen en json
#-----------------------------------------------------------------------------------

# Archivo JSON donde estan las notificaciones al descargarlas del Web-Service.
TMP_JSON="/tmp/notify_json"

# Imagen de las notificaciones.
IMAGEN_NOTOFY="planceibal.png"

# Base de Datos Sqlite3 donde se guardan las notificaciones.
DB_FILE="messages.db"

# URL al Servicio Web.
WEB_SERVICE_URL="http://notificaciones.ceibal.webfactional.com/index/obtenermensajes/"

# Archivo para saber el Build de una Magallanes o Positivo.
IMG_VERSION="/etc/ceibal-version"

# Texto del boton con accion general.
BTN_GENERAL="Has Clic acá!"

# Texto del boton con accion link.
BTN_LINK="Ir al Link!"

# Tiempo en segundo en deplegar siguiente mensaje.
TIME_ENTRE_MSJ=5

# Tiempo de espera a que esten todos los componentes cargados.
TIME_ESPERA=15

# Mensajes de Alerta.
ALERTA_ERROR="No se pudieron obtener los datos \n necesarios para obtener las notificaciones."
ALERTA_SN="No se pudo obtener el Número de Serie."

# Archivo que registra los messages marcados como leidos
READ_FILE = 'files_read.json'

# -----------------------------------------------
# Claves que llegan en el json del Web Service.
JSON_KEYS=['mensaje_id',
           'mensaje_vencimiento',
           'mensaje_abrir_como',
           'mensaje_url_boton',
           'mensaje_nombre',
           'mensaje_corto',
           'mensaje_html',]
# Traduccion de las claves para la insersion en DB.
DIC_KEYS=['id',
          'vencimiento',
          'funcion',
          'accion',
          'titulo',
          'texto',
          'html',
          'imagen']
# Lista de funciones/propridades.
FUNCIONES_PRIORIDAD=['sin_accion',
                     'general',
                     'url',
                     'institucional']
# ------------------------------------------------

INIT_DB = """
CREATE TABLE IF NOT EXISTS "notifications" ("id" INTEGER PRIMARY KEY NOT NULL,
"vencimiento" DATE NOT NULL DEFAULT CURRENT_DATE,
"funcion" TEXT DEFAULT '',
"accion" TEXT DEFAULT '',
"titulo" TEXT NOT NULL DEFAULT '',
"texto" TEXT NOT NULL DEFAULT '',
"html" TEXT DEFAULT '',
"imagen" TEXT DEFAULT '');
"""

#-----------------------------------------------------------------------------------------
#---------------- Constantes usadas en utilidades.py -------------------------------------

LISTA_XO=["XO-1","XO-1.5","XO-1.5HS","XO-1.5-Lite","XO-1.75","XO-4 Touch"]
LISTA_CLASSMATE=["MG1","MG2","MG3","MG4","MG6","JumPC","Magallanes2"]
LISTA_POSITIVO=["Positivo BGH"]

OFW_MODEL_TREE = '/ofw/mfg-data/MN'
PROC_MODEL_TREE = '/proc/device-tree/mfg-data/MN'
CLASSMATE_MODELO = '/etc/laptop_model'

CLASSMATE_BUILD = '/etc/image_version'
POSITIVO_BUILD = '/etc/ceibal-version'
