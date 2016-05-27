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

class purchase_order_line_discount(models.Model):

    _inherit = 'purchase.order.line'

    discount1 = fields.Float(string="Sconto1", digits_compute= dp.get_precision('Discount'),)
    discount2 = fields.Float(string="Sconto2", digits_compute= dp.get_precision('Discount'),)
    discount3 = fields.Float(string="Sconto3", digits_compute= dp.get_precision('Discount'),)
    max_discount = fields.Float(string="Sconto Massimo", digits_compute= dp.get_precision('Discount'),)    
    
    @api.onchange('discount1','discount2','discount3','max_discount')
    def onchange_discount(self):
        a = (100-self.discount1)/100
        b = (100-self.discount2)/100
        c = (100-self.discount3)/100
        tot = 100 - (100*a*b*c)
        self.discount = tot
        if self.max_discount > 0 and self.discount > self.max_discount:
            return {'warning':{'title': _('Warning!'), 'message': _('Sum of setted discounts is greater than what setted as maximum discount!')} }        

    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_limit_discount(self):
        
        total_discount = 100 - (100*((100-self.discount1)/100)*((100-self.discount2)/100)*((100-self.discount3)/100))
        if self.max_discount and total_discount - self.max_discount > 0.0001:
            raise ValidationError(_("Sum of discounts can't be greater than what setted as maximum discount!"))          

    @api.cr_uid_ids_context    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order=False, fiscal_position_id=False, date_planned=False, name=False, price_unit=False, state='draft', context=None):        
        res = super(purchase_order_line_discount, self).onchange_product_id(cr,uid,ids,pricelist_id,product_id,qty,uom_id,partner_id,date_order,fiscal_position_id,date_planned,name,price_unit,state,context)

        if product_id and res and res['value']:
            ctx = dict(context, date=date_order,
            )            
            product_data = self.pool.get('product.product').browse(cr,uid,product_id,context=context)
            pricelist_data = self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context)
            discount = self.pool.get('product.pricelist').discounts_get(cr, uid, pricelist_data,[(product_data, qty or 1.0, partner_id)], context=ctx)[product_id]
            res['value']['discount1'] = discount[0]
            res['value']['discount2'] = discount[1]
            res['value']['discount3'] = discount[2]
            res['value']['max_discount'] = discount[3]
        return res

    @api.cr_uid_ids_context    
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order_line_discount, self)._prepare_inv_line(cr, uid, account_id, order_line, context=context)
        if res:
            res.update({'discount1':order_line.discount1,
                        'discount2':order_line.discount2,
                        'discount3':order_line.discount3,
                        'max_discount':order_line.max_discount,})
        return res
        