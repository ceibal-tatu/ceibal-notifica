#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version 2.2
# 2013-03-18
# Autor: Esteban Bordon - ebordon@plan.ceibal.edu.uy
# Modificado por Esteban Arias - earias@plan.ceibal.edu.uy
# Representa la laptop, su estado y sus versiones de actualizaciones

# send_data y send_act funcionan para la version 4.1 de mpp_data
# para versiones anteriores no registra el ESSID

import os
import telnetlib
import socket
import ConfigParser
import commands
import sqlite3

import env
import util


###########################################
# constants
###########################################
UPDATES_ROOT = env.get_updates_root()
ARCH_LOG_RESP = UPDATES_ROOT + "/log_resp"
VERSION_ACTUAL = os.path.join(UPDATES_ROOT, "mi_version")
HISTORICO = os.path.join(UPDATES_ROOT, "updates.db")
PLAZO = os.path.join(env.get_security_root(), "blacklist")
ACT_BASE = os.path.join(UPDATES_ROOT, "act_base")
ACTHOY = os.path.join(UPDATES_ROOT, "acthoy")
DIR_TEMPORAL = "/tmp/actualizaciones"


_OFW_MODEL_TREE = '/ofw/mfg-data/MN'
_PROC_MODEL_TREE = '/proc/device-tree/mfg-data/MN'
_MG = '/etc/ceibal-version'
_JUMPC = '/etc/image_version'

init_db = """
CREATE TABLE IF NOT EXISTS updates (version INTEGER NOT NULL,
categoria VARCHAR(30) NOT NULL,
descripcion TEXT NOT NULL ON CONFLICT REPLACE DEFAULT '',
fecha DATETIME DEFAULT current_timestamp,
PRIMARY KEY (version, categoria)); """

###########################################

##########################################
#  functions
###########################################


class Laptop:
    """
    Super clase que modela las laptops y sus atributos
    """
    def __init__(self):
        self._get_sn()
        self._get_mac()
        self._get_build()
        self._get_update_type()
        self._get_model()

    def _get_sn(self):
        pass

    def _get_mac(self):
        pass

    def _get_build(self):
        pass

    def _get_model(self):
        self._model =  get_model_laptop()

    def _dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _run_query(self, query):
        """
        Ejecuta una consulta cualquiera a la base de datos.
        Retorna el resultado de dicha consulta
        """
        conn = sqlite3.connect(HISTORICO, isolation_level=None)
        conn.text_factory = str
        conn.row_factory = self._dict_factory
        c = conn.cursor()
        c.execute('BEGIN TRANSACTION')
        c.execute(query)
        output = c.fetchall()
        c.execute('END TRANSACTION')
        conn.close()
        return output

    def chk_env(self):
        '''
        Realiza el chequeo de los directorios y archivos necesarios para que
        funcione el programa.
        De no existir algun directorio necesario lo crea y le da permisos.
        '''
        util.clean_dir(DIR_TEMPORAL)
        if not os.path.isdir(UPDATES_ROOT):
            os.makedirs(UPDATES_ROOT, 0744)

        if not os.path.isdir(DIR_TEMPORAL):
            os.makedirs(DIR_TEMPORAL)

        if not os.path.exists(ACTHOY):
            f = open(ACTHOY, 'w')
            f.write('00000000')
            f.close()
        if not os.path.exists(VERSION_ACTUAL):
            open(VERSION_ACTUAL, 'w').close()
        # [ebordon] Permisos de escritura para todos (acthoy) y permisos
        # de lectura para todos (miversion)
        os.chmod(VERSION_ACTUAL, 0666)
        os.chmod(ACTHOY, 0666)

    def _get_update_type(self):
        '''
        Obtiene el Tipo de actualizacion correspondiente a la imagen de Sugar.
        '''
        try:
            f = open(UPDATES_ROOT + '/update_type', 'r')
            self._update_type = f.read().strip('\n').replace(" ", "-")
            f.close()
        except:
            self._update_type = None

    def chk_default_update_sections(self):
        """
        Realiza el chequeo de las versiones por defecto
        ('general' y su version de Sugar).
        En caso de no tener alguna seccion le asigna el valor del archivo base.
        """
        if not os.path.exists(HISTORICO):
            conn = sqlite3.connect(HISTORICO, isolation_level=None)
            conn.text_factory = str
            c = conn.cursor()
            c.executescript(init_db)
            conn.close()

        if not os.path.exists(VERSION_ACTUAL):
            #TODO: Inicializar base de datos
            for seccion in ['general', self._update_type]:
                open(VERSION_ACTUAL, 'w').close()
                self.make_update_category(seccion)
                self.set_current_update_version(seccion,
                                    self.get_update_version_base(seccion))

        for section in ['general', self._update_type]:
            config = ConfigParser.ConfigParser()
            config.read(VERSION_ACTUAL)
            if not config.has_section(section):
                config.add_section(section)
                config.set(section, 'version',
                                    self.get_update_version_base(section))
                arch = open(VERSION_ACTUAL, 'w')
                config.write(arch)
                arch.close()

    def get_update_version(self, seccion):
        """
        Obtiene la version de archivo base de configuracion
        @seccion: seccion de donde se busca obtener la version.
        @return: string correspondiente a la version,
          en caso de no existir la seccion retorna '00000000'
        """
        Config = ConfigParser.ConfigParser()
        Config.read(VERSION_ACTUAL)
        if Config.has_section(seccion):
            version = Config.get(seccion, 'version')
        else:
            version = "00000000"
        return version

    #[ebordon] 2009-07-24-+
    # Lee las versiones de cada categoria y las devuelve en un diccionario

    def get_update_version_base(self, seccion):
        """
        Obtiene la version de archivo base de configuracion
        @seccion: seccion de donde se busca obtener la version.
        """
        Config = ConfigParser.ConfigParser()
        Config.read(ACT_BASE)
        if Config.has_section(seccion):
            version = Config.get(seccion, 'version')
        else:
            # Conviene agregar la seccion si no existe?
            #config.add_section(seccion)
            #config.set(seccion,'version','00000000')
            #arch = open(ACT_BASE, 'w')
            #config.write(arch)
            #arch.close()
            version = '00000000'
        return version

    def get_current_active_updates(self):
        Config = ConfigParser.ConfigParser()
        Config.read(os.path.join(VERSION_ACTUAL))
        #Config.read(os.path.join(UPDATES_ROOT, "active_updates.conf"))
        list_actives = Config.sections()
        #list_actives = []
        #for seccion in Config.sections():
        #    active = Config.get(seccion, 'active')
        #    if active:
        #        list_actives.append(seccion)
        return list_actives

    def get_update_history(self):
        query = "select * from updates order by fecha desc"
        return self._run_query(query)

    def get_current_update_version(self):
        Config = ConfigParser.ConfigParser()
        Config.read(VERSION_ACTUAL)
        versiones = {}
        for seccion in Config.sections():
            versiones[seccion] = Config.get(seccion, 'version')
        return versiones

    def make_update_category(self, category):
        """
        Crea una nueva categoria de actualizacion
        """
        config = ConfigParser.ConfigParser()
        config.read(VERSION_ACTUAL)
        if not config.has_section(category):
            config.add_section(category)
            arch = open(VERSION_ACTUAL, 'w')
            config.write(arch)
            arch.close()

    def set_current_update_version(self, seccion, version, descripcion):
        """
        @seccion: Seccion que sera modificada
        @version: Valor que llevara el campo "version" dentro de la seccion
         especificada
        """
        config = ConfigParser.ConfigParser()
        config.read(VERSION_ACTUAL)
        if not config.has_section(seccion):
            config.add_section(seccion)
        config.set(seccion, 'version', version)
        arch = open(VERSION_ACTUAL, 'w')
        config.write(arch)
        arch.close()
        # Se guarda info en la base de datos

        query = 'INSERT INTO updates(version, categoria, descripcion) \
                    VALUES (%i,"%s","%s");' % (int(version), seccion, descripcion)
        self._run_query(query)

    def actualizar(self, on_demand=False):
        from ceibal.actualizador import Actualizador
        act = Actualizador(self, on_demand)
        act.run()


class XO(Laptop):
    def __init__(self):
        Laptop.__init__(self)
        self._get_firmware()
        self._get_plazo()

    def chk_env(self):
        '''
        Realiza el chequeo de los directorios y archivos necesarios para que
        funcione el programa.
        De no existir algun directorio necesario lo crea y le da permisos.
        '''
        Laptop.chk_env(self)

        security_root = env.get_security_root()
        if not os.path.isdir(security_root):
            os.makedirs(security_root, 0700)

        commands.getoutput('chown olpc:olpc %s' % env.get_ceibal_root())
        commands.getoutput('chown olpc:olpc %s' % UPDATES_ROOT)
        #[ebordon] Permisos de escritura para todos (acthoy) y permisos
        # de lectura para todos (miversion)

    def _get_sn(self):
        '''
        Obtiene el numero de serie de la XO
        '''
        if os.path.exists('/ofw/mfg-data/SN'):
            f = open('/ofw/mfg-data/SN', 'r')
            serie = f.read()
            f.close()
            self._sn = serie[0:serie.__len__() - 1]
            #return serie
        elif os.path.exists('/proc/device-tree/mfg-data/SN'):
            f = open('/proc/device-tree/mfg-data/SN', 'r')
            serie = f.read()
            f.close()
            self._sn = serie[0:len(serie) - 1]
        else:
            raise Exception("No se pudo obtener el numero de serie.")

    def _get_mac(self):
        '''
        Obtiene la MAC Address de la XO
        '''
        if os.path.exists('/ofw/mfg-data/WM'):
            f = open('/ofw/mfg-data/WM', 'r')
            mac = f.read()
            f.close()
            mac = mac[0:mac.__len__() - 1]
            self._mac = mac.replace('-', ':')
        elif os.path.exists('/proc/device-tree/mfg-data/WM'):
            f = open('/proc/device-tree/mfg-data/WM', 'r')
            mac = f.read()
            f.close()
            mac = mac[0:len(mac) - 1]
            self._mac = mac.replace('-', ':')
        else:
            raise Exception("No se pudo obtener la mac.")

    def _get_build(self):
        '''
        Obtiene el build number de Sugar.
        '''
        if os.path.exists('/boot/olpc_build'):
            f = open('/boot/olpc_build', 'r')
            self._build = f.read().strip('\n').replace(" ", "-")
            f.close()
        elif os.path.exists('/bootpart/olpc_build'):
            f = open('/bootpart/olpc_build', 'r')
            self._build = f.read().strip('\n').replace(" ", "-")
            f.close()
        else:
            raise Exception("No se pudo obtener el número de build.")

    def _get_firmware(self):
        '''
        Obtiene la version de firmware
        '''
        if os.path.exists('/ofw/openprom/model'):
            f = open('/ofw/openprom/model', 'r')
            self._fw = f.read().split()[1]
            f.close()
        elif os.path.exists('/proc/device-tree/openprom/model'):
            f = open('/proc/device-tree/openprom/model', 'r')
            self._fw = f.read().split()[1]
            f.close()
        else:
            raise Exception("No se pudo obtener la información del Firmware.")

    def _get_plazo(self):
        try:
            f = open(PLAZO, 'r')
            self._plazo = f.readlines()[0].strip('\n')
            f.close()
        except:
            self._plazo = None

    def send_data(self, server, port, msj):
        """
        sn mac build firmware plazo
        Para monitoreo se envian:
        mac, mac_ap, saltos, sn, essid
        """
        command = "/sbin/route |grep default |grep eth"
        temp = os.popen(command).readline().split()
        if len(temp):
            mac_ap = os.popen("/sbin/iwgetid -a").readline().split()[-1]
        else:
            # Si no encuentro la MAC con iwconfig, trato de hacerle
            # arping por si perdi conexion
            mac_ap = util.get_mac_gw()
        essid = util.get_essid()

        conn = telnetlib.Telnet()
        try:
            conn.open(server, port)
            conn.write("MONITOREO %s %s %i %s %s\r\n" % (str(self._mac),
                             mac_ap, util.get_jumps(), str(self._sn), essid))
            conn.close()
            conn.open(server, port)
            conn.write("DATAXO %s %s %s %s %s %s\r\n" % (str(self._sn),
                                    str(self._mac), str(self._build),
                                    str(self._fw), str(self._plazo),str(self._model)))
            conn.close()
        except socket.error:
            raise Exception("send_data(): Error en la conexion")
        except:
            raise Exception("send_data(): Error desconocido")

    def send_act(self, server, port, categoria, version):
        """
        sn tipo version
        """

        conn = telnetlib.Telnet()
        try:
            conn.open(server, port)
            conn.write("ACTXO %s %s %s\r\n" % (str(self._sn), str(categoria),
                                                            str(version)))
            conn.close()
        except socket.error:
            raise Exception("send_act(): Error en la conexion")
        except:
            raise Exception("send_act(): Error desconocido")

    def send_error(self, server, port, categoria=None, version=None, msg=None):
        """
        sn actualizacion mensaje
        """
        # Por el momento se deja de usar ya que genera trafico innecesario
        """
        conn = telnetlib.Telnet()
        try:
            version_act = "" if not categoria else "%s-%s" %(str(categoria),
                                                                 str(version))
            conn.open(server, port)
            conn.write("ERROR %s %s %s\r\n" % (str(self._sn),
                                                         version_act, msg))
            conn.close()
        except socket.error:
            raise Exception, "send_error(): Error en la conexion"
        except:
            raise Exception, "send_error(): Error desconocido"
        """
        pass


class JumPc(Laptop):
    """
    def __init__(self):
        Laptop.__init__(self)
    """

    def _get_mac(self):
        try:
            command = "/sbin/ifconfig | grep wlan1"
            self._mac = os.popen(command).readline().split()[4]
        except:
            raise Exception("No se pudo obtener la mac wireless.")

    def _get_build(self):
        '''
        Obtiene el build number de Sugar.
        '''
        try:
            f = open('/boot/olpc_build', 'r')
            #FIXME: El build se saca de ahí?
            self._build = f.read().strip('\n').replace(" ", "-")
            f.close()
        except:
            self._build = None

    def send_data(self, server, port, msj):
        """
        sn mac build firmware plazo
        Para monitoreo se envian:
        mac, mac_ap, saltos, sn, essid
        """
        command = "/usr/sbin/route |grep default |grep wlan1"
        temp = os.popen(command).readline().split()
        if len(temp):
            mac_ap = os.popen("/usr/sbin/iwgetid -a").readline().split()[-1]
        else:
            # Si no encuentro la MAC con iwconfig, trato de hacerle arping por
            #si perdi conexion
            mac_ap = util.get_mac_gw()
        essid = util.get_essid()

        conn = telnetlib.Telnet()
        try:
            conn.open(server, port)
            conn.write("MONITOREO %s %s %i %s %s\r\n" % (str(self._mac),
                              mac_ap, util.get_jumps(), str(self._mac), essid))
            conn.close()
            conn.open(server, port)
            conn.write("DATAXO %s %s %s %s %s %s\r\n" % (str(self._mac),
                                str(self._mac), str(self._build), " ", " ",str(self._model)))
            conn.close()
        except socket.error:
            raise Exception("send_data(): Error en la conexion")
        except:
            raise Exception("send_data(): Error desconocido")

    def send_act(self, server, port, categoria, version):
        """
        sn tipo version
        """

        conn = telnetlib.Telnet()
        try:
            conn.open(server, port)
            conn.write("ACTXO %s %s %s\r\n" % (str(self._mac),
                                             str(categoria), str(version)))
            conn.close()
        except socket.error:
            raise Exception("send_act(): Error en la conexion")
        except:
            raise Exception("send_act(): Error desconocido")

    def send_error(self, server, port, categoria=None, version=None, msg=None):
        """
        sn actualizacion mensaje
        """
        # Por el momento se deja de usar ya que genera trafico innecesario
        """
        conn = telnetlib.Telnet()
        try:
            version_act = "" if not categoria else "%s-%s" %(str(categoria),
                                                                 str(version))
            conn.open(server, port)
            conn.write("ERROR %s %s %s\r\n" % (str(self._sn),version_act, msg))
            conn.close()
        except socket.error:
            raise Exception, "send_error(): Error en la conexion"
        except:
            raise Exception, "send_error(): Error desconocido"
        """
        pass


class MG(Laptop):
    """
    def __init__(self):
        Laptop.__init__(self)
    """

    def _get_mac(self):
        '''
        Obtiene la MAC Address de la MG2
        '''
        try:
            command = "/sbin/ifconfig |grep wlan0 | grep HW | awk '{print $5}'"
            mac = commands.getoutput(command)
            self._mac = mac.strip()
        except:
            raise Exception("No se pudo obtener la mac.")

    def _get_build(self):
        '''
        Obtiene la version del metasys.
        '''
        try:
            f = open('/etc/ceibal-version', 'r')
            self._build = f.read().strip()
            f.close()
        except:
            self._build = None

    def send_data(self, server, port, msj):
        """
        sn mac build firmware plazo
        Para monitoreo se envian:
        mac, mac_ap, saltos, sn, essid
        """
        command = "/sbin/route | grep default | grep wlan0"
        temp = os.popen(command).readline().split()
        if len(temp):
            mac_ap = os.popen("/usr/sbin/iwgetid -a").readline().split()[-1]
        else:
            # Si no encuentro la MAC con iwconfig,
            #trato de hacerle arping por si perdi conexion
            mac_ap = util.get_mac_gw()
        essid = util.get_essid()

        conn = telnetlib.Telnet()
        try:
            conn.open(server, port)
            conn.write("MONITOREO %s %s %i %s %s\r\n" % (str(self._mac),
                            mac_ap, util.get_jumps(), str(self._mac), essid))
            conn.close()
            conn.open(server, port)
            # El encabezado es DATAXO siempre
            conn.write("DATAXO %s %s %s %s %s %s\r\n" % (str(self._mac),
                                str(self._mac), str(self._build), " ", " ",str(self._model)))
            conn.close()
        except socket.error:
            raise Exception("send_data(): Error en la conexion")
        except:
            raise Exception("send_data(): Error desconocido")

    def send_act(self, server, port, categoria, version):
        """
        sn tipo version
        """

        conn = telnetlib.Telnet()
        try:
            conn.open(server, port)
            conn.write("ACTXO %s %s %s\r\n" % (str(self._mac),
                                         str(categoria), str(version)))
            conn.close()
        except socket.error:
            raise Exception("send_act(): Error en la conexion")
        except:
            print Exception
            raise Exception("send_act(): Error desconocido")

    #no hace nada, pero lo llaman cuando falla la actualizacion
    def send_error(self, server, port, categoria=None, version=None, msg=None):
        """
        sn actualizacion mensaje
        """
        # Por el momento se deja de usar ya que genera trafico innecesario
        """
        conn = telnetlib.Telnet()
        try:
            version_act = "" if not categoria else "%s-%s" %(str(categoria),
                                                             str(version))
            conn.open(server, port)
            conn.write("ERROR %s %s %s\r\n" % (str(self._sn),version_act, msg))
            conn.close()
        except socket.error:
            raise Exception, "send_error(): Error en la conexion"
        except:
            raise Exception, "send_error(): Error desconocido"
        """
        pass


def get_model_laptop():
    '''
    Obtiene el modelo de laptop
    '''
    model = None
    if os.path.exists(_OFW_MODEL_TREE):
        model = util.read_file(_OFW_MODEL_TREE)
    elif os.path.exists(_PROC_MODEL_TREE):
        model = util.read_file(_PROC_MODEL_TREE)
    #FIXME: Revisar si hay una ruta en las laptops donde se obtiene el modelo
    elif os.path.exists(_MG):
        model = 'Magallanes'
    elif os.path.exists(_JUMPC):
        model = 'JumPc'
    return model
