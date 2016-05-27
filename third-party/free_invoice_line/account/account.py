# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by
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


from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning

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

class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        self.amount_total = self.amount_untaxed + self.amount_tax      
        tax_lines = {}
        #self.amount_untaxed = 0
        #self.amount_tax = 0
        self.amount_untaxed_free = 0
        self.amount_tax_free = 0
        for line in self.invoice_line:
            #self.amount_untaxed += line.price_subtotal
            if line.free in ['gift', 'base_gift']:
                self.amount_untaxed_free += line.price_subtotal
                if line.free == 'gift':
                    for tax in line.invoice_line_tax_id:
                        if tax.amount in tax_lines:
                            tax_lines[tax.amount] += line.price_subtotal
                        else:
                            tax_lines[tax.amount] = line.price_subtotal
        for tl in tax_lines:
            self.amount_tax_free += tax_lines[tl] * tl
        self.amount_untaxed -= self.amount_untaxed_free
        self.amount_tax = self.amount_tax - self.amount_tax_free
        self.amount_total = self.amount_untaxed + self.amount_tax

    amount_untaxed = fields.Float(
        string='Subtotal', digits=dp.get_precision('Account'), store=True,
        readonly=True, compute='_compute_amount', track_visibility='always')
    amount_tax = fields.Float(
        string='Tax', digits=dp.get_precision('Account'), store=True,
        readonly=True, compute='_compute_amount')
    amount_total = fields.Float(
        string='Total', digits=dp.get_precision('Account'), store=True,
        readonly=True, compute='_compute_amount')
    amount_untaxed_free = fields.Float(
        string='"For Free" Amount', digits=dp.get_precision('Account'),
        store=True, compute='_compute_amount')

    amount_tax_free = fields.Float(
        string='"For Free" Tax', digits=dp.get_precision('Account'),
        store=True, compute='_compute_amount')

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)        
        self._cr.execute('''SELECT inv.amount_untaxed_free, inv.amount_tax_free, inv.amount_total, jour.type FROM account_invoice AS inv, account_journal AS jour WHERE inv.id = %s AND inv.journal_id = jour.id''',(self.id,))
        t = self._cr.fetchall()[0]
        amount_untaxed_free = t[0]
        amount_tax_free = t[1]
        amount_total = t[2]
        type = t[3]
        
        if amount_untaxed_free > 0.0:
        
            '''
            PER QUALCHE ARCANA RAGIONE self.amount_untaxed_free NON E' ACCESSIBILE TRAMITE ORM IN NESSUN MODO
            '''
            
        #if self.amount_untaxed_free > 0.0:
            if not (self.env.user.company_id.homage_untaxed_account_id and
                    self.env.user.company_id.homage_tax_account_id):
                    raise Warning(
                        _("No homage accounts defined for this company"))

            # ricalcoliamo le scadenze

            ctx = {}
            for item in self._context.items():
                ctx[item[0]] = item[1]
            if self._name == 'account.invoice':
                ctx['invoice_id'] = self.id               
            
            try:
                totlines = self.with_context(ctx).payment_term.compute(amount_total, self.date_invoice)[0]
            except: 
                raise Warning(_("Exception Occurred: It's possible payment terms are not correctly setted."))                                

            dict = {}
            for tl in totlines:
                if tl[0] in dict:
                    dict[tl[0]] += tl[1]
                else:
                    dict[tl[0]] = tl[1]

            for ml in move_lines:
                if ml[2]['date_maturity'] in dict:
                    if type in ['sale','purchase_refund']:
                        ml[2]['debit'] = dict[ml[2]['date_maturity']]
                    elif type in ['purchase','sale_refund']:
                        ml[2]['credit'] = dict[ml[2]['date_maturity']]
                        
            # ----- Create line oly if debit is a valid value
            #if self.amount_untaxed_free:
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
                # riga iva omaggio
                # if precision_diff > 0.0:
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
        return move_lines
