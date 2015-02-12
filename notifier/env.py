#! /usr/bin/python
# -*- coding:utf-8 -*-
# env.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
#-------------------------------------------------------
# Setea algunas variables de entorno del notificador.
#-------------------------------------------------------

import os
from ceibal import env

def get_data_root():
    '''
    @summary: Obtiene la ruta donde esta la DB.
    @return: Retorna la ruta.
    '''
    return os.path.join(env.get_ceibal_root(),'etc','notifier', 'data')

def get_images_root():
    '''
    @summary: Obtiene la ruta donde esta la imagen.
    @return: Retorna la ruta.
    '''
    return os.path.join(env.get_ceibal_root(),'etc','notifier', 'images')

