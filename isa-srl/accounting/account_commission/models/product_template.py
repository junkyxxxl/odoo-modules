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

class product_template_commission(models.Model):

    _inherit = 'product.template'

    def _get_default_no_commission(self):
        if self.categ_id:
            return self.categ_id.no_commission
        return False

    product_commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'), )
    no_commission = fields.Boolean(string="No Commission", help="If flagged, won't be computed commissions on this product", default=_get_default_no_commission, ) 
    is_commission = fields.Boolean(string="Commission", help="If flagged, this product will be considered as a commission", default=False, )
    salesagent_cant_sell = fields.Boolean(string="Salesagent can't sell", help="If flagged, this product won't be available for selling by salesagents", default=False, )

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id:
            self.no_commission = self.categ_id.no_commission

    @api.onchange('is_commission')
    def onchange_iscommission(self):
        if self.is_commission:
            self.no_commission = True
            self.type = 'service'

    @api.onchange('no_commission')
    def onchange_nocommission(self):
        if self.no_commission:
            self.product_commission_perc = 0.0
        if not self.no_commission:
            self.is_commission = False

    @api.one
    @api.constrains('product_commission_perc')
    def _check_commission(self):
        if self.product_commission_perc < 0.0 or self.product_commission_perc > 100.0:
            raise ValidationError(_("Commission should be between 0 and 100!"))    
        
class product_category_commission(models.Model):

    _inherit = 'product.category'

    category_commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'), )
    no_commission = fields.Boolean(string="No Commission", help="If flagged, won't be computed commissions on all the products in this category", default=False, ) 

    @api.onchange('no_commission')
    def onchange_user_id(self):
        if self.no_commission:
            self.category_commission_perc = 0.0

    @api.one
    @api.constrains('category_commission_perc')
    def _check_commission(self):
        if self.category_commission_perc < 0.0 or self.category_commission_perc > 100.0:
            raise ValidationError(_("Commission should be between 0 and 100!"))