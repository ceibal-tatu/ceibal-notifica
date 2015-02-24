#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version 6.1
# 2012-10-25 - Plan CEIBAL
# Autor: Emiliano Pastorino - epastorino@plan.ceibal.edu.uy
# Modificado por Esteban Bordon - ebordon@plan.ceibal.edu.uy
#
# Descarga e instala las actualizaciones faltantes de la XO.
# A partir de la versión 5.0 no bloquea la XO. Sólo descarga la lista negra.
#

# TODO
# Crear clases para manejar excepciones, por el momento se tiran para arriba
# con un mensaje.
#

import os
import time
import commands
import random
import tarfile
import logging
import logging.handlers

from ConfigParser import ConfigParser, NoSectionError

from ceibal import env
from ceibal import util
from ceibal import security

###########################################
# constants
###########################################
TMP_DIR = "/tmp/actualizaciones"
WORK_DIR = env.get_updates_root()
#ARCH_LOG_RESP = os.path.join(WORK_DIR, "log_resp")


class Actualizador:
    def __init__(self, laptop, on_demand=False):
        self._laptop = laptop
        self._laptop.chk_default_update_sections()
        self._update_list = 'actualizaciones.list'
        self._updated_today = os.path.join(WORK_DIR, "acthoy")
        self._port = 5000
        self._on_demand = on_demand
        try:
            self._server = util.get_gateway()
        except:
            self._server = None
        self.__send_update_info()

    def __set_logger(self, mode):
        self._logger = logging.getLogger('actualizador')
        self._logger.setLevel(logging.DEBUG)
        # Add the log message handler to the logger
        handler = logging.FileHandler(os.path.join(WORK_DIR,
                "actualizador.log"), mode)  # ,maxBytes= 300, backupCount= 1)
        self._logger.addHandler(handler)

    def __log(self, msg):
        """
        Guarda el mensaje en el log del programa
        """
        self._logger.debug("%s - %s" % (time.ctime(), msg))

    def __send_update_info(self):
        first_act = os.path.join(WORK_DIR, "first_act")
        if not os.path.exists(first_act):
            versions = self.get_current_version()
            for version in versions:
                self.__send_act(version, versions[version])
            open(first_act, 'w').close()

    def __send_data(self, msj):
        """
        Envia la informacion de la XO hacia el servidor
        """
        self._laptop.send_data(self._server, self._port, msj)

    def __send_act(self, categoria, version):
        """
        Envia la informacion de la actualizacion indicada
        de la XO hacia el servidor
        """
        self._laptop.send_act(self._server, self._port, categoria, version)

    def __send_error(self, categoria, version, msg):
        """
        Envia la informacion del error ocurrido durante la actualizacion.
        """
        self._laptop.send_error(self._server, self._port,
                                                     categoria, version, msg)

    def get_sn(self):
        #TODO: Agregar el método get_sn() en la clase Laptop
        return self._laptop._sn

    def __set_update_today(self):
        """
        Marca que hoy se realizo una actualizacion
        """
        util.data_2_file(time.strftime('%Y%m%d', time.localtime()),
                                                         self._updated_today)

    def get_current_version(self):
        """
        Retorna un diccionario con las versiones actuales de cada
        actualizacion para la XO
        """
        return self._laptop.get_current_update_version()

    def __install_update(self, categoria, version):
        """
        Instala la actualizacion en la categoria indicada
        """
        util.clean_dir(TMP_DIR)
        error = False
        # el nombre del archivo de actualizacion debe ser
        # ceibal-<aaammdd>-<categoria>.tar.gz
        nombre_archivo = 'ceibal-%s-%s.tar.gz' % (categoria, version)
        filename = os.path.join('/', 'actualizaciones', categoria,
                                                                nombre_archivo)
        self.__log('Intentando descargar %s' % nombre_archivo)
        data = util.download_file(self._server, filename,
                                     os.path.join(TMP_DIR, nombre_archivo))
        if not data:
            msg = "ERROR: No se encuentra el archivo %s. Saliendo" % filename
            error = True
            return error, msg
        data = util.download_file(self._server, filename + ".sig",
                                os.path.join(TMP_DIR, nombre_archivo + '.sig'))
        if not data:
            msg = "ERROR: No se encuentra el archivo %s. Saliendo" % filename
            error = True
            return error, msg
        if not util.chk_signature(os.path.join(TMP_DIR,
                                               '%s.sig' % (nombre_archivo))):
            msg = 'ERROR: Firma de %s INVALIDA. Saliendo...' % nombre_archivo
            error = True
            return error, msg
        arch_tar = tarfile.open(os.path.join(TMP_DIR, nombre_archivo))
        arch_tar.extractall(TMP_DIR)
        if self.__chk_install():
            if self.__chk_deps(os.path.join(TMP_DIR, "deps.list")):
                desc = self.__get_desc(os.path.join(TMP_DIR, "info"))
                print desc
                os.chdir(TMP_DIR)
                output = commands.getstatusoutput('sh instalar')
                os.chdir(WORK_DIR)
                if output[0] > 0:
                    msg = '\t' + output[1]
                else:
                    msg = "actualizacion instalada"
                    self._laptop.set_current_update_version(categoria, version,
                                                                        desc)
                    self.__send_act(categoria, version)
            else:
                msg = 'La actualizacion (%s) %s no se instalo: \
                                faltan dependencias' % (categoria, version)
        else:
            msg = 'La actualizacion (%s) %s no corresponde a esta XO' \
                                                        % (categoria, version)
        return error, msg

    def already_checked_for_act(self):
        """
        Retorna True si ya se realizo un chequeo hoy
        """
        f = open(self._updated_today, 'r')
        dia = f.read()
        f.close()
        hoy = time.strftime("%Y%m%d", time.localtime())
        return dia == hoy

    def __chk_deps(self, file):
        """
        Revisa dependencias de la actualizacion
        @file: archivo con las dependencias de la actualizacion, el formato es
                categoria:version
                categoria:version
                .
                .
                .
        """
        result = True
        try:
            lines = open(file).readlines()
            while result and (len(lines) > 0):
                line = lines.pop()
                tupla = line.split(":")
                category = tupla[0].strip()
                version = int(tupla[1].strip())
                result = version <= int(self._laptop.get_update_version(category))
        except IOError:
            result = True
        return result

    def __get_desc(self, archivo):
        """
        Obtiene la descripción de la actualización
        """
        try:
            parser = ConfigParser()
            parser.read(archivo)
            desc = parser.get("info", 'descripcion')
            return desc
        except:
            return "No disponible"

    # [ebordon] 2009-07-24
    # Lista en un diccionario las actualizaciones faltantes en cada categoria
    def get_list_available_updates(self, installed_updates, available_updates):
        """
        @installed_updates: Diccionario con la ultima version en cada categoria
        @available_updates: Archivo con las actualizaciones disponibles en
         cada categoria
        """
        #TODO: Aca lo que se debería hacer es:
        # Obtener las disponibles, filtrar las mayores a act_base, sacar las
        # ya instaladas.
        available = ConfigParser()
        available.read(available_updates)
        versiones = {}
        for seccion in installed_updates.keys():
            try:
                lista = map(lambda x: x[1], available.items(seccion))
                mi_version = installed_updates[seccion]
                # me quedo con las versiones mayores a la mia
                lista = filter(lambda x: int(x) > int(mi_version), lista)
                versiones[seccion] = sorted(lista)
            except NoSectionError:
                pass
        return versiones

    def __chk_sn_install(self, list_sn):
        """
        Revisa si la actualizacion corresponde al sn intenta instalarla.
        """
        result = False
        try:
            arch = open(list_sn)
            list_sn = map(lambda x: x.strip("\n"), arch.readlines())
            result = self._laptop._sn in list_sn
        except IOError:
            result = True
        except:
            result = False

        return result

    def __chk_conf_install(self, conf_file):
        """
        Revisa si la actualizacion corresponde a la configuracion
        de la XO que intenta instalarla.
        """
        result = True
        try:
            arch = open(conf_file)
            list_conf = map(lambda x: x.strip("\n"), arch.readlines())
            active_cats = self._laptop.get_current_active_updates()
            for conf in list_conf:
                result = result and (conf in active_cats)
            #result = self._laptop._sn in list_sn
        except IOError:
            result = True
        except:
            result = False
        return result

    def __chk_install(self):
        """
        Revisa si la actualizacion corresponde a la XO que intenta instalarla.
        """
        list_sn = os.path.join(TMP_DIR, "sn.list")
        extra_conf = os.path.join(TMP_DIR, "extra.conf")
        return self.__chk_sn_install(list_sn) and \
                                        self.__chk_conf_install(extra_conf)

    def run(self):
        """
        Busca las actualizaciones disponibles para las categorias habilitadas,
        baja e instala las actualizaciones disponibles
        """
        print os.getcwd()
        os.chdir(TMP_DIR)
        print os.getcwd()
        # Si la actualizacion es a demanda ignora este if
        if not self._on_demand and self.already_checked_for_act():
            self.__set_logger('a')
            self.__log('AVISO: Ya hubo un chequeo hoy. Saliendo...')
            exit()
        else:
            self.__set_logger('w')

        time_wait = 60
        if self._on_demand:
            time_wait = 10
        espera = random.randint(0, time_wait)
        self.__log('Esperando %i segundos...' %espera)
        time.sleep(espera)

        if not self._server:
            self.__log('No se pudo obtener una direccion \
            para el servidor. Saliendo...')
            exit()

        msg = 'Chequeando conexion al servidor (%s)...' % self._server
        self.__log(msg)

        if not util.chk_connection(self._server):
            self.__log('ERROR: No existe ruta al servidor. Saliendo')
            exit()
        self.__log('Conexion establecida con %s' % self._server)
        self.__send_data(0)
        # Si la laptop es una XO se debe descargar la blacklist
        if self._laptop.__class__.__name__ == "XO":
            security.chk_security(self.get_sn(), self._logger, self._server)
        self.__log('Intentando descargar lista de actualizaciones...')
        update_list = util.download_file(self._server, '/actualizaciones/' +
                   self._update_list, os.path.join(TMP_DIR, self._update_list))

        if not update_list:
            self.__log('ERROR: No se pudo descargar la lista de \
actualizaciones. Saliendo...')
            exit()
        self.__log('Se obtuvo la lista de actualizaciones.')
        self.__log('Buscando actualizaciones faltantes...')
        faltantes = self.get_list_available_updates(self.get_current_version(),
                                    os.path.join(TMP_DIR, self._update_list))
        if not len(faltantes):
            self.__log('No se necesita actualizar. Saliendo...')
            self.__set_update_today()
            exit()

        for categoria in faltantes.keys():
            if not len(faltantes[categoria]):
                pass
            else:
                self.__log('Se van a instalar %i actualizaciones en %s.' %
                                (faltantes[categoria].__len__(), categoria))
                for version in faltantes[categoria]:
                    error, msg = self.__install_update(categoria, version)
                    self.__log(msg)
                    if error:
                        self.__send_error(categoria, version,
                                        "No se pudo instalar la actualizacion")
        self.__log('Actualizaciones finalizadas. Saliendo...')
        self.__send_data(7)
        self.__set_update_today()


