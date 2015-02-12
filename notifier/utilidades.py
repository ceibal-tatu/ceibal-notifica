#! /usr/bin/python
# -*- coding:utf-8 -*-
# utilidades.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
#------------------------------------------------------------------------------------
# Archivo con funcionalidades utiles para el sistema de Notificacion.
#------------------------------------------------------------------------------------

import sys
import os

from ceibal.notifier.constantes import CLASSMATE_MODELO,CLASSMATE_BUILD,POSITIVO_BUILD
from ceibal.notifier.constantes import LISTA_XO,LISTA_CLASSMATE,LISTA_POSITIVO,OFW_MODEL_TREE,PROC_MODEL_TREE

def redimensionar_texto(caracteres,texto):
    '''
    @param caracteres: Numero de caracteres por linea.
    @param texto: Texto a redimencionar.
    @summary: Funcion para colocar "Enter" en Strings. De esta manera el texto no se sale de la pantalla.
    @return: Texto redimencionado.
    '''
    texto_nuevo=''
    contador=0
    for char in texto:
        contador = contador + 1
        if contador > caracteres-5 and char == ' ':
            texto_nuevo = texto_nuevo + '\n'
            contador = 0
        else:
            texto_nuevo = texto_nuevo + char
    return texto_nuevo


def browser_fedora():
    '''
    @summary: Obtiene, mediente el proceso del texto de un comando, cual navegador esta configurado por defecto.
    @return: Retorna el navegador. Puede ejecutarse como comando.
    '''
    from subprocess import Popen, PIPE
    
    file_browser = check_output(["xdg-settings","get","default-web-browser"])
    
    p1 = Popen(["cat","/usr/share/applications/"+str(file_browser[0:-1])], stdout=PIPE)
    p2 = Popen(["grep","Exec"], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["tr","'='","' '"], stdin=p2.stdout, stdout=PIPE)
    p4 = Popen(["head", "-n", "1"], stdin=p3.stdout, stdout=PIPE)
    p5 = Popen(["awk",'{print $2}'], stdin=p4.stdout, stdout=PIPE).communicate()[0][0:-1]

    return p5

def es_imagen_Ubuntu_10():
    '''
    @summary: Verifica que la laptop este flasheada con Ubuntu-10.04
    @return: Devuelve si lo es o no.
    '''
    import os
    if os.path.exists("/etc/ceibal-version"):
        if "CM_Ubuntu_a14" == open("/etc/ceibal-version").read()[0:-1]:
            return True
        if "CM_Ubuntu_a13" == open("/etc/ceibal-version").read()[0:-1]:
            return True
        return False
    else:
        return False

def get_model_laptop():
    '''
    @summary: Obtiene el modelo de laptop.
    @return: Retorna el modelo de la laptop.
    '''
    import re
    model = None
    if os.path.exists(OFW_MODEL_TREE):
        model = open(OFW_MODEL_TREE).read().strip()[0:-1]
    elif os.path.exists(PROC_MODEL_TREE):
        model = open(PROC_MODEL_TREE).read().strip()[0:-1]
    elif os.path.exists(CLASSMATE_MODELO):
        model = open(CLASSMATE_MODELO).read().strip()
    return re.sub(" ","",model)

def get_sn_classmate():
    '''
    @summary: Obtiene el numero de serie de las laptop modelo CLassmate.
    @return: Retorna el numero de serie de la laptop.
    '''
    import re
    from subprocess import Popen, PIPE
    p1 = Popen(["ifconfig"], stdout=PIPE)
    p2 = Popen(["grep","eth0"], stdin=p1.stdout ,stdout=PIPE)
    p3 = Popen(["cut","-d",' ', "-f11"], stdin=p2.stdout, stdout=PIPE).communicate()[0][0:-1]
    numero_serie=re.sub(":","",p3).upper()
    return numero_serie

def get_sn_positivo():
    '''
    @summary: Obtiene el numero de serie de las laptop modelo Positivo.
    @return: Retorna el numero de serie de la laptop.
    '''
    from subprocess import check_output
    putout = check_output(["sudo","dmidecode","-s", "baseboard-serial-number"])
    numero_serie=putout[0:-1]
    return numero_serie

def get_sn_xo():
    '''
    @summary: Obtiene el numero de serie de las laptop modelo XO.
    @return: Retorna el numero de serie de la laptop.
    '''
    from ceibal.laptops import XO
    xo=XO()
    return xo._sn

def get_tipo_laptop():
    '''
    @summary: Funcion que especifica en que grupo de moledos pertenece la laptop.
    @return: Retorna un valor correspondiente el grupo.
    '''
    modelo=get_model_laptop()
    if(filter(lambda x: x == modelo, LISTA_XO) != []):
        return 0
    if(filter(lambda x: x == modelo, LISTA_CLASSMATE) != []):
        return 1
    if(filter(lambda x: x == modelo, LISTA_POSITIVO) != []):
        return 2

def get_build_xo():
    '''
    @summary: Obtiene el nombre de la imagen de las laptop modelo XO.
    @return: Nombre de la Imagen.
    '''
    from ceibal.laptops import XO
    xo=XO()
    return xo._build

def get_build_otras():
    '''
    @summary: Obtiene el nombre de la imagen de las laptop modelo Classmate y Positivo.
    @return: Nombre de la Imagen.
    '''
    build=None
    if os.path.exists(CLASSMATE_BUILD):
        build = open(CLASSMATE_BUILD).read().strip()
    if os.path.exists(POSITIVO_BUILD):
        build = open(POSITIVO_BUILD).read().strip()
    return build

def get_ci():
    return ""

def obtener_parametros():
    '''
    @summary: Obtiene todos los parametros necesarios para consumir el Web-Service.
    @return: Lista de parametros.
    '''
    tipo=get_tipo_laptop()
    print tipo
    if (tipo == 0):
        return [str(get_ci()),str(get_sn_xo()), str(get_model_laptop()), str(get_build_xo())]
    if (tipo == 1):
        return [str(get_ci()),str(get_sn_classmate()), str(get_model_laptop()), str(get_build_otras())]
    if (tipo == 2):
        return [str(get_ci()),str(get_sn_positivo()), str(get_model_laptop()), str(get_build_otras())]

def notificacion(texto):
    '''
    @summary: Envia una notificacion de alerta con el texto recivido como parametro.
    @param text: Texto del mensaje.
    '''
    comando = "notify-send Atención! "
    comando = comando + "\""+texto+"\""
    os.system(comando)
    