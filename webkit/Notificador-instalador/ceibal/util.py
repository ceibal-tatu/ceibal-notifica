#!/usr/bin/python
# Version 1.1
# 2012-01-24 - Plan CEIBAL
# Autor: Esteban Bordon - ebordon@plan.ceibal.edu.uy
# Modify by: Esteban Arias - earias@plan.ceibal.edu.uy
# util.py
# Libreria miscelanea de CEIBAL

import telnetlib
import socket
import httplib
import GnuPGInterface
import os
import shutil
import commands


def chk_signature(path_to_signature):
    try:
        gpg = GnuPGInterface.GnuPG()
        salida = gpg.run(['--verify'],args=[path_to_signature],create_fhs=['status'])
        return salida.handles['status'].read().strip().split('[GNUPG:]')[2].split()[0] == "GOODSIG"
    except:
        return False


def data_2_file(data, file):
    try:
        f = open(file, 'w')
        f.write(data)
        f.close()
        return True
    except:
        return False


def get_gateway():
    try:
        f = open('/etc/resolv.conf', 'r')
        server = f.read().strip().split('nameserver ')[1].strip()
        return server
    except Exception, e:
        raise Exception(str(e))


def get_mac_gw():
    ip = os.popen("route |grep default").readline().split()[1]
    arping = os.popen("arping -I wlan0 -c 2 %s" % ip)
    arping.readline()
    return str(arping.readline().split()[4].split("[")[1].split("]")[0])


def get_essid():
    return str(commands.getoutput("iwgetid").split()[1].split(":")[1])


def chk_portal():
    """Chequea si la conexion es a traves de un AP"""
    portal = "CLIENTE"
    if len(os.popen("route |grep eth0 |grep default").readline().split()):
        # Esta conectada por un AP, chequeo ser portal
        portal = "NOPORTAL"
        if len(os.popen("netstat -nlp |grep dhcpd").readline()):
            portal = "PORTAL"
    return portal


def get_jumps():
    mesh = os.popen("route |grep default |grep msh0").readline().split()
    saltos = 0
    if len(mesh) != 0:
        os.popen("ping -c 2 -W 1 %s > /dev/null" % mesh[1])
        os.popen("sleep 5")
        arp = os.popen("arp |grep %s" % mesh[1]).readline().split()
        if len(arp):
            saltos = os.popen("iwpriv msh0 fwt_lookup %s" % arp[2])
            saltos = saltos.readline().split()[10]
    return saltos


def download_file(server, file, dest_file):
    try:
        conn = httplib.HTTPConnection(server)
        conn.putrequest('GET', file)
        conn.putheader('Pragma', 'no-cache')
        conn.endheaders()
        response = conn.getresponse()
        if response.status != 200:
            conn.close()
            return False
        else:
            data = response.read()
            conn.close()
            return data_2_file(data, dest_file)
    except:
        raise Exception("No se pudo descargar el archivo")


def chk_connection(server, port=5000, timeout=3):
    #[ebordon] 2009-07-15, intenta loguearse por telnet
    socket.setdefaulttimeout(timeout)
    conn = telnetlib.Telnet()
    try:
        conn.open(server, port)
        connection = True
        conn.close()
    except socket.timeout, socket.error:
        connection = False
    return connection


def clean_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def read_file(path):
    if os.access(path, os.R_OK) == 0:
        return None

    fd = open(path, 'r')
    value = fd.read()
    fd.close()
    if value:
        value = value.strip('\n')
        return value
    else:
        return None
