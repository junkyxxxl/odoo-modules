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

from openerp.osv import fields, osv


class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
            'pick_partner_id': fields.related('picking_id', 'partner_id', type='many2one', relation='res.partner', string='Partner', store=True),
            'ordered_quants': fields.related('procurement_id', 'sale_line_id', 'product_uom_qty', type='float', string='Ordered Quant'),
            'reservation_product_ids': fields.one2many('stock.reservation.product', 'move_id', 'Scalature & Divisioni', copy=False, readonly=True),
            }
