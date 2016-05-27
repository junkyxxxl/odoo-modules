# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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
from datetime import datetime


class stock_picking_exporter_statements(orm.Model):
    _inherit = "stock.picking"

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):      
 
        inv_vals = super(stock_picking_exporter_statements, self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)
        sale = move.picking_id.sale_id
        if sale:
            ext_obj = self.pool.get('account.exporter.statements')
            exp_ids = ext_obj.search(cr, uid, [('partner_id', '=', sale.partner_id.id), ('letter_status', '=', 'A')])
            if exp_ids:
                inv_vals.update({'exporter_id': exp_ids[0], 'comment': 'Lettera d\'intento n. ' + ext_obj.browse(cr, uid, exp_ids[0]).letter_number + ' - Del ' + datetime.strptime(ext_obj.browse(cr, uid, exp_ids[0]).letter_date,"%Y-%m-%d").strftime('%d/%m/%Y'),})                
        return inv_vals
