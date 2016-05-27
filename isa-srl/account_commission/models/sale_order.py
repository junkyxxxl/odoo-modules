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

class sale_order_commission(models.Model):

    _inherit = 'sale.order'

    @api.one
    def _get_is_salesagent(self):
        self.is_salesagent = self.env['res.users'].browse(self._uid).salesagent

    def _get_is_salesagent_default(self):
        return self.env['res.users'].browse(self._uid).salesagent

    is_salesagent = fields.Boolean(compute='_get_is_salesagent', string="Agente", default=_get_is_salesagent_default)  

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = super(sale_order_commission, self).onchange_partner_id(cr, uid, ids, partner_id, context=context)
        if res and partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            if partner and partner.salesagent_id:
                if partner.salesagent_id.user_ids:
                    user = partner.salesagent_id.user_ids.ids[0]           
                else:
                    user = uid
                if  user: 
                    if 'value' in res:
                        res['value'].update({'user_id':user})
                    else:
                        res['value'] = {'user_id':partner.salesagent_id.user_id.id}
        return res
    
    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.order_line:
            return {'warning':{'title': _('Warning!'), 'message': _('This order already contains some lines, commission on those lines will not be automatically recomputed!')} }  

class sale_order_line_commission(models.Model):

    _inherit = 'sale.order.line'

    @api.one
    def _get_is_salesagent(self):
        self.is_salesagent = self.env['res.users'].browse(self._uid).salesagent

    def _get_is_salesagent_default(self):
        return self.env['res.users'].browse(self._uid).salesagent

    is_salesagent = fields.Boolean(compute='_get_is_salesagent', string="Agente", default=_get_is_salesagent_default)      
    commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'),)
    commission_amount = fields.Float(compute="_compute_commission_amount", string="Commission", digits_compute= dp.get_precision('Account'),)    
    
    @api.one
    @api.depends('price_subtotal', 'commission_perc')      
    def _compute_commission_amount(self):
        self.commission_amount = self.price_subtotal * self.commission_perc / 100.0

    @api.cr_uid_ids_context
    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):

        res = super(sale_order_line_commission, self).product_id_change(cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context=context)
  
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
                
                if comm_perc == 0.0:
                    if company.commission_priority1:
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority1, product, partner_id, salesagent_id, context=context)
                    if not comm_perc and company.commission_priority2:
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority2, product, partner_id, salesagent_id, context=context)                
                    if not comm_perc and company.commission_priority3:
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority3, product, partner_id, salesagent_id, context=context)                
                    if not comm_perc and company.commission_priority4:   
                        comm_perc = company_obj.get_commission_perc(cr, uid, company.commission_priority4, product, partner_id, salesagent_id, context=context)     
            res['value']['commission_perc'] = comm_perc           
        return res

    @api.cr_uid_ids_context    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line_commission, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        if res:
            res.update({'commission_perc':line.commission_perc,
                        'commission_amount':line.commission_amount,})
        return res