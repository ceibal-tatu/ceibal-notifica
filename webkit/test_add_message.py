#! /usr/bin/python
from ceibal.notifier.data_base import Db
from ceibal.notifier.constantes import DIC_KEYS
import time
base = Db()

html =[ 
{'id':'2' , 'txt': "<html><header><body><h1>TITULO 1</h1> <h2>texto del mensaje 1...</h2></body></header></html>"},
{'id':'10', 'txt': "<html><header><body><h1 style='font-size:1.5em'>TITULO 2</h1> <h2 style='font-size:1.2em'>texto del mensaje 2...</h2></body></header></html>"},
{'id':'9',  'txt': "<html><header><body>texto del mensaje 3...<a href='http://www.ceibal.edu.uy'>link</a></body></header></html>"},
{'id':'3',  'txt': "<html><header><body>texto del mensaje 4...</body></header></html>"},
{'id':'4',  'txt': "<html><header><body>texto del mensaje 5...</body></header></html>"},
{'id':'7',  'txt': "<html><header><body>texto del mensaje 6...<a href='http://www.ceibal.edu.uy'>link</a></body></header></html>"},
{'id':'5',  'txt': "<html><header><body>texto del mensaje 7...</body></header></html>"},
{'id':'1',  'txt': "<html><header><body>texto del mensaje 8...</body></header></html>"}
]

"""                         ID   VENCIMIENTO  FUNCION     ACCION                       TITULO          TEXTO               TEXTO_HTML  IMAGEN """
idx=1
for h in html:
    if idx >= 2 and idx <= 4:
        time.sleep(2)
    base.add_message(DIC_KEYS, [h['id'], "2015-12-31","general",  "http://www.ceibal.edu.uy" ,"Prueba HTML ", "Probando visor html "+h['id'], h['txt']  ,"/home/gustavo/devel/notification/ceibal/notificador-ceibal-notifier/etc/notifier/images/planceibal.png"])
    idx = idx + 1    
