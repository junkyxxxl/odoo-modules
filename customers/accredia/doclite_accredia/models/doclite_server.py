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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class doclite_server_accredia(orm.Model):

    _inherit = 'doclite.server'
    _description = 'Multiple Server for Accredia'

    _columns = {'server_location': fields.selection([('R', 'Roma'),
                                                     ('M', 'Milano'), ],
                                                    'Location'),
                }

    _defaults = {'server_location': 'M'
                 }

    def check_get_server(self, cr, uid, ids, context):

        user_id = self.pool.get('res.users').browse(cr, uid, uid)
        t_user_loc = user_id.server_location
        t_loc = None
        if not(t_user_loc in ['M', 'T', 'R']):
            raise orm.except_orm(_('Errore!'),
                                 _('User Location Server Not Defined'))

        if user_id.server_location in ['M', 'T']:
            t_loc = 'M'
        if user_id.server_location in ['R']:
            t_loc = 'R'

        server_ids = self.search(cr, uid, [('server_location', '=', t_loc)])
        if not server_ids:
            raise orm.except_orm(_('Errore!'),
                                 _('Server Doclite Mancante'))
        server_id = self.browse(cr, uid, server_ids[0])
        return server_id

    def get_final_url(self, cr, uid, ids, context):

        server_id = self.check_get_server(cr, uid, ids, context)

        t_ip = server_id.ip_address
        t_port = server_id.port
        t_path = server_id.base_path
        final_url = 'http://' + str(t_ip) + ':' + str(t_port) + str(t_path) + '?user_id=' + str(uid) 

        return final_url

    def get_ip_address(self, cr, uid, ids, context):

        server_id = self.check_get_server(cr, uid, ids, context)
        t_ip = server_id.ip_address
        return t_ip

    def get_port(self, cr, uid, ids, context):

        server_id = self.check_get_server(cr, uid, ids, context)
        t_port = server_id.port
        return t_port

    def get_base_path(self, cr, uid, ids, context):

        server_id = self.check_get_server(cr, uid, ids, context)
        t_base_path = server_id.base_path
        return t_base_path
