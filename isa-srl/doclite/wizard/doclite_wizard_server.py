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


class doclite_wizard_server(orm.TransientModel):
    _name = 'doclite.wizard.server'
    _inherit = 'res.config'

    def execute(self, cr, uid, ids, context=None):
        
        obj_wizard = self.browse(cr, uid, ids[0], context=context)
        t_ip_address = obj_wizard.ip_address
        t_port = obj_wizard.port
        t_base_path = obj_wizard.base_path
        self.pool.get('doclite.server').create(cr, uid,
                {'ip_address': t_ip_address,
                 'port': t_port,
                 'base_path': t_base_path,
                 })

        return {}

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
