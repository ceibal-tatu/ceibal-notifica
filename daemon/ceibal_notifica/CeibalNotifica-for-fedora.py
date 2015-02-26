#!/usr/bin/python
# -*- coding: utf-8 -*-

#   Plan Ceibal - Uruguay
#   Flavio Danesse - fdanesse@activitycentral.com

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import shelve
import os
import gtk
import sys
import gobject

# Importamos la clase W_S_Conexion para conectarons al Web Service.
from ceibal.notifier.web_service_conexion import W_S_Conexion

# Importamos las Constantes.
from ceibal.notifier.constantes import WEB_SERVICE_URL

#import webkit

'''
try:
    from ceibal.notifier.store import *
except:
    from store import *'''

from store import *

BASE = os.path.dirname(__file__)
pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(BASE, "Iconos", "ceibal-gris.png"), 32, 32)
pixbuf2 = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(BASE, "Iconos", "ceibal.png"), 32, 32)


class CeibalNotifica(gtk.Window):
    def __init__(self):
        super(CeibalNotifica, self).__init__()
        self.maximize()
        self.set_title("Ceibal Notifica")
        self.set_icon_from_file(os.path.join(BASE, "Iconos", "ceibal.png"))
        self.set_resizable(True)
        self.set_size_request(1100, 480)
        self.set_border_width(2)
        self.set_position(gtk.WIN_POS_CENTER)
        self.text_buffer = None
        self.text_view = None
        self.store = None
        self.listore_model = None
        self.modelsort = None
        self.notify_store = None
        self.info_toolbar = None
        self.control_toolbar = None
        self.filter = None
        self.set_layout()
        self.show_all()
        self.connect("delete_event", self.delete_event)
        self.notify_store.connect("show_notify", self.show_notify)
        self.notify_store.connect("delete_notify", self.delete_notify)
        self.notify_store.connect("marcar_notify", self.marcar_notify)
        self.control_toolbar.connect("get_filter", self.get_filter)
        self.control_toolbar.connect("make_filter", self.make_filter)
        self.control_toolbar.connect("show_filter", self.show_filter)
        self.load_notify()
        self.notify_store.columns_autosize()

    def set_layout(self):
        self.listore_model = ListoreModel()
        self.modelsort = gtk.TreeModelSort(self.listore_model)
        self.notify_store = Notify_Store(self.modelsort)
        self.text_buffer = gtk.TextBuffer()
        self.text_view = gtk.TextView(buffer=self.text_buffer)
        self.text_view.set_editable(False)
        self.text_view.set_wrap_mode(gtk.WRAP_WORD)
        self.text_view.set_justification(gtk.JUSTIFY_FILL)
        self.text_view.set_pixels_above_lines(5)
        self.text_view.set_pixels_below_lines(15)
        self.text_view.set_pixels_inside_wrap(5)
        self.text_view.set_left_margin(10)
        self.text_view.set_right_margin(10)
        #self.view = webkit.WebView()

        #hpanel = gtk.HPaned()
        #hpanel.set_position(350)
        hboxGeneral = gtk.HBox(homogeneous=False)


        '''
        try:
            self.store = Store(db_filename="prueba.db")
        except:
            self.store = Store()'''
        self.store = Store()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.notify_store)
        scroll.set_size_request(400, -1)

        #hpanel.pack1(scroll, resize = True, shrink = False)
        hboxGeneral.pack_start(scroll, False, False, 0)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #scroll.add_with_viewport(self.view)
        scroll.add_with_viewport(self.text_view)

        #hpanel.pack2(scroll, resize = True, shrink = False)
        hboxGeneral.pack_start(scroll, True, True, 0)

        vbox = gtk.VBox()
        self.info_toolbar = ToolbarInfo()
        self.control_toolbar = ToolbarControl()
        vbox.pack_start(self.control_toolbar, False, False, 0)


        #vbox.pack_start(hpanel, True, True, 0)
        vbox.pack_start(hboxGeneral, True, True, 0)


        vbox.pack_start(self.info_toolbar, False, False, 0)


        #hpanel.show_all()
        hboxGeneral.show_all()
        

        self.add(vbox)

    def get_filter(self, widget, value):
        filtro_nivel2 = self.store.db.get_categories(value=value)
        widget.set_filter(filtro_nivel2)

    def make_filter(self, widget, value):
        self.filter = value
        self.load_notify()
        widget.make_filter(self.filter)

    def show_notify(self, widget, text, info, url):
        self.text_buffer.set_text(text)
#        self.view.load_html_string(str(text), '')
        self.info_toolbar.set_text(info)

    def delete_notify(self, widget, path):
        iter = widget.get_model().get_iter(path)
        id_registro = int(widget.get_model().get_value(iter, 0))
        self.store.db.remove_message(id_registro)
        iter = self.listore_model.get_iter(path)
        self.listore_model.remove(iter)
        self.update_view()

    def show_filter(self, widget):
        if self.filter[0] == 'Ninguno' and self.filter[1] == 'Ninguno': return
        valor = 0
        if self.filter[0] == 'Tipo': valor = 2
        if self.filter[0] == 'Vencimiento': valor = 1
        iter = self.listore_model.get_iter_first()
        while iter:
            val = self.listore_model.get_value(iter, valor)
            path = self.listore_model.get_path(iter)
            iter = self.listore_model.iter_next(self.listore_model.get_iter(path))
            if val != self.filter[1]:
                self.listore_model.remove(self.listore_model.get_iter(path))

    def marcar_notify(self, widget, path):
        iter = widget.get_model().get_iter(path)
        id_registro = int(widget.get_model().get_value(iter, 1))
        marca = not self.store.db.is_fav(id_registro)
        self.store.db.set_fav(id_registro, fav=marca)
        iter = self.listore_model.get_iter(path)
        fav = self.store.db.is_fav(id_registro)
        self.listore_model.set_value(iter, 8, fav)
        self.update_view()

    def update_view(self):
        path = self.notify_store.get_path_selected()
        if path == None: path = 0
        self.notify_store.treeselection.select_path(path)
        try:
            iter = self.listore_model.get_iter(path)
            if self.listore_model.get_value(iter, 8):
                self.listore_model.set_value(iter, 0, pixbuf2)
            else:
                self.listore_model.set_value(iter, 0, pixbuf1)
        except:
            self.text_buffer.set_text('')
            #self.view.load_html_string('', '')
            self.info_toolbar.set_text('')

    def load_notify(self):
        notificaciones = self.store.db.get_messages([])
        self.listore_model.clear()
        for notif in notificaciones:
            self.add_notify(notif)

    def add_notify(self, notify):
        mark = pixbuf1
        notify = [notify['id'], notify['vencimiento'], notify['funcion'], notify['accion'],
        notify['titulo'], notify['texto'], notify['html']]
        io = self.modelsort.get_model().append(notify)
        sel = self.notify_store.get_selection()
        il = self.modelsort.convert_child_iter_to_iter(None, io)
        sel.select_iter(il)

    def delete_event(self, widget, event):
        self.salir()
        return False

    def salir(self, widget=None):
        sys.exit(0)


class ListoreModel(gtk.ListStore):
    def __init__(self):
        gtk.ListStore.__init__(self,gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_STRING)


class Notify_Store(gtk.TreeView):
    __gsignals__ = {"show_notify": (gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING,gobject.TYPE_STRING)),
    "delete_notify": (gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "marcar_notify": (gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self, model):
        gtk.TreeView.__init__(self, model)
        self.set_property("rules-hint", True)
        self.add_events(gtk.gdk.BUTTON2_MASK)
        self.connect("button-press-event", self.handle_click, self.get_model())
        self.set_headers_clickable(True)
        self.set_columns()
        self.show_all()
        self.treeselection = self.get_selection()
        self.treeselection.set_mode(gtk.SELECTION_SINGLE)
        self.treeselection.set_select_function(self.func_selections,
            self.get_model(), True)

    def set_columns(self):
        self.append_column(self.make_column_mark('', 0, True))
        self.append_column(self.make_column('Vencimiento', 1, True))
        self.append_column(self.make_column('Funcion', 2, False))
        self.append_column(self.make_column('Accion', 3, False))
        self.append_column(self.make_column('Titulo', 4, True))
        self.append_column(self.make_column('Texto', 5, False))
        self.append_column(self.make_column('Html', 6, False))
        self.append_column(self.make_column('Imagen', 7, False))

    def make_column_mark(self, text, index, visible):
        render = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn(text, render, pixbuf = index)
        column.set_property("visible", visible)
        return column

    def make_column(self, text, index, visible):
        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn(text, render, text=index)
        column.set_sort_column_id(index)
        column.set_property('visible', visible)
        return column

    def func_selections(self, selection, model, path, is_selected, user_data):
        iter = self.get_model().get_iter(path)
        texto = self.get_model().get_value(iter, 5)
        nid = self.get_model().get_value(iter, 0)
        ntype = self.get_model().get_value(iter, 2)
        nurl = self.get_model().get_value(iter, 3)
        info = "ID: %s " % (nid)
        if ntype == 'url':
            self.emit("show_notify", texto, info, nurl)
        else:
            nurl = None
            self.emit("show_notify", texto, info, nurl)
        return True

    def handle_click(self, widget, event, path):
        boton = event.button
        pos = (int(event.x), int(event.y))
        tiempo = event.time
        try:
            path, col, x, y = widget.get_path_at_pos(pos[0], pos[1])
            if boton == 1:
                return
            elif boton == 3:
                self.get_menu(boton, pos, tiempo, path)
                return
            elif boton == 2:
                return
        except:
            pass

    def get_menu(self, boton, pos, tiempo, path):
        menu = gtk.Menu()
        eliminar = gtk.MenuItem("Eliminar Notificación.")
        menu.append(eliminar)
        eliminar.connect_object("activate", self.emit_delete_notify, path)
        iter = self.get_model().get_iter(path)
        #fav = self.get_model().get_value(iter, 8)
        #marcar = gtk.MenuItem("Marcar Como Favorito.")
        #if fav: marcar = gtk.MenuItem("Desmarcar Como Favorito.")
        #menu.append(marcar)
        #marcar.connect_object("activate", self.emit_marcar_notify, path)
        menu.show_all()
        gtk.Menu.popup(menu, None, None, None, boton, tiempo)

    def get_path_selected(self):
        (model, iter) = self.get_selection().get_selected()
        path = None
        if iter:
            treemodelrow = model[iter]
            path = treemodelrow.path
        return path

    def emit_delete_notify(self, path):
        self.emit("delete_notify", path)

    def emit_marcar_notify(self, path):
        self.emit("marcar_notify", path)


class ToolbarInfo(gtk.Toolbar):

    def __init__(self):
        gtk.Toolbar.__init__(self)
        #self.modify_bg(gtk.STATE_NORMAL,
        #    gtk.gdk.Color(0, 20000, 0, 1))
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)
        item = gtk.ToolItem()
        self.info_label = gtk.Label("")
        #self.info_label.modify_fg(gtk.STATE_NORMAL,
        #    gtk.gdk.Color(65535, 65535, 65535,1))
        self.info_label.show()
        item.add(self.info_label)
        self.insert(item, -1)
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)

    def set_text(self, text=""):
        self.info_label.set_text(text)


class ToolbarControl(gtk.Toolbar):
    __gsignals__ = {"get_filter": (gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
    "make_filter": (gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "show_filter": (gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, [])}

    def __init__(self):
        gtk.Toolbar.__init__(self)
        #self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 1))
        self.filter_combo1 = None
        self.filter_combo2 = None
        self.btn_notify_demand = None
        self.set_layout()
        self.show_all()

        self.filter_combo1.connect("change_selection", self.emit_get_filter)
        self.filter_combo2.connect("change_selection", self.emit_make_filter)
        self.btn_notify_demand.connect("clicked", self.emit_get_notify_on_demand)

    def set_layout(self):
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(10, -1)
        separator.set_expand(False)
        self.insert(separator, -1)

        item = gtk.ToolItem()
        label = gtk.Label("Filtrar por:")
        #label.modify_fg(gtk.STATE_NORMAL,
        #   gtk.gdk.Color(65535, 65535, 65535,1))
        label.show()
        item.add(label)
        self.insert(item, -1)

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(10, -1)
        separator.set_expand(False)
        self.insert(separator, -1)

        item = gtk.ToolItem()
        self.filter_combo1 = Combo()
        self.filter_combo1.set_items(["Tipo", "Vencimiento"])
        self.filter_combo1.show()
        item.add(self.filter_combo1)
        self.insert(item, -1)

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(10, -1)
        separator.set_expand(False)
        self.insert(separator, -1)

        item = gtk.ToolItem()
        label = gtk.Label("Seleccionar:")
        #label.modify_fg(gtk.STATE_NORMAL,
        #   gtk.gdk.Color(65535, 65535, 65535,1))
        label.show()
        item.add(label)
        self.insert(item, -1)

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(10, -1)
        separator.set_expand(False)
        self.insert(separator, -1)

        item = gtk.ToolItem()
        self.filter_combo2 = Combo()
        self.filter_combo2.set_items([])
        self.filter_combo2.get_model().clear()
        self.filter_combo2.show()
        item.add(self.filter_combo2)
        self.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(200, -1)
        separator.set_expand(False)
        self.insert(separator, -1)
        
        item = gtk.ToolItem()
        self.btn_notify_demand = gtk.Button("Obtener Notificaciones")
        self.btn_notify_demand.show()
        item.add(self.btn_notify_demand)
        self.insert(item, -1)

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(20, -1)
        separator.set_expand(False)
        self.insert(separator, -1)

    def emit_get_notify_on_demand(self, widget):
        # Realizamos la coneccion con el Web Service.
        web=W_S_Conexion(WEB_SERVICE_URL)

        # Verificamos los parametros de entrada. Si es on demand obtenemos las notificaciones sin restricción. 
        if len(sys.argv) > 1 and sys.argv[1] == '--on-demand':
            web.Obtener_notificaciones(True)
        else:
            web.Obtener_notificaciones(False)

    def emit_get_filter(self, widget, value):
        self.emit("get_filter", value)

    def emit_make_filter(self, widget, value):
        val1 = self.filter_combo1.get_value_select()
        self.emit("make_filter", [val1,value])

    def set_filter(self, lista):
        self.filter_combo2.set_items(lista)

    def make_filter(self, filter):
        if filter[0] == 'Ninguno':
            self.filter_combo2.get_model().clear()
        self.emit('show_filter')


class Combo(gtk.ComboBox):
    __gsignals__ = {"change_selection": (gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}

    def __init__(self):
        gtk.ComboBox.__init__(self, gtk.ListStore(str))
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.show_all()
        self.connect("changed", self.emit_selection)

    def set_items(self, items):
        self.get_model().clear()
        self.append_text("Ninguno")
        for item in items:
            self.append_text(str(item))
        self.set_active(0)

    def emit_selection(self, widget):
        indice = widget.get_active()
        if indice < 0: return
        iter = widget.get_model().get_iter(indice)
        value = widget.get_model().get_value(iter, 0)
        self.emit("change_selection", value)

    def get_value_select(self):
        indice = self.get_active()
        if indice < 0: return None
        iter = self.get_model().get_iter(indice)
        value = self.get_model().get_value(iter, 0)
        return value


if __name__ == "__main__":
    CeibalNotifica()
    gtk.main()
