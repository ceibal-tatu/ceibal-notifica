#!/usr/bin/python
# -*- coding: utf-8 -*-

# Flavio Danesse - fdanesse@activitycentral.com

import shelve
import sqlite3
import time
import datetime
import os
from store import *

# Archivo notificaciones # http://docs.python.org/library/shelve.html
filename = os.path.join('/tmp', 'notify_0')
d = shelve.open(filename)
d['id'] = 0
d['title'] = "Uruguay"
d['text'] = '''Uruguay, oficialmente República Oriental del Uruguay, es un país de América del Sur, situado en la parte oriental del Cono Sur americano.
Limita al noreste con Brasil —estado de Río Grande del Sur—, al oeste con Argentina —provincias de Entre Ríos y Corrientes— y tiene costas en el océano Atlántico al sureste y sobre el Río de la Plata hacia el sur.
Abarca 176 mil km² siendo el segundo país más pequeño de Sudamérica en cuanto a territorio, detrás de Surinam. Posee un clima templado.
La población estimada para 2011 es de 3,25 millones de habitantes,1 4 representando la décima mayor población entre los países de América del Sur.
Es una república presidencialista subdividida en 19 departamentos y 89 alcaldías.
La capital y ciudad más grande del país es Montevideo, con 1,4 millones de habitantes,5 y cuya área metropolitana alcanza casi los dos millones,6 lo que corresponde al 58,8% del total nacional.
Es miembro de las Naciones Unidas, del Mercosur, de la OEA, de la UNASUR y del G77, entre otros.
El actual territorio uruguayo fue conocido en un principio como Banda Oriental —que también incluía parte del actual estado brasileño de Río Grande del Sur—.
Tal denominación proviene de su ubicación geográfica, pues se ubica al este —u oriente— del río Uruguay y al norte del Río de la Plata, siendo la tierra más oriental del Virreinato del Río de la Plata.
El 28 de agosto de 1828 se firmó la Convención Preliminar de Paz en la que se estableció la creación de un estado independiente, aunque sin denominación oficial. La primera denominación de la actual República Oriental del Uruguay fue «Estado Oriental del Uruguay.»
Dicha denominación fue dada al país por la primera Constitución promulgada el 28 de junio de 1830 y jurada por el pueblo el 18 de julio del mismo año.'''
d['priority'] = 1
d['launched'] = datetime.date(1972, 6, 21)
d['expires'] = datetime.date(2012, 6, 21)
d['type'] = "Geografía"
d['fav'] = 0
d.close()

filename = os.path.join('/tmp', 'notify_1')
d = shelve.open(filename)
d['id'] = 1
d['title'] = "América del Sur"
d['text'] = '''América del Sur, también llamada Sudamérica o Suramérica, es el subcontinente austral de América.
Está atravesada por la línea ecuatorial en su extremo norte, quedando así con la mayor parte de su territorio comprendida dentro del Hemisferio Sur.
Está situada entre el océano Atlántico y el océano Pacífico quienes delimitan los extremos Este y Oeste respectivamente, mientras que el Mar Caribe delimita por el norte y el Océano Antártico su extremo sur.
Ocupa una superficie de 17,8 millones de km², lo que representa un 42% del continente americano y un 12% de las tierras emergidas,9 y está habitada por el 6% de la población mundial.'''
d['priority'] = 2
d['launched'] = datetime.date(1973, 6, 21)
d['expires'] = datetime.date(2013, 6, 21)
d['type'] = "Geografía"
d['fav'] = 1
d.close()

filename = os.path.join('/tmp', 'notify_2')
d = shelve.open(filename)
d['id'] = 2
d['title'] = "Nueva Imagen Para tu xo"
d['text'] = '''Está disponible la nueva imagen para tu XO!
Para tenerla entrar al sitio www.ceibal.edu.uy'''
d['priority'] = 0
d['launched'] = datetime.date(1974, 6, 21)
d['expires'] = datetime.date(2013, 6, 21)
d['type'] = "Actualización"
d['fav'] = 1
d.close()

filename = os.path.join('/tmp', 'notify_3')
d = shelve.open(filename)
d['id'] = 3
d['title'] = "Actividades"
d['text'] = '''En setiembre se viene la Liga de Primavera de Cazaproblemas.
En breve podrás inscribirte y participar por grandes premios'''
d['priority'] = 3
d['launched'] = datetime.date(1975, 6, 21)
d['expires'] = datetime.date(2013, 6, 21)
d['type'] = "Actividades"
d['fav'] = 0
d.close()

store = Store(xmlpath='/tmp', db_filename="prueba.db")
mensaje = store.db.get_messages([])
print mensaje
