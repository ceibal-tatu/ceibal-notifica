#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, commands, platform

print "Desinstalando de:", platform.platform()
print commands.getoutput('rm -r /usr/local/share/CeibalNotifica')
print commands.getoutput('rm /usr/share/applications/CeibalNotifica.desktop')
print commands.getoutput('rm /usr/local/bin/CeibalNotifica')
print commands.getoutput('rm /usr/local/bin/CeibalNotificaUninstall')
print "CeibalNotifica se ha Desinstalado Correctamente del Sistema"

