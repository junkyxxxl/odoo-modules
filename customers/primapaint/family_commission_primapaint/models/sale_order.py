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

class sale_order_line_family_commission(models.Model):

    _inherit = 'sale.order.line'

    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_limit_discount(self):
        total_discount = 100 - (100*((100-self.discount1)/100)*((100-self.discount2)/100)*((100-self.discount3)/100))
        if self.product_id:
            rule = self.env['product.pricelist'].with_context(date=self.order_id.date_order).pricelist_item_get(self.order_id.pricelist_id,[(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id.id)])[self.product_id.id]         
            if rule and rule.is_net_price and total_discount > 0:
                raise ValidationError(_('Sum of setted discounts is greater than what setted as maximum discount!'))               
        return


    @api.one
    @api.constrains('product_uom_qty','product_id')
    def _check_total_qty(self):
        if self.product_id:
            if self.product_uom_qty == 0.0:
                raise ValidationError(_("There are invoice lines with quantity setted to 0, which is not allowed!"))                                       
        return


    @api.one
    @api.constrains('discount')
    def _check_max_discount(self):

        max_discount = 0
        if self.product_id and self.product_id.family and self.order_id:
            max_discount = 0
            partner = self.order_id.partner_id        
            
            if partner.family_discount_ids:
                for line in partner.family_discount_ids:
                    if line.family_id.id == self.product_id.family.id:
                        max_discount = line.discount     


            t_discount = 0
            
            special_category = False
            for line in self.product_id.family.category_commission_ids:
                if line.special_partner_category_id == partner.partner_category:
                    special_category = True
                    break
            
            if not special_category:
                for line in self.product_id.family.commission_discount_ids:
                    if line.discount > t_discount:
                        t_discount = line.discount
                
            max_discount = 100 - (100 * ((100-max_discount)/100) * ((100-t_discount)/100))                
        
        if self.discount - max_discount > 0.00001:
            raise ValidationError(_("Maximum Discount Exceeded','message':'You cannot set a total discount greater than what is allowed for this customer"))                       

    @api.cr_uid_ids_context
    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):
        res = self.product_id_change(cr, uid, ids, pricelist, product, qty=qty, uom=False, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id, lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if 'warning' in res:
            del res['warning']
        return res        
    
    @api.cr_uid_ids_context
    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):

        res = super(sale_order_line_family_commission, self).product_id_change(cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context=context)

        if res and res['value'] and partner_id and product_id and 'user_id' in context and context['user_id'] and self.pool.get('res.users').browse(cr, uid, context['user_id']).partner_id.salesagent:
            salesagent_id = self.pool.get('res.users').browse(cr, uid, context['user_id'], context=context).partner_id
            comm_perc = 0.0        

            if product_id and not self.pool.get('product.product').browse(cr, uid, product_id, context=context).no_commission and not self.pool.get('product.product').browse(cr, uid, product_id, context=context).categ_id.no_commission:
                cmp_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
                company_obj = self.pool.get('res.company')
                company = company_obj.browse(cr, uid, cmp_id, context=context)
                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                        

                if salesagent_id.is_overriding:
                    for comm_line in salesagent_id.custom_commission_line_ids:
                        if not comm_line.partner_id or comm_line.partner_id.id == partner_id:
                            if not comm_line.category_id or comm_line.category_id.id == product.categ_id.id:
                                if not comm_line.template_id or comm_line.template_id.id == product.product_tmpl_id.id:
                                    if not comm_line.product_id or comm_line.product_id.id == product.id:
                                        comm_perc = comm_line.commission_perc
                                        break

                rule = None
                pricelist_data = self.pool.get('product.pricelist').browse(cr, uid, pricelist, context=context)                
                product_data = product
                if pricelist_data:   
                    rule = self.pool.get('product.pricelist').pricelist_item_get(cr, uid, pricelist_data,[(product_data, qty or 1.0, partner_id)], context=context)[product.id]   
               
            
                ctx = dict(
                    context,
                    pricelist_item_id=rule.id,
                )                
            
                if comm_perc == 0.0:
                    if company.commission_priority1:
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority1, product, partner_id, salesagent_id, context=ctx)
                    if not comm_perc and company.commission_priority2:
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority2, product, partner_id, salesagent_id, context=ctx)                
                    if not comm_perc and company.commission_priority3:
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority3, product, partner_id, salesagent_id, context=ctx)                
                    if not comm_perc and company.commission_priority4:   
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority4, product, partner_id, salesagent_id, context=ctx)                         
                    if not comm_perc and company.commission_priority5:
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority5, product, partner_id, salesagent_id, context=ctx)
            if comm_perc >= 0:                 
                res['value']['commission_perc'] = comm_perc        
            elif comm_perc == -5.0:
                res['value']['commission_perc'] = 0.0  
            else:
                res['warning'] = {'title':'Maximum Discount Exceeded','message':'You cannot set a total discount greater than what is allowed for this customer'} 
        return res
    
    @api.onchange('discount')
    def onchange_base_discount(self):
        res = {}
        if self.product_id and self.product_id.family and self.order_id:
            max_discount = 0
            partner = self.order_id.partner_id   

            
            pricelist = self.order_id.pricelist_id.id     
            rule = None
            pricelist_data = self.pool.get('product.pricelist').browse(self._cr, self._uid, pricelist, context=self._context)                
            product_data = self.product_id
            if pricelist_data:   
                rule = self.pool.get('product.pricelist').pricelist_item_get(self._cr, self._uid, pricelist_data,[(product_data, self.product_uom_qty or 1.0, partner.id)], context=self._context)[product_data.id] 

            
            if partner.family_discount_ids:
                for line in partner.family_discount_ids:
                    if line.family_id.id == self.product_id.family.id:
                        max_discount = line.discount     
            
            t_discount = 0
            
            special_category = False
            for line in self.product_id.family.category_commission_ids:
                if line.special_partner_category_id == partner.partner_category:
                    special_category = True
                    break
            
            if not special_category:
                for line in self.product_id.family.commission_discount_ids:
                    if line.discount > t_discount:
                        t_discount = line.discount
                
            max_discount = 100 - (100 * ((100-max_discount)/100) * ((100-t_discount)/100))        
        
            
            if self.discount - max_discount > 0.00001:
                res['warning'] = {'title':'Maximum Discount Exceeded','message':'You cannot set a total discount greater than what is allowed for this customer'}

            if self.order_id.user_id and self.order_id.user_id.partner_id and self.order_id.user_id.partner_id.salesagent:    
                
                company = self.order_id.company_id
                product = self.product_id
                salesagent_id = self.order_id.user_id.partner_id    
                
                comm_perc = 0
                company_obj = self.env['res.company']
                if company.commission_priority1:
                    comm_perc = company_obj.with_context(pricelist_item_id = rule.id).get_commission_perc(company.commission_priority1, product, partner.id, salesagent_id, self.discount)
                if not comm_perc and company.commission_priority2:
                    comm_perc = company_obj.with_context(pricelist_item_id = rule.id).get_commission_perc(company.commission_priority2, product, partner.id, salesagent_id, self.discount)                
                if not comm_perc and company.commission_priority3:
                    comm_perc = company_obj.with_context(pricelist_item_id = rule.id).get_commission_perc(company.commission_priority3, product, partner.id, salesagent_id, self.discount)                
                if not comm_perc and company.commission_priority4:   
                    comm_perc = company_obj.with_context(pricelist_item_id = rule.id).get_commission_perc(company.commission_priority4, product, partner.id, salesagent_id, self.discount)                         
                if not comm_perc and company.commission_priority5:
                    comm_perc = company_obj.with_context(pricelist_item_id = rule.id).get_commission_perc(company.commission_priority5, product, partner.id, salesagent_id, self.discount)
                
                if comm_perc >= 0:                 
                    self.commission_perc = comm_perc          
                elif comm_perc == -5.0:
                    self.commission_perc = 0.0                       
                else:
                    res['warning'] = {'title':'Maximum Discount Exceeded','message':'You cannot set a total discount greater than what is allowed for this customer'}
            if res:
                return res