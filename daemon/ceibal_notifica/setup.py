#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   setup.py por: Flavio Danesse fdanesse@activitycentral.com
#   https://sites.google.com/site/flaviodanesse/
#   https://sites.google.com/site/sugaractivities/
#   http://codigosdeejemplo.blogspot.com/

import commands
from distutils.core import setup

setup(name="CeibalNotifica",  
      	version = "1",
      	author = "Flavio Danesse",
      	author_email = "fdanesse@activitycentral.com",
      	license = "GPL3",
      	scripts = ["CeibalNotifica", "CeibalNotificaUninstall"],
      	py_modules = ['CeibalNotifica', 'CeibalNotificaUninstall'],
		data_files = [('/usr/share/applications/', ['CeibalNotifica.desktop']),
		('', ['CeibalNotificaUninstall.py']),
		('Iconos', ['Iconos/ceibal.png', 'Iconos/ceibal-gris.png'])])
