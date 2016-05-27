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

from openerp import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    picking_type_code = fields.Selection(string='Picking Type Code', related='picking_id.picking_type_id.code')

    ddt_id = fields.Many2one('stock.ddt', string='DDT', related='picking_id.ddt_id')

    supplier_ddt_number = fields.Char(string='DDT Fornitore', related='picking_id.supplier_ddt_number')

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(move, partner, inv_type)
        if res and 'quantity' in res:
            ctx = dict(self._context or {})
            if ctx and 'picking_return' in ctx and ctx['picking_return'] and move.picking_id and move.picking_id.id in ctx['picking_return']:
                res['quantity'] = - res['quantity']
        return res
