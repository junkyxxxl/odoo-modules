# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import orm


class salesagent_common(orm.Model):

    _inherit = "salesagent.common"

    # ----- Return the right commission percentuage
    def recognized_commission(self, cr, uid, customer_id, salesagent_id, product_id, base=False):
        commission = super(salesagent_common, self).recognized_commission(cr, uid, customer_id, salesagent_id, product_id)
        commission_base = commission
        if commission != 0.0:
            
            customer_obj = self.pool.get('res.partner')
            customer_id = customer_obj.search(cr, uid, [('id','in',customer_id)])
            customer_data = customer_obj.browse(cr,uid,customer_id)
            
            # If salesagent is a subagent:
            
            if customer_data.salesagent_for_customer_id and customer_data.salesagent_for_customer_id.id != ((salesagent_id and salesagent_id[0]) or False):
                partner_product_commission_obj = self.pool.get('partner.product_commission')
                partner_product_category_commission_obj = self.pool.get('partner.product_category_commission')
                
                # If customer has a special commission reduction for the product
                lst_commission_product_customer = partner_product_commission_obj.search(cr, uid, [('name', '=', product_id), ('partner_id', 'in', customer_id)])
                if lst_commission_product_customer:
                    commission = commission - (commission*partner_product_commission_obj.browse(cr, uid, lst_commission_product_customer[0]).subagent_product_commission_reduction)/100
                    if commission < 0.0:
                        commission = 0.0
                        
                    if not base:
                        return commission
                    else:
                        return commission_base - commission
                    
                # If customer has a special commission reduction for the product category
                product_category_data = self.pool.get('product.product').browse(cr, uid, product_id).categ_id
                if product_category_data:
                    lst_commission_product_category_customer = partner_product_category_commission_obj.search(cr, uid, [('name', '=', product_category_data.id), ('partner_id', 'in', customer_id)])
                    if lst_commission_product_category_customer:
                        commission = commission - (commission*partner_product_category_commission_obj.browse(cr, uid, lst_commission_product_category_customer[0]).subagent_category_commission_reduction)
                        if commission < 0.0:
                            commission = 0.0
                            
                        if not base:
                            return commission
                        else:
                            return commission_base - commission                  
    
                # If customer has a special generic commission reduction
                reduction = self.pool.get('res.partner').browse(cr, uid, customer_id).subagent_commission_reduction
                if reduction > 0.0:
                    commission = commission - (commission*reduction)/100
                    if commission < 0.0:
                        commission = 0.0
                        
                    if not base:
                        return commission
                    else:
                        return commission_base - commission                  
                
                # If salesagent has a special commission reduction for the product
                lst_commission_product_customer = partner_product_commission_obj.search(cr, uid, [('name', '=', product_id), ('partner_id', 'in', salesagent_id)])
                if lst_commission_product_customer:
                    commission = commission - (commission*partner_product_commission_obj.browse(cr, uid, lst_commission_product_customer[0]).subagent_product_commission_reduction)/100
                    if commission < 0.0:
                        commission = 0.0
                        
                    if not base:
                        return commission
                    else:
                        return commission_base - commission          
    
                # If salesagent has a special commission reduction for the product category
                product_category_data = self.pool.get('product.product').browse(cr, uid, product_id).categ_id
                if product_category_data:
                    lst_commission_product_category_customer = partner_product_category_commission_obj.search(cr, uid, [('name', '=', product_category_data.id), ('partner_id', 'in', salesagent_id)])
                    if lst_commission_product_category_customer:
                        commission = commission - (commission*partner_product_category_commission_obj.browse(cr, uid, lst_commission_product_category_customer[0]).subagent_category_commission_reduction)/100
                        if commission < 0.0:
                            commission = 0.0
                            
                        if not base:
                            return commission
                        else:
                            return commission_base - commission
    
                # If salesagent has a special generic commission reduction
                reduction = self.pool.get('res.partner').browse(cr, uid, salesagent_id).subagent_commission_reduction
                if reduction:
                    commission = commission - (commission*reduction)/100
                    if commission < 0.0:
                        commission = 0.0 
                        
                    if not base:
                        return commission
                    else:
                        return commission_base - commission
                
                # If product has a special generic commission reduction
                reduction = self.pool.get('product.product').browse(cr, uid, product_id).subagent_commission_reduction
                if reduction:
                    commission = commission - (commission*reduction)/100
                    if commission < 0.0:
                        commission = 0.0 
                        
                    if not base:
                        return commission
                    else:
                        return commission_base - commission
    
                # If product category has a special generic commission reduction
                product_data = self.pool.get('product.product').browse(cr, uid, product_id)
                if product_data.categ_id:
                    categ_id = product_data.categ_id.id
                    reduction = self.pool.get('product.category').browse(cr, uid, categ_id).subagent_commission_reduction
                    if reduction:
                        commission = commission - (commission*reduction)/100
                        if commission < 0.0:
                            commission = 0.0 
                            
                        if not base:
                            return commission
                        else:
                            return commission_base - commission
                                      
        if not base:
            return commission
        else:
            return commission_base - commission

    # ----- Calcola la provvigione totale da riconoscere all'agente
    def commission_calculate(self, cr, uid, param_class, id, base=False, context=None):
        '''
        @classe : Indica la classe di riferimento per gli id passati al parametro ids
        @id : id della classe di cui si vuole calcolare la provvigione
        '''
        class_brows = self.pool.get(param_class).browse(cr, uid, id, context)
        total_commission = 0.0
        if param_class == 'account.invoice.line':
            salesagent = class_brows.invoice_id.salesagent_id or False
            customer = class_brows.invoice_id.partner_id
            product = class_brows.product_id or False
            total_price = class_brows.price_subtotal
        percentage_commission = self.recognized_commission(cr, uid, customer and [customer.id] or False, salesagent and [salesagent.id] or False, product and product.id or False, base)
        if percentage_commission:
            if not class_brows.free:
                total_commission = (total_price * percentage_commission) / 100
                for disc_line in class_brows.invoice_id.global_discount_lines:
                    t_disc = total_commission * disc_line.value / 100
                    total_commission -= t_disc
        return total_commission