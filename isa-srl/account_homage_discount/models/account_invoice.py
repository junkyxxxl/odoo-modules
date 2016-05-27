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

from openerp.osv import fields, orm
from openerp import osv
from openerp.tools.translate import _
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class account_invoice_discount(orm.Model):
    _name = 'account.invoice.discount'
    _description = 'Sconto Globale'
    _order = 'sequence ASC'
    _columns= {
                'name': osv.fields.many2one('account.discount.type', string='Nome', required = True),
                'application': osv.fields.selection([('partner','Cliente'),('payment','Termine di Pagamento'),('general','Generale')], string='Applicazione', required=True),
                'type': osv.fields.selection([('perc','%'),('fisso','Fisso')], string='Tipo', required=True),
                'sequence': osv.fields.integer('Sequence'),
                'value': osv.fields.float('Valore'),
                'account_id': osv.fields.many2one('account.invoice', string='Fattura'),
    }    
    _defaults={
               'sequence':0,
               'type': 'perc',
               'application': 'general',
    }
    
    def onchange_discount_name(self, cr, uid, ids, name, type, context=None):
        value = {}
        if name:
            disc_obj = self.pool.get('account.discount.type').browse(cr,uid,name)
            if not type:
                value['type'] = disc_obj.type
        return {'value':value}

class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    free = fields.Selection([('gift', 'Gift on Amount Total'),
                             ('base_gift', 'Gift on Amount Untaxed')])

    @api.onchange('free')
    def onchange_free(self):
        tax = self.env.user.company_id.homage_tax_id
        if tax:
            tax_ids = False
            if self.free:
                # ----- Keep the tax from company
                if tax:
                    tax_ids = [(6, 0, [tax.id])]
            self.invoice_line_tax_id = tax_ids
            
        homage_goods_account = self.env.user.company_id.homage_goods_account_id.id
        normal_goods_account = self.product_id.categ_id.property_account_income_categ.id
        if homage_goods_account and self.free:
            self.account_id = homage_goods_account
        elif normal_goods_account and not self.free:
            self.account_id = normal_goods_account

    @api.model
    def create(self,values):
        if 'free' in values and values['free']:
            company_id = self.pool.get('res.users').browse(self._cr, self._uid, self._uid, context=self._context).company_id
            if company_id.homage_goods_account_id:
                values.update({'account_id': company_id.homage_goods_account_id.id})
        return super(AccountInvoiceLine,self).create(values)

class account_invoice_with_discount(models.Model):

    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line.price_subtotal', 'invoice_line.free', 'tax_line.amount', 'global_discount_lines')
    def _compute_amount(self):
        cur_obj = self.pool.get('res.currency')
        cur = self.currency_id
        tax_lines = {}        

        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        self.amount_total = self.amount_untaxed + self.amount_tax  
        self.amount_untaxed_free = 0
        self.amount_tax_free = 0
        
        temporary_untaxed_value = 0.0
        temporary_global_discount_total = 0.0
        temporary_showed_global_discount_total = 0.0
        original_untaxed_value = 0.0
        original_total_value = 0.0
        original_tax_value = 0.0        

        for line in self.invoice_line:
            original_untaxed_value = 0.0
            original_total_value = 0.0
            original_tax_value = 0.0               
            temporary_untaxed_value += line.price_subtotal
            
            if line.free == 'gift':
                for tax in line.invoice_line_tax_id:
                    if tax.amount in tax_lines:
                        tax_lines[tax.amount] += line.price_subtotal
                    else:
                        tax_lines[tax.amount] = line.price_subtotal
                    
            if line.free not in ['gift', 'base_gift'] and (not line.product_id or (line.product_id and not line.product_id.no_discount)):  
                for tax in line.invoice_line_tax_id:
                     original_tax_value += line.price_subtotal * tax.amount                       
                original_untaxed_value = line.price_subtotal
                original_total_value = original_untaxed_value + original_tax_value
        
                for discount in self.global_discount_lines:

                   val = original_tax_value
                   val1 = original_untaxed_value
                   val2 = original_total_value
                            
                   if discount.type=='fisso':
                        temporary_global_discount_total += discount.value
                        temporary_showed_global_discount_total += discount.value
                        perc = discount.value / val1                
                   else:
                        perc = discount.value/100
        
                   sc = val*perc 
                   val -= sc
                   sc1 = val1*perc
                   val1 -= sc1
                                      
                   if discount.type=='perc':
                       temporary_global_discount_total += sc+sc1
                       temporary_showed_global_discount_total += sc1
                        
                   original_tax_value = cur_obj.round(self._cr, self._uid, cur, val)
                   original_untaxed_value = cur_obj.round(self._cr, self._uid, cur, val1)
                   original_total_value = original_tax_value + original_untaxed_value

        for tl in tax_lines:
            self.amount_tax_free += tax_lines[tl] * tl
                
        if self.amount_total:   
            if original_untaxed_value + temporary_showed_global_discount_total:
                self.global_discount_percentual = temporary_showed_global_discount_total/(original_untaxed_value + temporary_showed_global_discount_total)
        else:
            self.global_discount_percentual = 0.0
            
        self.showed_global_discount_total = temporary_showed_global_discount_total
        self.global_discount_total = temporary_global_discount_total
        self.amount_tax = self.amount_tax - self.amount_tax_free - (temporary_global_discount_total - temporary_showed_global_discount_total)
        self.amount_untaxed = temporary_untaxed_value - temporary_showed_global_discount_total - self.amount_untaxed_free
        self.amount_total = self.amount_tax + self.amount_untaxed
               
    #COLUMNS
    
    global_discount_lines = fields.One2many('account.invoice.discount', 'account_id', string='Sconti Globali')
    global_discount_total = fields.Float(string='Totale Sconti', digits=dp.get_precision('Account'), store=True, readonly=True, compute='_compute_amount')
    showed_global_discount_total = fields.Float(string='Totale Sconti', digits=dp.get_precision('Account'), store=True, readonly=True, compute='_compute_amount')    
    global_discount_percentual = fields.Float(string='Totale Sconti (%)', store=True, readonly=True, compute='_compute_amount')
    amount_untaxed = fields.Float(string='Subtotal', digits=dp.get_precision('Account'), store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_tax = fields.Float(string='Tax', digits=dp.get_precision('Account'), store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'), store=True, readonly=True, compute='_compute_amount')
    amount_untaxed_free = fields.Float(string='"For Free" Amount', digits=dp.get_precision('Account'), store=True, compute='_compute_amount')
    amount_tax_free = fields.Float(string='"For Free" Tax', digits=dp.get_precision('Account'), store=True, compute='_compute_amount')

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(account_invoice_with_discount, self).finalize_invoice_move_lines(move_lines)
        
        tax_obj = self.pool.get('account.tax')
        self._cr.execute('''SELECT inv.showed_global_discount_total, inv.global_discount_total, inv.amount_untaxed_free, inv.amount_tax_free, inv.amount_total, jour.type FROM account_invoice AS inv, account_journal AS jour WHERE inv.id = %s AND jour.id = inv.journal_id''',(self.id,))
        t = self._cr.fetchall()[0]
        showed_global_discount_total = t[0]
        global_discount_total = t[1]    
        amount_untaxed_free = t[2]
        amount_tax_free = t[3]        
        amount_total = t[4] 
        type = t[5]
        
        if showed_global_discount_total > 0.0:
            if not (self.env.user.company_id.discount_untaxed_account_id and
                    self.env.user.company_id.discount_tax_account_id):
                    raise Warning(_("No discount accounts defined for this company"))

        if amount_untaxed_free > 0.0:
            if not (self.env.user.company_id.homage_untaxed_account_id and
                    self.env.user.company_id.homage_tax_account_id):
                    raise Warning(_("No homage accounts defined for this company"))        
            
        if amount_untaxed_free > 0.0 or showed_global_discount_total > 0.0:
            # ricalcoliamo le scadenze
            ctx = {}
            for item in self._context.items():
                ctx[item[0]] = item[1]
            if self._name == 'account.invoice':
                ctx['invoice_id'] = self.id            
            
            totlines = self.with_context(ctx).payment_term.compute(amount_total, self.date_invoice)[0]

            dict = {}
            for tl in totlines:
                if tl[0] in dict:
                    dict[tl[0]] += tl[1]
                else:
                    dict[tl[0]] = tl[1]

            tax_code_id = None
            base_code_id = None

            for ml in move_lines:
                ml_maturity = ml[2]['date_maturity'] 
                if ml_maturity in dict:
                    if type in ['sale','purchase_refund']:
                        ml[2]['debit'] = dict[ml[2]['date_maturity']]
                    elif type in ['purchase','sale_refund']:
                        ml[2]['credit'] = dict[ml[2]['date_maturity']]
                
                if not tax_code_id:
                    if 'tax_code_id' in ml[2] and ml[2]['tax_code_id']:
                        tax_ids = tax_obj.search(self._cr,self._uid,[('tax_code_id','=',ml[2]['tax_code_id'])],self._context)
                        if tax_ids and len(tax_ids) and tax_ids[0]:
                            tax_code_id = ml[2]['tax_code_id']
                if not base_code_id:
                    if 'tax_code_id' in ml[2] and ml[2]['tax_code_id']:
                        tax_ids = tax_obj.search(self._cr,self._uid,[('base_code_id','=',ml[2]['tax_code_id'])],self._context)
                        if tax_ids and len(tax_ids) and tax_ids[0]:
                            base_code_id = ml[2]['tax_code_id']                                            

            # ----- Create line oly if debit is a valid value
            if amount_untaxed_free:
                # riga imponibile omaggio
                new_line = {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'analytic_lines': [],
                    'tax_amount': False,
                    'name': _('"For Free" Amount'),
                    'ref': '',
                    'currency_id': False,
                    #'debit': self.amount_untaxed_free,
                    'credit': type in ['purchase','sale_refund'] and amount_untaxed_free,
                    'product_id': False,
                    'date_maturity': False,
                    'debit': type in ['sale','purchase_refund'] and amount_untaxed_free,
                    'date': move_lines[0][2]['date'],
                    'amount_currency': 0,
                    'product_uom_id': False,
                    'quantity': 1,
                    'partner_id': move_lines[0][2]['partner_id'],
                    'account_id': (
                        self.env.user.company_id.homage_untaxed_account_id.id),
                }
                move_lines += [(0, 0, new_line)]
            # ----- Create line only if debit is a valid value
            if amount_tax_free:
                new_line = {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'analytic_lines': [],
                    'tax_amount': False,
                    'name': _('"For Free" Tax Amount'),
                    'ref': '',
                    'currency_id': False,
                    'credit': type in ['purchase','sale_refund'] and amount_tax_free,
                    'product_id': False,
                    'date_maturity': False,
                    'debit': type in ['sale','purchase_refund'] and amount_tax_free,
                    'date': move_lines[0][2]['date'],
                    'amount_currency': 0,
                    'product_uom_id': False,
                    'quantity': 1,
                    'partner_id': move_lines[0][2]['partner_id'],
                    'account_id': (
                        self.env.user.company_id.homage_tax_account_id.id),
                }
                move_lines += [(0, 0, new_line)]
            
            # ----- Create line oly if debit is a valid value
            if showed_global_discount_total:
                # riga imponibile omaggio
                new_line = {
                    'analytic_account_id': False,
                    'tax_code_id': base_code_id or False,
                    'analytic_lines': [],
                    'tax_amount': (type in ['sale','purchase_refund'] and -showed_global_discount_total) or (type in ['purchase','sale_refund'] and showed_global_discount_total),
                    'name': _('"Discount" Amount'),
                    'ref': '',
                    'currency_id': False,
                    'debit': type in ['sale','purchase_refund'] and showed_global_discount_total,
                    'product_id': False,
                    'date_maturity': False,
                    'credit': type in ['purchase','sale_refund'] and showed_global_discount_total,
                    'date': move_lines[0][2]['date'],
                    'amount_currency': 0,
                    'product_uom_id': False,
                    'quantity': 1,
                    'partner_id': move_lines[0][2]['partner_id'],
                    'account_id': (
                        self.env.user.company_id.discount_untaxed_account_id.id),
                }
                move_lines += [(0, 0, new_line)]
            # ----- Create line only if debit is a valid value
            if global_discount_total - showed_global_discount_total > 0.0:
                # riga iva omaggio
                new_line = {
                    'analytic_account_id': False,
                    'tax_code_id': tax_code_id or False,
                    'analytic_lines': [],
                    'tax_amount': (type in ['sale','purchase_refund'] and -(global_discount_total - showed_global_discount_total)) or (type in ['purchase','sale_refund'] and (global_discount_total - showed_global_discount_total)),
                    'name': _('"Discount" Tax Amount'),
                    'ref': '',
                    'currency_id': False,
                    'debit': type in ['sale','purchase_refund'] and (global_discount_total - showed_global_discount_total),
                    'product_id': False,
                    'date_maturity': False,
                    'credit': type in ['purchase','sale_refund'] and (global_discount_total - showed_global_discount_total),
                    'date': move_lines[0][2]['date'],
                    'amount_currency': 0,
                    'product_uom_id': False,
                    'quantity': 1,
                    'partner_id': move_lines[0][2]['partner_id'],
                    'account_id': (
                        self.env.user.company_id.discount_tax_account_id.id),
                }
                move_lines += [(0, 0, new_line)]
            
            tot_debit = 0.0
            tot_credit = 0.0
            for line in move_lines:
                if line[2]['credit'] and line[2]['credit'] > 0.0:
                    tot_credit += line[2]['credit']
                if line[2]['debit'] and line[2]['debit'] > 0.0:
                    tot_debit += line[2]['debit']
            if abs(round(tot_debit-tot_credit,2)) <= 0.01 and abs(round(tot_debit-tot_credit,2)) > 0.0:
                prv = abs(round(tot_debit-tot_credit,2))
                if tot_debit > tot_credit:
                    if showed_global_discount_total and global_discount_total - showed_global_discount_total > 0.0:
                        if move_lines[-2][2]['debit']:
                            move_lines[-2][2].update({'debit': move_lines[-2][2]['debit'] - round(tot_debit-tot_credit,2)})
                        elif move_lines[-2][2]['credit']:
                            move_lines[-2][2].update({'credit': move_lines[-2][2]['credit'] + round(tot_debit-tot_credit,2)})                            
                    else:
                        if move_lines[-1][2]['debit']:
                            move_lines[-1][2].update({'debit': move_lines[-1][2]['debit'] - round(tot_debit-tot_credit,2)})
                        elif move_lines[-1][2]['credit']:
                            move_lines[-1][2].update({'credit': move_lines[-1][2]['credit'] + round(tot_debit-tot_credit,2)})                            
                else:
                    if showed_global_discount_total and global_discount_total - showed_global_discount_total > 0.0:
                        if move_lines[-2][2]['debit']:
                            move_lines[-2][2].update({'debit': move_lines[-2][2]['debit'] + round(tot_credit - tot_debit,2)})
                        elif move_lines[-2][2]['credit']:
                            move_lines[-2][2].update({'credit': move_lines[-2][2]['credit'] - round(tot_credit - tot_debit,2)})                            
                    else:
                        if move_lines[-1][2]['debit']:
                            move_lines[-1][2].update({'debit': move_lines[-1][2]['debit'] + round(tot_credit - tot_debit,2)})    
                        elif move_lines[-1][2]['credit']:      
                            move_lines[-1][2].update({'credit': move_lines[-1][2]['credit'] - round(tot_credit - tot_debit,2)})    

        return move_lines
        
class account_invoice_tax_with_discount(models.Model):

    _inherit = "account.invoice.tax"
    
    @api.one
    @api.depends('base', 'amount', 'invoice_id.global_discount_percentual')
    def _compute_displayed_values(self):
        self.displayed_base = self.base #* (1 - self.invoice_id.global_discount_percentual)
        self.displayed_amount = self.amount #* (1 - self.invoice_id.global_discount_percentual)
        
        tmp_amount = 0.0
        tmp_base = 0.0
        
        for line in self.invoice_id.invoice_line:
            for tax_id in line.invoice_line_tax_id:
                if line.invoice_line_tax_id and self.tax_code_id == tax_id.tax_code_id:
                    if line.free == 'gift' and self.base:
                        self.displayed_base -= line.price_subtotal
                        self.displayed_amount -= line.price_subtotal * (self.amount / self.base)
                    if line.free == 'base_gift':
                        self.displayed_base -= line.price_subtotal
                    if line.free not in ['gift','base_gift'] and self.base:         
                        tmp_discount_value = 0.0
                        
                        val1 = line.price_subtotal
                        for discount in self.invoice_id.global_discount_lines:    
                            
                                    
                           if discount.type== 'fisso' and val1 != 0:
                                tmp_discount_value += discount.value
                                perc = discount.value / val1                
                           else:
                                perc = discount.value/100
                
                           sc1 = val1*perc
                           val1 -= sc1                                                                
                           
                           tmp_base += sc1
                           tmp_amount += line.price_subtotal * (self.amount / self.base) - (line.price_subtotal-sc1) * (self.amount / self.base)
                           
        self.displayed_base -= tmp_base
        self.displayed_amount -= tmp_amount     
                
        None

    displayed_base = fields.Float(string='Base', store=True, readonly=True, digits=dp.get_precision('Account'), compute='_compute_displayed_values')
    displayed_amount = fields.Float(string='Amount', store=True, readonly=True, digits=dp.get_precision('Account'), compute='_compute_displayed_values')