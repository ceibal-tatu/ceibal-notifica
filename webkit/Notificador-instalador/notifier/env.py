#! /usr/bin/python
# -*- coding:utf-8 -*-
# env.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
#-------------------------------------------------------
# Setea algunas variables de entorno del notificador.
#-------------------------------------------------------

import os
from os.path import expanduser

def get_path_home():
    if os.getenv['SUDO_UID'] != '':
        if os.path.isdir("/home/olpc"):
            return '/home/olpc'
        elif os.path.isdir("/home/ceibal"):
            return '/home/ceibal'
        else:
            return '/root'
    else:
        return expanduser('~')

def get_data_root():
    '''
    @summary: Obtiene la ruta donde esta la DB.
    @return: Retorna la ruta.
    '''
    return os.path.join(get_path_home(),'.notifier', 'data')

def get_images_root():
    '''
    @summary: Obtiene la ruta donde esta la imagen.
    @return: Retorna la ruta.
    '''
    return os.path.join(get_path_home(),'.notifier', 'images')

