#!/usr/bin/python
# -*- coding: utf-8 -*-
# 2015-03 - Plan CEIBAL Uruguay
# Autor: Francisco Cobas - fcobas@plan.ceibal.edu.uy
#
# Descarga las notificaciones encontradas
# Ultima modificacion: 2015-03

import commands
import os
import sys
import time
import random
import logging
import logging.handlers

from ceibal import env
from ceibal import util

WORK_DIR = env.get_notifications_root()

DIR_SEGURIDAD = env.get_security_root()

ARCH_LOG = os.path.join(WORK_DIR, "notificador.log")
NOTIHOY = os.path.join(WORK_DIR, "notihoy")

def already_running():
    command = 'ps -ef | grep notificador.py | grep -v grep | wc -l'
    status, output = commands.getstatusoutput(command)
    if not status:
        if int(output) <= 2:
            return False
        else:
            return True
    return False


def chk_env(laptop):
    '''
    Realiza el chequeo de los directorios y archivos necesarios para que
    funcione el programa.
    De no existir algun directorio necesario lo crea y le da permisos.
    '''

    if not os.path.isdir(WORK_DIR):
        os.makedirs(WORK_DIR, 0744)

    if laptop in ["XO"] and not os.path.isdir(DIR_SEGURIDAD):
        os.makedirs(DIR_SEGURIDAD, 0700)
        f = open(os.path.join(DIR_SEGURIDAD, "blacklisted"), 'w')
        f.write('0')
        f.close()

    if not os.path.exists(NOTIHOY):
        f=open(NOTIHOY, 'w')
        f.write('00000000')
        f.close()

    os.chmod(NOTIHOY, 0666)


class NotificadorObtener:

    def __init__(self):
        self._updated_today = os.path.join(WORK_DIR, "notihoy")
        self.__set_logger()

        if self.already_checked_for_noti():
            self._logger.debug(time.ctime() + ' -AVISO: Ya se chequearon las notificaciones hoy. Saliendo...')
            exit()

        time_wait = 60
        espera = random.randint(0, time_wait)
        self._logger.debug('Esperando %i segundos...' %espera)
        time.sleep(espera)

        # Importamos la clase W_S_Conexion para conectarons al Web Service.
        from ceibal.notifier.web_service_conexion import W_S_Conexion

        # Importamos las Constantes.
        from ceibal.notifier.constantes import WEB_SERVICE_URL

        # Realizamos la coneccion con el Web Service.
        web = W_S_Conexion(WEB_SERVICE_URL)

        # Obtenemos las notificaciones
        web.Obtener_notificaciones(False)

        self._logger.debug(time.ctime() + '- Se termino el proceso de obtener notificaciones. Saliendo...')

        # Seteamos la hora en el notihoy
        self.__set_update_today()


    def __set_update_today(self):
        '''
        Marca cuando se llamo al WebService
        '''
        util.data_2_file(str(time.time().split('.')[0]), self._updated_today)

    def already_checked_for_noti(self):
        '''
        Retorna True si ya se actualizo hoy
        '''
        retorno = False

        try:
            f = open(self._updated_today, 'r')
        except:
            return False

        horaActualizado = int(f.read())
        f.close()
        horaActual = int(str(time.time()).split('.')[0])
        diffHoras = horaActual - horaActualizado
        if diffHoras < 14400:
            retorno = True
        
        return retorno


    def __set_logger(self):
        FILE_LOG = os.path.join(WORK_DIR, 'notificador.log')
        logging.basicConfig(filename=FILE_LOG,
                            level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filemode='w')

        self._logger = logging.getLogger('notificador')


#############################################################
# main
#############################################################

if __name__ == "__main__":

    if already_running():
        exit()

    modelo = util.get_model_laptop()
    if modelo.startswith('XO'):
        chk_env("XO")
    elif modelo.startswith('Magallanes'):
        chk_env("MG")
    elif modelo.startswith('Positivo'):
        chk_env("Positivo")
    else:
        chk_env("JumPC")

    notificacionesObtener = NotificadorObtener()
