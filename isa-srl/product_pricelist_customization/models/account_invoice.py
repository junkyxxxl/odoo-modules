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

class account_invoice_line_discount(models.Model):

    _inherit = 'account.invoice.line'

    discount1 = fields.Float(string="Sconto1", digits= dp.get_precision('Discount'),)
    discount2 = fields.Float(string="Sconto2", digits= dp.get_precision('Discount'),)
    discount3 = fields.Float(string="Sconto3", digits= dp.get_precision('Discount'),)
    max_discount = fields.Float(string="Sconto Massimo", digits= dp.get_precision('Discount'),)        
    
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
        
    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, company_id=None):    
        res = super(account_invoice_line_discount,self).product_id_change(product, uom_id, qty=qty, name=name, type=type, partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id, company_id=company_id)

        if res and res['value'] and partner_id and product:
            pricelist = None
            if type=='out_invoice': 
                pricelist = self.env['res.partner'].browse(partner_id).property_product_pricelist
            elif type=='in_invoice':
                pricelist = self.env['res.partner'].browse(partner_id).property_product_pricelist_purchase
                
            if pricelist:                
                product_data = self.env['product.product'].browse(product)
                discount = self.env['product.pricelist'].discounts_get(pricelist,[(product_data, qty or 1.0, partner_id)])[product]
                res['value']['discount1'] = discount[0]
                res['value']['discount2'] = discount[1]
                res['value']['discount3'] = discount[2]
                res['value']['max_discount'] = discount[3]
        return res
        