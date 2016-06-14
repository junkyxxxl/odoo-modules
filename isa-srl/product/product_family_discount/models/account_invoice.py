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

class account_invoice_line_family_discount(models.Model):

    _inherit = 'account.invoice.line'
    
    @api.onchange('discount1','discount2','discount3','max_discount')
    def onchange_discount(self):
        a = (100-self.discount1)/100
        b = (100-self.discount2)/100
        c = (100-self.discount3)/100
        tot = 100 - (100*a*b*c)
        partial_tot = 100 - (100*a*b)
        self.discount = tot
        if self.product_id:        

            if self.invoice_id.type=='out_invoice': 
                pricelist_data = self.invoice_id.partner_id.property_product_pricelist
            elif self.invoice_id.type=='in_invoice':
                pricelist_data = self.invoice_id.partner_id.property_product_pricelist_purchase                
            rule = self.env['product.pricelist'].pricelist_item_get(pricelist_data,[(self.product_id, self.quantity or 1.0, self.invoice_id.partner_id.id)])[self.product_id.id]         

            if rule and rule.is_net_price and tot > 0:
                return {'warning':{'title': _('Warning!'), 'message': _('Sum of setted discounts is greater than what setted as maximum discount!')} }              
            if self.max_discount > 0 and partial_tot > self.max_discount:
                return {'warning':{'title': _('Warning!'), 'message': _('Sum of setted discounts is greater than what setted as maximum discount!')} }        

    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_limit_discount(self):
        total_discount = 100 - (100*((100-self.discount1)/100)*((100-self.discount2)/100))
        if self.product_id:

            pricelist_data = None
            rule = None            
            if self.type=='out_invoice': 
                pricelist_data = self.invoice_id.partner_id.property_product_pricelist
            elif self.type=='in_invoice':
                pricelist_data = self.invoice_id.partner_id.property_product_pricelist_purchase              
            
            if pricelist_data:
                rule = self.env['product.pricelist'].pricelist_item_get(pricelist_data,[(self.product_id, self.quantity or 1.0, self.invoice_id.partner_id.id)])[self.product_id.id]         
            if rule and rule.is_net_price and total_discount > 0:
                raise ValidationError(_("Sum of discounts can't be greater than what setted as maximum discount!"))  
                     
        if self.max_discount and total_discount - self.max_discount > 0.0001:
            raise ValidationError(_("Sum of discounts can't be greater than what setted as maximum discount!"))     
        
    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, company_id=None):    
        res = super(account_invoice_line_family_discount,self).product_id_change(product, uom_id, qty=qty, name=name, type=type, partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id, company_id=company_id)

        if res and res['value'] and partner_id and product:
            res['value']['discount3'] = 0.0

            rule = None
            if type=='out_invoice': 
                pricelist_data = self.env['res.partner'].browse(partner_id).property_product_pricelist
            elif type=='in_invoice':
                pricelist_data = self.env['res.partner'].browse(partner_id).property_product_pricelist_purchase            
            
            product_data = self.env['product.product'].browse(product)
            if pricelist_data:   
                rule = self.pool.get('product.pricelist').pricelist_item_get(self._cr, self._uid, pricelist_data,[(product_data, qty or 1.0, partner_id)], context=self._context)[product]

            if not rule or (rule and not rule.is_net_price):
            
                product_data = self.env['product.product'].browse(product)
                partner_data = self.env['res.partner'].browse(partner_id)
                filter = partner_data.company_id.family_type_filter            
                for discount in partner_data.family_discount_ids:
                    if filter == 'family':
                        if discount.family_id == product_data.family:
                            res['value']['discount3'] = discount.discount                        
                            break
                    elif filter == 'subfamily':
                        if discount.family_id == product_data.subfamily:
                            res['value']['discount3'] = discount.discount                        
                            break
                    elif filter == 'subgroup':
                        if discount.family_id == product_data.subgroup:
                            res['value']['discount3'] = discount.discount                           
                            break
                    elif filter == 'classifier1':
                        if discount.family_id == product_data.classifier1: 
                            res['value']['discount3'] = discount.discount
                            break
                    elif filter == 'classifier2':
                        if discount.family_id == product_data.classifier2:  
                            res['value']['discount3'] = discount.discount                  
                            break
                    elif filter == 'classifier3':
                        if discount.family_id == product_data.classifier3:   
                            res['value']['discount3'] = discount.discount                 
                            break
        return res
        