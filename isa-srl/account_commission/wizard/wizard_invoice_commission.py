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
from datetime import date, datetime
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class wizard_invoice_commission(models.TransientModel):

    _name = 'wizard.invoice.commission'
    _description = 'Create Invoice from Commission Lines'
    
    '''
    Sebbene sia possibile richiamare questo wizard selezionando tutte le righe di provvigione, quelle che possono essere effettivamente fatturate sono solo quelle in stato
    'matured', per cui con questo metodo viene eseguito un filtro automatico.
    '''
    def _get_commission_lines(self):
        if 'active_ids' not in self._context or not self._context['active_ids']:
            return
        res = []
        commission_obj = self.env['account.commission.line']
        for id in self._context['active_ids']:
            if commission_obj.browse(id).state == 'matured':
                res.append(id)            
        return res
    
    line_ids = fields.Many2many('account.commission.line', string="Commission Lines", default=_get_commission_lines, )
    group_by_invoice = fields.Boolean(string="Group by Invoice", default=True)
    group_by_partner = fields.Boolean(string="Group by Partner", default=True)
    group_by_month = fields.Boolean(string="Group by Month", default=True)
    date = fields.Date(string="Invoice Date", )        

    @api.onchange('group_by_invoice')
    def onchange_group_invoice(self):
        if self.group_by_invoice:
            self.group_by_partner = True
            self.group_by_month = True          

    @api.onchange('group_by_month','group_by_partner')
    def onchange_group(self):
        if self.group_by_month and self.group_by_partner:
            self.group_by_invoice = True
        else:
            self.group_by_invoice = False                             
    
    '''
    Raggruppa le righe in base al tipo di raggruppamento che è stato scelto (per mese, per partner e/o per fattura);
    '''
    @api.multi
    def _get_key_from_line(self, line):
        key1 = (line.salesagent_id,)
        
        date = fields.Date.from_string(line.invoice_date)
        date += relativedelta(day=1)
        
        key2 = (
                    (self.group_by_month and date) or None,
                    (self.group_by_partner and line.partner_id) or None,
                    (self.group_by_invoice and line.invoice_src_id) or None,
               )
        if not key2[0] and not key2[1] and not key2[2]:
            key2 = (line, )            
        return key1, key2

    @api.multi
    def _get_keys(self):
        commission_by_key = {}        
        for line in self.line_ids:                   
            key1, key2 = self._get_key_from_line(line)
            if key1 not in commission_by_key:
                commission_by_key[key1] = {}
            if key2 not in commission_by_key[key1]:
                commission_by_key[key1][key2] = []
            commission_by_key[key1][key2].append(line)                
        return commission_by_key

    @api.multi
    def _get_type(self, keys):
        type = 'in_refund'
        for key in keys:            
            for line in keys[key]:
                if line.invoice_src_type == 'out_invoice':
                    return 'in_invoice'
        return type
    
    @api.multi
    def _get_journal(self, type, company_id):
        if type == 'in_invoice':
            journals = self.env['account.journal'].search([('type','=','purchase'),('company_id','=',company_id)])
        else:
             journals = self.env['account.journal'].search([('type','=','purchase_refund'),('company_id','=',company_id)])
        return (journals and journals[0]) or None      

    @api.multi
    def _get_account(self, product, fpos):
        account_id =  product.property_account_expense or None
        if not account_id:
            account_id = product.categ_id.property_account_expense_categ                
        return fpos.map_account(account_id)    
 
    @api.multi
    def _get_taxes(self, product, company, fpos):
        if self._uid == SUPERUSER_ID:
            taxes = product.taxes_id.filtered(lambda r: r.company_id.id == company.id)
        else:
            taxes = product.taxes_id
        return fpos.map_tax(taxes)  

    @api.multi
    def _get_invoice_vals(self, commission_by_key, user, partner, type, fpos, company, journal):
        invoice_vals = {
                        'date_invoice': self.date,
                        'user_id': user.id,
                        'partner_id': partner.id,
                        'account_id': (partner.property_account_receivable and partner.property_account_receivable.id) or None,
                        'payment_term': (partner.property_supplier_payment_term and partner.property_supplier_payment_term.id) or None,
                        'type': type,
                        'fiscal_position': (fpos and fpos.id) or None,
                        'company_id': company.id,
                        'currency_id': company.currency_id.id,
                        'journal_id': journal.id,                            
                        }
        return invoice_vals

    @api.multi
    def _get_name(self, subkey):
        name = ''

        if len(subkey) == 1:
            name = _("Commission matured on: '") + subkey[0].line_src_id.name + _("' from invoice n. '") + subkey[0].invoice_id.number + ("' in Date: ") + str(subkey[0].invoice_id.date_invoice) + _(" to the Partner: '") + subkey[0].invoice_id.partner_id.name + _("'")
        else:
            if self.group_by_invoice:
                name = _("Commissions matured on invoice n.: '") + subkey[2].number + ("' in Date: ") + str(subkey[2].date_invoice) + _("; to the Partner: '") + subkey[2].partner_id.name + _("'")
                
            else:
                if self.group_by_partner:
                    name = name + _("Commissions matured on the partner: '") + subkey[1].name + _("' ")
                if self.group_by_month:
                    if name:
                        name = name + _('in ')
                    else:
                        name = name + _('Commissions matured in ')
                    name = name + subkey[0].strftime('%B') + ' ' + subkey[0].strftime('%Y')
        return name
                
    @api.multi
    def create_invoice(self):
        invoices = [] 
        
        commission_by_key = self._get_keys()
        
        # PER OGNI RAGGRUPPAMENTO PRINCIPALE: 
        
        for key in commission_by_key:
            
            # DATI DA UTILIZZARE PER LA TESTATA:
            user = self.env['res.users'].browse(self._uid)
            type = self._get_type(commission_by_key[key])
            journal = self._get_journal(type, user.company_id.id)
            partner = key[0]
            company = user.company_id
            fpos = partner.property_account_position
            
            # DATI COMUNI A TUTTE LE RIGHE:

            product = partner.commission_product_id or company.commission_product_id
            account_id = self._get_account(product, fpos)
            tax_id = self._get_taxes(product, company, fpos)
            
            # CREO LA TESTATA:
            
            invoice_vals = self._get_invoice_vals(commission_by_key[key], user, partner, type, fpos, company, journal)            
            invoice_id = self.env['account.invoice'].create(invoice_vals)
            
            # PER OGNI RAGGRUPPAMENTO SECONDARIO:
            
            for subkey in commission_by_key[key]:
                
                name = self._get_name(subkey)

                price = 0.0
                commission_ids = []                
                for line in commission_by_key[key][subkey]:
                    price += line.amount_commission
                    commission_ids.append(line.id)
                    
                invoice_line_vals = {
                                        'name': name,
                                        'invoice_id': invoice_id.id,
                                        'account_id': account_id.id,
                                        'product_id': product.id,
                                        'uos_id': product.uom_id.id,
                                        'quantity': 1,
                                        'price_unit': price,
                                        'invoice_line_tax_id': [(6, 0, tax_id.ids)],
                                        'discount': 0.0,
                                        'account_analytic_id': False,                                                          
                                    }
                
                invoice_line = self.env['account.invoice.line'].create(invoice_line_vals)
                self.pool.get('account.commission.line').write(self._cr, self._uid, commission_ids, {'line_agent_id':invoice_line.id}, context=self._context)
            
            invoices.append(invoice_id.id)
            
        mod_obj = self.env['ir.model.data']
        result = mod_obj.get_object_reference('account','invoice_tree')
        view_id = result and result[1] or False

        return {'domain': "[('id','in', ["+','.join(map(str,invoices))+"])]",
                'name': _("Commission Invoices"),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'context': {'view_mode':True},
                'views': [(view_id,'tree'),(False,'form')],
                }
        