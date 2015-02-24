#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version 1.2
# 2010-09-24 - Plan CEIBAL
# Autor: Esteban Bordon - ebordon@plan.ceibal.edu.uy
#
# Modulo de seguridad de la XO. Realiza los chequeos sobre la lista negra.
# chk_security sólo baja la lista negra pero no realiza chequeos sobre ella
# excepto que la lista negra esté vigente


import os
import time
import re
import shutil

from ceibal import util
from ceibal import env

BLACKLIST = 'blacklist'
TMP_DIR = os.path.join("/", "tmp", "actualizaciones")
BLACKLIST_DIR = env.get_security_root()
BLACKLIST_PATH = os.path.join("/", "seguridad", "lista-negra")


def __download_blacklist(logger, server=None):
    """
    Descarga la lista negra desde el servidor y comprueba su firma.
    """
    if not server:
        server = util.get_gateway()
    blacklist_ok = False
    if util.download_file(server, os.path.join(BLACKLIST_PATH, BLACKLIST),
                                            os.path.join(TMP_DIR, BLACKLIST)):
        if not util.download_file(server, os.path.join(BLACKLIST_PATH,
            BLACKLIST + ".sig"), os.path.join(TMP_DIR, BLACKLIST + ".sig")):
            msg = 'ERROR: No se pudo descargar la firma de la lista negra.'
            logger.debug(time.ctime() + ' - ' + msg)
        else:
            bl_path = os.path.join(TMP_DIR, BLACKLIST + ".sig")
            if util.chk_signature(bl_path):
                # Si la lista esta vencida o vence hoy no la guarda
                today = time.strftime("%Y%m%d", time.localtime())
                bl_path = os.path.join(TMP_DIR, BLACKLIST)
                bl_life = open(bl_path)
                bl_life = bl_life.readlines()[0].strip()
                if bl_life > today:
                    blacklist_ok = True
                    logger.debug(time.ctime() +' - Lista negra descargada correctamente')
                    shutil.copy(bl_path, BLACKLIST_DIR)
                    shutil.copy(bl_path + ".sig", BLACKLIST_DIR)
                else:
                    logger.debug(time.ctime() + ' - ERROR: Lista negra vencida.')
            else:
                msg = 'ERROR: Fallo al comprobar la firma de la lista negra.'
                logger.debug(time.ctime() + ' - ' + msg)
    return blacklist_ok


def __get_blacklist_data():
    """
    Retorna un diccionario con la informacion relativa a la lista negra:
    vencimiento, plazo y lista de sn.
    """
    f = open(os.path.join(TMP_DIR, BLACKLIST), 'r')
    data = f.read().split()
    f.close()
    data_dic = {}
    data_dic["vencimiento"] = data[0]
    data_dic["plazo"] = data[1]
    data_dic["series"] = data[2:]
    return data_dic


def __chk_vigencia(vencimiento):
    """
    Chequea vigencia de la lista negra.
    """
    try:
        fecha = time.strftime("%Y%m%d", time.localtime())
        if int(vencimiento) < int(fecha):
            return False
        else:
            return True
    except:
        return False


def __chk_plazo_format(plazo):
    """
    Chequea el formato del plazo.
    """
    plazore = re.compile(r'^20[0-9]{2}(01|02|03|04|05|06|07|08|09|10|11|12)(01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)$')
    if plazore.match(plazo):
        return True
    else:
        return False


def __chk_plazo(plazo):
    """
    Chequea vigencia del plazo.
    """
    fecha = time.strftime("%Y%m%d", time.localtime())
    if (int(plazo) < int(fecha)):
        return False
    else:
        return True


def __find_sn(sn, list_sn):
    return sn in list_sn


def chk_security(sn, logger, server=None):
    """
    Retorna:
        0 si la laptop esta en la lista negra.
        1 si la laptop no pasa el chequeo pero no esta en la lista negra.
        2
    """
    #state = 1
    __download_blacklist(logger, server)
    """
    if __download_blacklist(logger, server):
        data = __get_blacklist_data()
        if not __chk_vigencia(data["vencimiento"]):
            logger.debug('ERROR: Lista negra vencida. Saliendo...')
        elif not __chk_plazo_format(data["plazo"]):
            logger.debug('ERROR: El formato del plazo no es valido.')
        elif not __chk_plazo(data["plazo"]):
            logger.debug('ERROR: El plazo obtenido es menor que la fecha actual.')
        elif __find_sn(sn, data["series"]):
            logger.debug('MAQUINA EN LA LISTA NEGRA!!!')
            state = 0
        else:
            state = data["plazo"]
    else:
        logger.debug('ERROR: No se pudo descargar la lista negra.')
    return state
    """
