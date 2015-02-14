#! /usr/bin/python

import sys
sys.path.append("/home/gustavo/devel/notification/ceibal/notificador-ceibal-notifier")

from ceibal.notifier.data_base import Db
from ceibal.notifier.constantes import DIC_KEYS

base = Db()

html_txt1 = "<html><header><body>texto del mensaje 1...</body></header></html>"
html_txt2 = "<html><header><body>texto del mensaje 2...</body></header></html>"
html_txt3 = "<html><header><body>texto del mensaje 3...</body></header></html>"
html_txt4 = "<html><header><body>texto del mensaje 4...</body></header></html>"
html_txt5 = "<html><header><body>texto del mensaje 5...</body></header></html>"

"""                         ID   VENCIMIENTO  FUNCION     ACCION                       TITULO          TEXTO               TEXTO_HTML  IMAGEN """

base.add_message(DIC_KEYS, ["1", "2015-12-31","general",  "http://www.ceibal.edu.uy" ,"Prueba HTML ", "Probando visor html 1", html_txt1  ,"/home/gustavo/devel/notification/ceibal/notificador-ceibal-notifier/etc/notifier/images/planceibal.png"])
base.add_message(DIC_KEYS, ["2", "2015-12-31","general",  "http://www.ceibal.edu.uy" ,"Prueba HTML ", "Probando visor html 2", html_txt2  ,"/home/gustavo/devel/notification/ceibal/notificador-ceibal-notifier/etc/notifier/images/planceibal.png"])
base.add_message(DIC_KEYS, ["3", "2015-12-31","general",  "http://www.ceibal.edu.uy" ,"Prueba HTML 3", "Probando visor html 3", html_txt3  ,"/home/gustavo/devel/notification/ceibal/notificador-ceibal-notifier/etc/notifier/images/planceibal.png"])
base.add_message(DIC_KEYS, ["4", "2015-12-31","general",  "http://www.ceibal.edu.uy" ,"Prueba HTML 4", "Probando visor html 4", html_txt4  ,"/home/gustavo/devel/notification/ceibal/notificador-ceibal-notifier/etc/notifier/images/planceibal.png"])
base.add_message(DIC_KEYS, ["5", "2015-12-31","general",  "http://www.ceibal.edu.uy" ,"Prueba HTML 5", "Probando visor html 5", html_txt5  ,"/home/gustavo/devel/notification/ceibal/notificador-ceibal-notifier/etc/notifier/images/planceibal.png"])

