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

class res_partner_commission_line(models.Model):
    _name = 'res.partner.commission.line'
    _description = 'Salesagent Custom Commission Lines'
    _order = 'sequence'
    
    salesagent_id = fields.Many2one('res.partner', string="Salesagent", )
    partner_id = fields.Many2one('res.partner', string="Customer", )
    category_id = fields.Many2one('product.category', string="Category", )
    template_id = fields.Many2one('product.template', string="Product Template", )
    product_id = fields.Many2one('product.product', string="Product", )    
    commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'), )        
    sequence = fields.Integer('Sequence')

    @api.one
    @api.constrains('commission_perc')
    def _check_commission(self):
        if self.commission_perc < 0.0 or self.commission_perc > 100.0:
            raise ValidationError(_("Commission should be between 0 and 100!"))

class res_partner_commission(models.Model):

    _inherit = 'res.partner'

    def _get_default_salesagent(self):
        user = self.env['res.users'].browse(self._uid).partner_id
        if not user.salesagent:
            return self.env['res.partner'].browse(0)
        else:
            return user

    def _get_commission_product(self):
        if not self.salesagent:
            return self.env['product.product'].browse(0)
        if self.company_id:
            return self.company_id.commission_product_id
        return self.env['res.users'].browse(self._uid).company_id.commission_product_id

    '''
    In questa funzione è stato utilizzato il metodo 'sudo()' per eseguire la browse con credenziali di superuser. Ciò è necessario in quanto l'utente 'Administrator' 
    non è sempre visibile dagli agenti (infatti potrebbe spesso non esserlo) e tuttavia essere collegato a dei partner legati all'agente (e dunque da questi visibili ed 
    esplorabili) attraverso campi quali 'create_uid'. In tal caso, senza le credenziali di superuser, questo metodo restituirebbe un'eccezione che impedisce di fatto l'accesso
    al partner.
    '''
    @api.one
    def _get_is_salesagent(self):
            self.is_salesagent = self.env['res.users'].sudo().browse(self._uid).salesagent
            
    def _get_is_salesagent_default(self):
        return self.env['res.users'].browse(self._uid).salesagent

    is_salesagent = fields.Boolean(compute='_get_is_salesagent', string="Agente", default=_get_is_salesagent_default)  

    salesagent = fields.Boolean(string='Salesagent', help="If flagged, this partner is a salesagent", default=False, )
    is_overriding = fields.Boolean(strin='Salesagent overrides default commission rules', default=False)
    
    salesagent_commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'), )
    customer_commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'), )    
    salesagent_parent_commission_perc = fields.Float(string="Parent Commission [%]", digits_compute= dp.get_precision('Account'), )

    salesagent_code = fields.Char(string="Salesagent Code", )

    commission_mode = fields.Selection([('invoiced','Invoiced'),('paid','Paid')], string="Commission Mode", help="Defines the maturity conditions for commissions", default=None, )    
    
    salesagent_id = fields.Many2one('res.partner', string="Salesagent", default=_get_default_salesagent, )
    salesagent_parent_id = fields.Many2one('res.partner', string="Salesagent-Chief", )
    salesagent_child_ids = fields.One2many('res.partner', 'salesagent_parent_id', string="Attendant Salesagents")
    salesagent_customer_ids = fields.One2many('res.partner','salesagent_id', string="Customers")
    commission_product_id = fields.Many2one('product.product', string="Commission Product", help="This product will be used as product in commission invoicing", default=_get_commission_product, )
    custom_commission_line_ids = fields.One2many('res.partner.commission.line', 'salesagent_id', string='Custom Commissions')

    @api.onchange('salesagent_parent_id')
    def onchange_salesagent_parent(self):
        if not self.salesagent_parent_id:
            self.salesagent_parent_commission_perc = 0.0
    
    @api.onchange('salesagent')
    def onchange_salesagent(self):
        if self.salesagent:
            self.supplier = True
            if self.company_id:
                self.commission_product_id = self.company_id.commission_product_id.id
            else:
                self.commission_product_id = self.env['res.users'].browse(self._uid).company_id.commission_product_id.id            
        else:
            self.salesagent_commission_perc = 0.0
            self.salesagent_parent_commission_perc = 0.0
            self.salesagent_parent_id = None
            self.commission_mode = None
            self.commission_product_id = None
            self.salesagent_code = ''

    @api.onchange('supplier')
    def onchange_supplier(self):
        if not self.supplier:
            self.salesagent = False

    @api.onchange('customer')
    def onchange_customer(self):
        if not self.customer:
            self.salesagent_id = None
            self.customer_commission_perc = 0.0

    @api.onchange('salesagent_id')
    def onchange_salesagent_id(self):
        if not self.salesagent_id:
            self.customer_commission_perc = 0.0

    @api.one
    @api.constrains('salesagent_commission_perc','salesagent_parent_commission_perc','customer_commission_perc')
    def _check_commission(self):
        if self.customer_commission_perc < 0.0 or self.customer_commission_perc > 100.0:
            raise ValidationError(_("Commission should be between 0 and 100!"))
        if self.salesagent_parent_commission_perc < 0.0 or self.salesagent_parent_commission_perc > 100.0:
            raise ValidationError(_("Parent Commission should be between 0 and 100!"))      
        if self.salesagent_commission_perc < 0.0 or self.salesagent_commission_perc > 100.0:
            raise ValidationError(_("Parent Commission should be between 0 and 100!"))                              

    @api.one
    @api.constrains('salesagent_code')
    def _check_salesagent_code(self):
        if self.salesagent_code:
            lst = self.search([('salesagent_code','ilike',self.salesagent_code),('id','!=',self.id)])
            if lst:
                raise ValidationError(_('The specified Salesagent Code already exists into the system!'))       
        
    