# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015
#    Andrea Cometa <a.cometa@apuliasoftware.it>
#    WEB (<http://www.apuliasoftware.it>).
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class SaleAnalysis(models.Model):
    """ Sale Analysis """
    _name = 'sale.analysis'
    _description = 'Sale analysis'

    name = fields.Char(string="Code", required=True)
    user_id = fields.Many2one('res.users', string="Analysis User",
        default=lambda self: self.env.user)
    date_begin = fields.Date(string="Start Date",
        readonly=True, default = fields.Datetime.now())
    date_end = fields.Date(string="End Date",
        readonly=True, default = fields.Datetime.now())
    bom_id = fields.Many2one('mrp.bom', string="Mrp bom")
    product_id = fields.Many2one('product.product', string="Product")
    uom = fields.Many2one('product.uom', string="UoM")
    qty = fields.Float(string="Quantity",
                       digits= dp.get_precision('Product Unit of Measure'))
    order_id = fields.Many2one('sale.order', string="Order")
    type = fields.Char()
    qty_available = fields.Float(
        string='Quantity On Hand',
        digits= dp.get_precision('Product Unit of Measure'))
    residual = fields.Float(
        string='Residual', digits= dp.get_precision('Product Unit of Measure'))
    analysis_type = fields.Char()
    order_qty = fields.Float(
        string='Order Quantity',
        digits= dp.get_precision('Product Unit of Measure'))