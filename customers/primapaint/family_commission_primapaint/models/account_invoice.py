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

class account_invoice_commission(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def force_commission_recompute(self):

        company_obj = self.env['res.company']
        commission_obj = self.env['account.commission.line']
        
        inv_line_ids = self.invoice_line
        invoice = self
        any_change = False

        if commission_obj.search([('invoice_src_id','=',invoice.id),('state','in',['invoiced','paid'])]):
            raise Warning('Some Commission Line for this Invoice are already invoiced or paid')
        
        old_commission_ids = commission_obj.search([('invoice_src_id','=',invoice.id)])
        
        for line_id in inv_line_ids:
            if invoice.type in ['out_invoice','out_refund'] and invoice.partner_id and invoice.user_id and invoice.user_id.partner_id.salesagent:
                comm_perc = 0.0                  
                if line_id.product_id and not line_id.product_id.no_commission and not line_id.product_id.categ_id.no_commission:
                    
                    salesagent_id = invoice.user_id.partner_id
                    partner = invoice.partner_id
                    partner_id = partner.id
                    company = invoice.company_id
                    product = line_id.product_id                                  

                    if salesagent_id.is_overriding:
                        for comm_line in salesagent_id.custom_commission_line_ids:
                            if not comm_line.partner_id or comm_line.partner_id.id == partner_id:
                                if not comm_line.category_id or comm_line.category_id.id == product.categ_id.id:
                                    if not comm_line.template_id or comm_line.template_id.id == product.product_tmpl_id.id:
                                        if not comm_line.product_id or comm_line.product_id.id == product.id:
                                            comm_perc = comm_line.commission_perc
                                            break       

                    rule = None
                    pricelist_data = None
                    if self.type=='out_invoice': 
                        pricelist_data = self.env['res.partner'].browse(partner.id).property_product_pricelist
                    elif self.type=='in_invoice':
                        pricelist_data = self.env['res.partner'].browse(partner.id).property_product_pricelist_purchase      
                        
                    product_data = product
                    if pricelist_data:   
                        rule = self.pool.get('product.pricelist').pricelist_item_get(self._cr, self._uid, pricelist_data,[(product_data, line_id.quantity or 1.0, partner.id)], context=self._context)[product.id]                               
                    
                    
                    if comm_perc == 0.0:
                        if company.commission_priority1:
                            comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority1, product, partner_id, salesagent_id)
                        if not comm_perc and company.commission_priority2:
                            comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority2, product, partner_id, salesagent_id)                
                        if not comm_perc and company.commission_priority3:
                            comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority3, product, partner_id, salesagent_id)                
                        if not comm_perc and company.commission_priority4:   
                            comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority4, product, partner_id, salesagent_id)                         
                        if not comm_perc and company.commission_priority5:
                            comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority5, product, partner_id, salesagent_id)
                            
                if comm_perc < 0.0:
                    comm_perc = 0.0
                            
                if comm_perc != line_id.commission_perc:
                    line_id.write({'commission_perc':comm_perc})
                    any_change = True
                            
            
        if any_change and invoice.state != 'draft':
            for old_commission in old_commission_ids:
                old_commission.unlink()
            invoice.create_commission_line()
            
        return True   

class account_invoice_line_family_commission(models.Model):

    _inherit = 'account.invoice.line' 

    @api.multi
    def product_id_change(self, product_id, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, company_id=None):    
        res = super(account_invoice_line_family_commission,self).product_id_change(product_id, uom_id, qty=qty, name=name, type=type, partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id, company_id=company_id)

        if res and res['value'] and partner_id and product_id and type in ['out_invoice','out_refund'] and 'user_id' in self._context and self._context['user_id'] and self.pool.get('res.users').browse(self._cr, self._uid, self._context['user_id'], context=self._context).partner_id.salesagent:
            salesagent_id = self.pool.get('res.users').browse(self._cr, self._uid, self._context['user_id'], context=self._context).partner_id
            comm_perc = 0.0                  

            if product_id and not self.env['product.product'].browse(product_id).no_commission and not self.env['product.product'].browse(product_id).categ_id.no_commission:
                cmp_id = company_id or self._context.get('company_id',False) or self.env['res.users'].browse(self._uid).company_id.id
                company_obj = self.env['res.company']
                company = company_obj.browse(cmp_id)
                product = self.pool.get('product.product').browse(self._cr, self._uid, product_id, context=self._context)                     

                if salesagent_id.is_overriding:
                    for comm_line in salesagent_id.custom_commission_line_ids:
                        if not comm_line.partner_id or comm_line.partner_id.id == partner_id:
                            if not comm_line.category_id or comm_line.category_id.id == product.categ_id.id:
                                if not comm_line.template_id or comm_line.template_id.id == product.product_tmpl_id.id:
                                    if not comm_line.product_id or comm_line.product_id.id == product.id:
                                        comm_perc = comm_line.commission_perc
                                        break

                rule = None
                pricelist_data = None
                if type=='out_invoice': 
                    pricelist_data = self.env['res.partner'].browse(partner_id).property_product_pricelist
                elif type=='in_invoice':
                    pricelist_data = self.env['res.partner'].browse(partner_id).property_product_pricelist_purchase      
                    
                product_data = product
                if pricelist_data:   
                    rule = self.pool.get('product.pricelist').pricelist_item_get(self._cr, self._uid, pricelist_data,[(product_data, qty or 1.0, partner_id)], context=self._context)[product.id]   
                                     
            
                if comm_perc == 0.0:
                    if company.commission_priority1:
                        comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority1, product, partner_id, salesagent_id)
                    if not comm_perc and company.commission_priority2:
                        comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority2, product, partner_id, salesagent_id)                
                    if not comm_perc and company.commission_priority3:
                        comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority3, product, partner_id, salesagent_id)                
                    if not comm_perc and company.commission_priority4:   
                        comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority4, product, partner_id, salesagent_id)                         
                    if not company.commission_priority5:
                        comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority5, product, partner_id, salesagent_id)
            if comm_perc >= 0:                 
                res['value']['commission_perc'] = comm_perc        
            elif comm_perc == -5.0:
                res['value']['commission_perc'] = 0.0  
            else:
                res['warning'] = {'title':'Maximum Discount Exceeded','message':'You cannot set a total discount greater than what is allowed for this customer'} 
        return res

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
        None
       
    @api.one
    @api.constrains('discount')
    def _check_max_discount(self):

        max_discount = 0
        if self.product_id and self.product_id.family and self.account_id and self.account_id.partner_id:
            max_discount = 0
            partner = self.account_id.partner_id        
            
            if partner.family_discount_ids:
                for line in partner.family_discount_ids:
                    if line.family_id.id == self.product_id.family.id:
                        max_discount = line.discount     

            t_discount = 0
            for line in self.product_id.family.commission_discount_ids:
                if line.discount > t_discount:
                    t_discount = line.discount

            max_discount = 100 - (100 * ((100-max_discount)/100) * ((100-t_discount)/100))    
        
            if self.discount - max_discount > 0.00001:
                raise ValidationError(_("Maximum Discount Exceeded','message':'You cannot set a total discount greater than what is allowed for this customer"))                       

            
    @api.onchange('discount')
    def onchange_base_discount(self):
        res = {}
        if self.product_id and self.product_id.family and self.invoice_id:
            max_discount = 0
            partner = self.invoice_id.partner_id        
            
            if partner.family_discount_ids:
                for line in partner.family_discount_ids:
                    if line.family_id.id == self.product_id.family.id:
                        max_discount = line.discount     

            t_discount = 0
            for line in self.product_id.family.commission_discount_ids:
                if line.discount > t_discount:
                    t_discount = line.discount

            max_discount = 100 - (100 * ((100-max_discount)/100) * ((100-t_discount)/100))        
        
            if self.discount - max_discount > 0.00001:
                res['warning'] = {'title':'Maximum Discount Exceeded','message':'You cannot set a total discount greater than what is allowed for this customer'}

            if self.invoice_id.user_id and self.invoice_id.user_id.partner_id and self.invoice_id.user_id.partner_id.salesagent:    
                
                company = self.invoice_id.company_id
                product = self.product_id
                salesagent_id = self.invoice_id.user_id.partner_id    

                rule = None
                pricelist_data = None
                if self.invoice_id.type=='out_invoice': 
                    pricelist_data = self.env['res.partner'].browse(partner.id).property_product_pricelist
                elif self.invoice_id.type=='in_invoice':
                    pricelist_data = self.env['res.partner'].browse(partner.id).property_product_pricelist_purchase      
                    
                product_data = product
                if pricelist_data:   
                    rule = self.pool.get('product.pricelist').pricelist_item_get(self._cr, self._uid, pricelist_data,[(product_data, self.quantity or 1.0, partner.id)], context=self._context)[product.id]                               
                
                comm_perc = 0
                company_obj = self.env['res.company']
                if company.commission_priority1:
                    comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority1, product, partner.id, salesagent_id, self.discount)
                if not comm_perc and company.commission_priority2:
                    comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority2, product, partner.id, salesagent_id, self.discount)                
                if not comm_perc and company.commission_priority3:
                    comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority3, product, partner.id, salesagent_id, self.discount)                
                if not comm_perc and company.commission_priority4:   
                    comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority4, product, partner.id, salesagent_id, self.discount)                         
                if not company.commission_priority5:
                    comm_perc = company_obj.with_context(pricelist_item_id = (rule and rule.id) or None).get_commission_perc(company.commission_priority5, product, partner.id, salesagent_id, self.discount)
                
                if comm_perc >= 0:                 
                    self.commission_perc = comm_perc       
                elif comm_perc == -5.0:
                    self.commission_perc = 0.0                         
                else:
                    res['warning'] = {'title':'Maximum Discount Exceeded','message':'You cannot set a total discount greater than what is allowed for this customer'}
            if res:
                return res            