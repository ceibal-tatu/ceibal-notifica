#!/usr/bin/python
# -*- coding: utf-8 -*-
# 2012-04-16
# Autor: Esteban Bordón - ebordon@plan.ceibal.edu.uy
#
# Guarda los mensajes obtenidos desde el servidor
# Actualmente se guardan en una base de datos sqlite3
# y los archivos vienen en shelve

import sqlite3
import os
import datetime
import shelve
from ceibal.notifier import env

# for future releases
#from xml.dom import minidom

init_db = """
CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY,
title VARCHAR(30) NOT NULL ON CONFLICT REPLACE DEFAULT '',
text TEXT NOT NULL ON CONFLICT REPLACE DEFAULT '',
priority INTEGER NOT NULL,
launched DATE NOT NULL ON CONFLICT REPLACE DEFAULT 00000000,
expires DATETIME,
type VARCHAR(15) NOT NULL ON CONFLICT REPLACE DEFAULT '',
fav INTEGER NOT NULL ON CONFLICT REPLACE DEFAULT 0 ); """

class Db:
    def __init__(self, db_filename=None):
        if db_filename:
            self._db_filename = db_filename
        else:
            self._db_filename = os.path.join(env.get_data_root(), "messages.db")
            #self._db_filename = os.path.join("/home/lordtias/git/ceibal-notifier", "messages.db")
        conn = self._connect()
        c = conn.cursor()
        c.executescript(init_db)
        self._close_connection(conn)

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _connect(self):
        conn = sqlite3.connect(self._db_filename, isolation_level=None)
        conn.text_factory = str
        return conn

    def _close_connection(self, conn):
        conn.close()

    def add_message(self, keys, values):
        """Agrega un mensaje a la base de datos"""
        con = self._connect()
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        try:
            c.execute('insert into notifications(%s,%s,%s,%s,%s,%s,%s,%s)  values (?,?,?,?,?,?,?,?)' % tuple(keys), values)
        except sqlite3.IntegrityError, e:
            print "Error al insertar datos: %s" % str(e)
        c.execute('END TRANSACTION')
        self._close_connection(con)

    def remove_message(self, id_msg):
        """Elimina el mensaje de la base de datos"""
        con = self._connect()
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        try:
            c.execute('delete from notifications where id=%i' % id_msg)
        except sqlite3.IntegrityError, e:
            print "Error al eliminar datos: %s" % str(e)
        c.execute('END TRANSACTION')
        self._close_connection(con)

    def get_categories(self, order='+',value="Tipo"):
        if order == '+':
            order = "ASC"
        else:
            order = "DESC"
        value = value.lower()
        mapped_value = "funcion"
        if value == "funcion":
            mapped_value = "type"
        elif value == "prioridad":
            mapped_value = "priority"
        elif value == "lanzamiento":
            mapped_value = "launched"
        elif value == u"vencimiento":
            mapped_value = "vencimiento"
        query = "select distinct %s from notifications order by %s %s " %(mapped_value, mapped_value, order)
        return map(lambda x:x[mapped_value],self.run_query(query))

    def set_fav(self, id_msg, fav=True):
        """Marca un mensaje como favorito.
        Si fav == False lo desmarca"""
        con = self._connect()
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        try:
            c.execute('update notifications set fav=%i where id=%i' % (int(fav), id_msg))
        except sqlite3.IntegrityError, e:
            print "Error al eliminar datos: %s" % str(e)
        c.execute('END TRANSACTION')
        self._close_connection(con)

    def is_fav(self, id_msg):
        fav = self.run_query("select fav from notifications where id=%i" % id_msg)
        return bool(int(fav[0]['fav']))

    def run_query(self, query):
        """
        Ejecuta una consulta cualquiera a la base de datos.
        Retorna el resultado de dicha consulta
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
        con = self._connect()
        con.row_factory = self.dict_factory
        filters = ''
        if args:
            filters = 'where '
            while args:
                clave, valor = args.popitem()
                filters += clave + ' ' + str(valor)
                filters += ' and ' if args else ''
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        c.execute('SELECT * FROM notifications %s order by vencimiento asc;' % filters)
        output = c.fetchall()
        c.execute('END TRANSACTION')
        self._close_connection(con)
        return output

    """
    def get_msg_by_priority(self, priority):
        con = self._connect()
        con.row_factory = self.dict_factory
        c = con.cursor()
        c.execute('BEGIN TRANSACTION')
        c.execute('select * from notifications where prority=%d' %priority)
        output = c.fetchall()
        c.execute('END TRANSACTION')
        self._close_connection(con)
        return output
    """

class Store:
    def __init__(self, xmlpath=None, db_filename=None):
        self.db = Db(db_filename)
        # Borro todas las notificaciones que ya expiraron
        # Para el futuro puede interesar tener un hisórico, habría que cambiar esto
        today = datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
        query = "delete from notifications where vencimiento < %s;" % today
        self.db.run_query(query)
        # Implementado para futuras versiones
        """
        if not xmlpath:
            xmlpath = os.path.join(env.get_data_root(),"mensajes.xml")
        fsock = open(xmlpath)
        self.xmldoc = minidom.parse(fsock)
        fsock.close()
        self.msg_list = self.xmldoc.getElementsByTagName("message")
        """
        # por el momento se implementa un parseo de los archivos shelve
        # de texto que se encuentren en /etc/notifier/data/tmp/
        # obtengo todos los archivos que comiencen con 'notify_'
        xmlpath = '/tmp'  # os.path.join(env.get_data_root(),'tmp')
        files = filter(lambda x: x.startswith("notify_"), os.listdir(xmlpath))
        self.msg_list = {}
        #msg_items = ['id', 'title', 'text', 'launched', 'expired', 'priority',]
        for file in files:
            abspath = os.path.join(xmlpath, file)
            try:
                f = shelve.open(abspath)
                self._save_message(f)
                f.close()
                os.remove(abspath)
            except:
                    pass
        #for msg in self.msg_list:
        #    self._save_message(msg)

    def _save_message(self, msg):
        """Procesa los mensajes que vienen en el diccionario msg"""
        print "procesando nodo %s" % msg["id"]
        keys = msg.keys()
        values = []
        for item in keys:
            values.append(str(msg[item]))
        self.db.add_message(keys, values)

    def _save_XML_message(self, msg):
        # For future releases
        #TODO: Poder leer links html en el campo text
        print "procesando nodo %s" % msg.getAttribute("id")
        refNode = msg.childNodes
        keys = ["id", "type", "priority"]
        values = []
        map(lambda x: values.append(msg.getAttribute(x)), keys)
        for node in refNode:
            if node.nodeType == 1:
                #print "clave: %s, valor: %s" % (node.localName, node.firstChild.data)
                keys.append(node.localName)
                values.append(node.firstChild.wholeText.strip())
        self.db.add_message(keys, values)

if __name__ == "__main__":
    #db_filename = '../data/messages.db'
    #xmlpath = "../data/mensajes.xml"
    notification = Store()
