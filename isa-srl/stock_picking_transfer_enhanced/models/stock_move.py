# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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

from openerp import models, fields, api


class stock_move(models.Model):
    _inherit = 'stock.move'

    selected = fields.Boolean(string="Select", default=True)
    orig_quants = fields.Float(string="Initial Quantity")

    @api.model
    def create(self, vals):
        if not vals:
            return super(stock_move, self).create(vals)
        qty = vals.get('product_uom_qty', 0.0)
        vals.update({'orig_quants': qty,})
        return super(stock_move, self).create(vals)

    @api.one
    def do_select(self):

        if self.selected:
            self.selected = False
        else:
            self.selected = True
        return True
