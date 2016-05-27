# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _


class doclite_server(orm.Model):
    _name = 'doclite.server'

    _columns = {
        'ip_address': fields.char('IP Address',
                            size=15,
                            required=True),
        'port': fields.char('Port',
                            size=6),
        'base_path': fields.char('URL Base Path',
                            size=64,
                            required=True),
    }

    _defaults = {
        'ip_address': '127.0.0.1',
        'port': '80',
        'base_path': '/doclite/',
        }

    def check_server(self, cr, uid, ids, context):
        server_ids = self.search(cr, uid, [])

        if not server_ids:
            raise orm.except_orm(_('Errore!'),
                                    'Server Doclite Mancante')
        return True

    def get_final_url(self, cr, uid, ids, context):
        
        self.check_server(cr, uid, ids, context)
            
        server_ids = self.search(cr, uid, [])
        server_id = self.browse(cr, uid, server_ids[0])
        t_ip = server_id.ip_address
        t_port = server_id.port
        t_path = server_id.base_path
        final_url = 'http://' + str(t_ip) + ':' + str(t_port) + str(t_path) + '?user_id=' + str(uid) 
            
        return final_url

    def get_ip_address(self, cr, uid, ids, context):
        
        self.check_server(cr, uid, ids, context)
        server_ids = self.search(cr, uid, [])
        server_id = self.browse(cr, uid, server_ids[0])
        t_ip = server_id.ip_address
        return t_ip

    def get_port(self, cr, uid, ids, context):
        
        self.check_server(cr, uid, ids, context)
        server_ids = self.search(cr, uid, [])
        server_id = self.browse(cr, uid, server_ids[0])
        t_port = server_id.port
        return t_port

    def get_base_path(self, cr, uid, ids, context):
        
        self.check_server(cr, uid, ids, context)
        server_ids = self.search(cr, uid, [])
        server_id = self.browse(cr, uid, server_ids[0])
        t_base_path = server_id.base_path
        return t_base_path

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for ap in self.browse(cr, uid, ids):
            descr = ("%s:%s") % (ap.ip_address, ap.port or '')
            res.append((ap.id, descr))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                                                context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}

        req_ids = self.search(cr, uid, args + 
                              [('ip_address', operator, name)],
                              limit=limit,
                              context=context)
        return self.name_get(cr, uid, req_ids, context=context)
