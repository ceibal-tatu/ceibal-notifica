#!/usr/bin/python
# -*- coding: utf-8 -*-
# 2015-03 - Plan CEIBAL Uruguay
# Autor: Francisco Cobas - fcobas@plan.ceibal.edu.uy
#
# Descarga las notificaciones encontradas
# Ultima modificacion: 2015-04

import os
import sys
import json

TMP_JSON = '/tmp/notify_json'

def chequear_cambio_cron():
    if os.path.exists('/etc/cron.d/notifier'):
        cron = open('/etc/cron.d/notifier', 'r')
        data = cron.read()
        cron.close()
        minutos = data.split('\n')[4].split(' ')[0].split('/')[1]

        json_response = open(TMP_JSON, 'r')
        contenido = json.loads(json_response.read())
        json_response.close()
        frecuencia_cron = contenido['frecuencia']

        if minutos != frecuencia_cron:

            usuario = sys.argv[1]

            if usuario is not None:
                notifier = open('/etc/cron.d/notifier', 'w')
                texto = 'SHELL=/bin/sh\nPATH=/usr/local/sbin:/usr/local/bin:/bin:/usr/sbin:/usr/bin\nDISPLAY=:0\n\n*/' + frecuencia_cron + ' * * * * ' + usuario
                texto += ' /usr/bin/python /usr/sbin/notificador-obtener'
                texto += '\n@reboot root /usr/bin/python /usr/sbin/notificador-chequeo-cron.py ' + usuario
                notifier.write(texto)
                notifier.close()


chequear_cambio_cron()