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

class sale_order_line_family_discount(models.Model):

    _inherit = 'sale.order.line'

    @api.onchange('discount1','discount2','discount3','max_discount')
    def onchange_discount(self):
        a = (100-self.discount1)/100
        b = (100-self.discount2)/100
        c = (100-self.discount3)/100
        tot = 100 - (100*a*b*c)
        partial_tot = 100 - (100*a*b)
        self.discount = tot
        if self.product_id:
            rule = self.env['product.pricelist'].with_context(date=self.order_id.date_order).pricelist_item_get(self.order_id.pricelist_id,[(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id.id)])[self.product_id.id]         
            if rule and rule.is_net_price and tot > 0:
                return {'warning':{'title': _('Warning!'), 'message': _('Sum of setted discounts is greater than what setted as maximum discount!')} }             
            if self.max_discount > 0 and partial_tot - self.max_discount > 0.0001:
                return {'warning':{'title': _('Warning!'), 'message': _('Sum of setted discounts is greater than what setted as maximum discount!')} }        

    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_limit_discount(self):
        total_discount = 100 - (100*((100-self.discount1)/100)*((100-self.discount2)/100)*((100-self.discount3)/100))
        if self.product_id:
            rule = self.env['product.pricelist'].with_context(date=self.order_id.date_order).pricelist_item_get(self.order_id.pricelist_id,[(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id.id)])[self.product_id.id]         
            if rule and rule.is_net_price and total_discount > 0:
                raise ValidationError(_("Sum of discounts can't be greater than what setted as maximum discount!"))              
        if self.max_discount and total_discount - self.max_discount > 0.0001:
            raise ValidationError(_("Sum of discounts can't be greater than what setted as maximum discount!"))     
        
    @api.cr_uid_ids_context
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):

        res = super(sale_order_line_family_discount,self).product_id_change(cr, uid, ids, pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name,partner_id=partner_id, lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context )
        
        if res and res['value'] and partner_id and product:
            res['value']['discount3'] = 0.0

            ctx = dict(
                context,
                date=date_order,
            )
            product_data = self.pool.get('product.product').browse(cr,uid,product,context=context)
            pricelist_data = self.pool.get('product.pricelist').browse(cr, uid, pricelist, context=context)
            
            rule = self.pool.get('product.pricelist').pricelist_item_get(cr, uid, pricelist_data,[(product_data, qty or 1.0, partner_id)], context=ctx)[product]            
            if not rule or not rule.is_net_price:
                
                product_data = self.pool.get('product.product').browse(cr, uid, product, context=context)
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
