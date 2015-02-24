#!/usr/bin/python
# Version 1.1
# 2010-09-28 - Plan CEIBAL
# Autor: Esteban Bordon - ebordon@plan.ceibal.edu.uy
#
# Setea algunas variables de entorno de los programas - scripts de Ceibal
# Para F11 cambia ceibal_root a "/"

import os


def get_ceibal_root():
    return os.path.join('/')


def get_updates_root():
    return os.path.join(get_ceibal_root(), 'etc', '.actualizaciones')


def get_security_root():
    return os.path.join(get_ceibal_root(), '.seguridad')


def get_conf_root():
    return os.path.join(get_ceibal_root(), '.conf')
