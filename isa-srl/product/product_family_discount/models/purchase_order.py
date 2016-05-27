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

class purchase_order_line_family_discount(models.Model):

    _inherit = 'purchase.order.line'

    @api.onchange('discount1','discount2','discount3','max_discount')
    def onchange_discount(self):
        a = (100-self.discount1)/100
        b = (100-self.discount2)/100
        c = (100-self.discount3)/100
        tot = 100 - (100*a*b*c)
        partial_tot = 100 - (100*a*b)
        self.discount = tot
        if self.max_discount > 0 and partial_tot > self.max_discount:
            return {'warning':{'title': _('Warning!'), 'message': _('Sum of setted discounts is greater than what setted as maximum discount!')} }        

    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_limit_discount(self):
        total_discount = 100 - (100*((100-self.discount1)/100)*((100-self.discount2)/100))
        if self.max_discount and total_discount - self.max_discount > 0.0001:
            raise ValidationError(_("Sum of discounts can't be greater than what setted as maximum discount!"))     
        
    @api.cr_uid_ids_context    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order=False, fiscal_position_id=False, date_planned=False, name=False, price_unit=False, state='draft', context=None):        
        res = super(purchase_order_line_family_discount, self).onchange_product_id(cr,uid,ids,pricelist_id,product_id,qty,uom_id,partner_id,date_order,fiscal_position_id,date_planned,name,price_unit,state,context)

        if res and res['value'] and partner_id and product_id:
            res['value']['discount3'] = 0.0
            product_data = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            partner_data = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
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

        