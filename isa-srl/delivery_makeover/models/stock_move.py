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


class stock_move(orm.Model):

    _inherit = 'stock.move'

    _columns = {
        'ddt_id': fields.related('picking_id',
                                 'ddt_id',
                                 relation='stock.picking.ddt',
                                 type='many2one',
                                 readonly=True,
                                 string='DDT'),
    }
    
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):

        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)

        if move.ddt_id and move.ddt_id.picking_back_ids and move.ddt_id.invoice_state != 'invoiced':
            t_list = []
            t_pick_id = move.picking_id.id
            t_pick_back_ids = move.picking_id.ddt_id.picking_back_ids
            for t_pick_back_id in t_pick_back_ids:
                t_list.append(t_pick_back_id.id)
            if t_pick_id in t_list:
                res['quantity'] = - res['quantity']

        return res
    