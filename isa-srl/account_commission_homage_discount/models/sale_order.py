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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError

class sale_order_line_commission_homage(models.Model):

    _inherit = 'sale.order.line'
    
    commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'),)
    commission_amount = fields.Float(compute="_compute_commission_amount", string="Commission", digits_compute= dp.get_precision('Account'),)    
    
    @api.one
    @api.depends('price_subtotal', 'commission_perc')    
    def _compute_commission_amount(self):
        super(sale_order_line_commission_homage,self)._compute_commission_amount()
        if self.free in ['gift','base_gift']:
            self.commission_amount = 0.0            
        if self.commission_amount and self.order_id.global_discount_percentual:
            self.commission_amount -= (self.commission_amount * self.order.global_discount_percentual)