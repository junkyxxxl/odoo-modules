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

class res_company_family_commission(models.Model):

    _inherit = 'res.company'

    def _function_priorities(self):
        res = super(res_company_family_commission,self)._function_priorities()
        res.append(('family','Family'))
        return res
        
    commission_priority5 = fields.Selection(string="Priority #5", selection='_function_priorities', default='family', )        

    @api.model
    def get_commission_perc(self, type, product, partner_id, salesagent_id, discount=0.0):
        
        if type == 'product':
            res = 0.0
            if product:
                res = product.product_commission_perc
            return res
        
        if type == 'category':
            res = 0.0
            if product and product.categ_id:
                res = product.categ_id.category_commission_perc
            return res
        
        if type == 'customer':
            res = 0.0
            if partner_id:
                res = self.env['res.partner'].browse(partner_id).customer_commission_perc
            return res
        
        if type == 'salesagent':
            res = 0.0
            if salesagent_id:
                res = salesagent_id.salesagent_commission_perc
            else:
                res = 0.0
            return res
        
        if type == 'family':
            res = 0.0
            if product and product.family:
                if 'pricelist_item_id' in self._context and self._context['pricelist_item_id'] and self.env['product.pricelist.item'].browse(self._context['pricelist_item_id']).is_net_price:
                    if product.family.net_price_commission_perc:
                        res = product.family.net_price_commission_perc
                    else:
                        res = -5.0
                else:   
                    res = product.family.get_commission_perc(partner_id,discount=discount)
            else:
                res = 0.0
            return res
    
    @api.one
    @api.constrains('commission_priority1','commission_priority2','commission_priority3','commission_priority4','commission_priority4')
    def _check_priorities(self):
        if self.commission_priority1:
            if self.commission_priority1 == self.commission_priority2 or self.commission_priority1 == self.commission_priority3 or self.commission_priority1 == self.commission_priority4 or self.commission_priority1 == self.commission_priority5:         
                raise ValidationError(_("It's not possible to have duplicate values of priority!"))
        if self.commission_priority2:
            if self.commission_priority2 == self.commission_priority3 or self.commission_priority2 == self.commission_priority4 or self.commission_priority2 == self.commission_priority5:         
                raise ValidationError(_("It's not possible to have duplicate values of priority!"))
        if self.commission_priority3:
            if self.commission_priority3 == self.commission_priority4 or self.commission_priority3 == self.commission_priority5:         
                raise ValidationError(_("It's not possible to have duplicate values of priority!"))    
        if self.commission_priority4:
            if self.commission_priority4 == self.commission_priority5:         
                raise ValidationError(_("It's not possible to have duplicate values of priority!"))               