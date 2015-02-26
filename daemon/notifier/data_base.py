#! /usr/bin/python
# -*- coding:utf-8 -*-
# data_base.py V2.0
# Author: Matias Basso <mbasso@plan.ceibal.edu.uy> 
#------------------------------------------------------------------------------------
# Guarda los mensajes obtenidos desde un Web Service.
# Actualmente se guardan en una base de datos sqlite3 y los archivos vienen en json.
#------------------------------------------------------------------------------------

import sqlite3
import os
import datetime
from ceibal.notifier import env
from ceibal.notifier.constantes import DB_FILE,INIT_DB

class Db:
    def __init__(self, db_filename=None):
        '''
        @param db_filename: Nombre/direccion del archivo DB.
        @summary: Constructor de la clase.
        '''
        if db_filename:
            self._db_filename = db_filename
        else:
            self._db_filename = os.path.join(env.get_data_root(), DB_FILE)
        conn = self._connect()
        c = conn.cursor()
        c.executescript(INIT_DB)
        self._close_connection(conn)
    
    def dict_factory(self, cursor, row):
        '''
        @param cursor: Cursor de la conexion.
        @param row: Fila de la consulta.
        @summary: Da un formato a una Fila.
        @return: Fila formateada.
        '''
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def _connect(self):
        '''
        @summary: Abre una conexion a la DB.
        @return: Retorna la conexion.
        '''
        conn = sqlite3.connect(self._db_filename, isolation_level=None)
        conn.text_factory = str
        return conn
    
    def _close_connection(self, conn):
        '''
        @param conn: Conexion a DB que se va a cerrar.
        @summary: Se cierra la conexion.
        '''
        conn.close()
    
    def clean_db(self):
        """
        @summary: Borro todas las notificaciones que ya expiraron. El historico queda en la bandeja Web.
        """
        today = datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
        con = self._connect()
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        try:
            c.execute('delete from notifications where vencimiento < date("%s");' % today)
        except sqlite3.IntegrityError, e:
            print str(e)
        c.execute('END TRANSACTION')
        self._close_connection(con)
    
    def add_message(self, keys, values):
        """
        @param key: Lista de las columnas.
        @param values: Valores de las columnas.
        @summary: Agrega un mensaje a la base de datos.
        """
        values = map(lambda x: x.encode('utf-8'), values)
        con = self._connect()
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        try:
            c.execute('insert into notifications ({0[0]},{0[1]},{0[2]},{0[3]},{0[4]},{0[5]},{0[6]},{0[7]}) values ("{1[0]}",date("{1[1]}"),"{1[2]}","{1[3]}","{1[4]}","{1[5]}","{1[6]}","{1[7]}")'.format(keys,values))
        except sqlite3.IntegrityError, e:
            try:
                c.execute('update notifications SET {0[1]}=date("{1[1]}"), {0[2]}="{1[2]}", {0[3]}="{1[3]}", {0[4]}="{1[4]}", {0[5]}="{1[5]}", {0[7]}="{1[7]}" WHERE id="{1[6]}";'.format(keys,values))
            except Exception, e:
                print str(e)    
        c.execute('END TRANSACTION')
        self._close_connection(con)
    
    def run_query(self, query):
        """
        @param query: Consulta a ejecutar.
        @summary: Ejecuta una consulta cualquiera a la base de datos.
        @return: Retorna el resultado de dicha consulta.
        """
        con = self._connect()
        con.row_factory = self.dict_factory
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        c.execute(query)
        output = c.fetchall()
        c.execute('END TRANSACTION')
        self._close_connection(con)
        return output
    
    def get_messages(self, args):
        """
        @param args: Argumentos para filtrar la consulta.
        @summary: Obtiene todas las Notificacones.
        @return: Retorna las Notificaciones que correspondan al filtro de args.
        """
        con = self._connect()
        con.row_factory = self.dict_factory
        filters = ''
        if args:
            filters = 'where '
            while args:
                clave, valor = args.popitem()
                filters += clave + '=' + str(valor)
                filters += ' and ' if args else ''
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        c.execute('SELECT * FROM notifications %s order by vencimiento asc;' % filters)
        output = c.fetchall()
        c.execute('END TRANSACTION')
        self._close_connection(con)
        return output

if __name__ == "__main__":
    import sys
    from ceibal.notifier.constantes import DIC_KEYS
    base = Db()
    if len(sys.argv) > 6:
        base.add_message(DIC_KEYS, [sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],"/etc/notifier/images/planceibal.png"])
    else:
        print "Error!"
        print "El orden de los parametros: ID VENCIMIENTO FUNCION ACCION TITULO TEXTO TEXTO_HTML"