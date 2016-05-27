# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Giuseppe D'Alò (<g.dalo@apuliasoftware.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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


from openerp.osv import orm, fields
from openerp import api
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from math import fabs
from openerp.exceptions import Warning
from datetime import datetime, timedelta


class account_vat_period_end_statement(orm.Model):

    _inherit = 'account.vat.period.end.statement'

    def _compute_authority_vat_amount(self, cr, uid, ids, field_name, arg,
                                      context):
        res = {}
        for i in ids:
            res[i] = {
                'authority_vat_amount': 0.0,
                'authority_vat_amount_net': 0.0,
                }
            statement = self.browse(cr, uid, i)
            debit_vat_amount = 0.0
            credit_vat_amount = 0.0
            generic_vat_amount = 0.0
            for debit_line in statement.debit_vat_account_line_ids:
                if not debit_line.tax_code_id.xcash_vat:
                    debit_vat_amount += debit_line.amount
            for credit_line in statement.credit_vat_account_line_ids:
                if not credit_line.tax_code_id.xcash_vat:
                    credit_vat_amount += credit_line.amount
            for generic_line in statement.generic_vat_account_line_ids:
                if not generic_line.tax_code_id.xcash_vat:
                    generic_vat_amount += generic_line.amount
            # check if company has quarterly vat
            company = self.pool['res.users'].browse(
                cr, uid, uid, context).company_id
            authority_amount = (
                debit_vat_amount - credit_vat_amount - generic_vat_amount -
                statement.previous_credit_vat_amount +
                statement.previous_debit_vat_amount)
            res[i]['authority_vat_amount'] = (
                authority_amount * (company.of_account_end_vat_statement_interest and (
                    (100 + company.of_account_end_vat_statement_interest_percent) / 100.00) or 1.0))
            res[i]['authority_vat_amount_net'] = authority_amount
        return res

    def _compute_payable_vat_amount(self, cr, uid, ids, field_name, arg,
                                    context):
        res = {}
        for i in ids:
            statement = self.browse(cr, uid, i)
            debit_vat_amount = 0.0
            for debit_line in statement.debit_vat_account_line_ids:
                if not debit_line.tax_code_id.xcash_vat:
                    debit_vat_amount += debit_line.amount
            res[i] = debit_vat_amount
        return res

    def _compute_deductible_vat_amount(self, cr, uid, ids, field_name, arg,
                                       context):
        res = {}
        for i in ids:
            statement = self.browse(cr, uid, i)
            credit_vat_amount = 0.0
            for credit_line in statement.credit_vat_account_line_ids:
                if not credit_line.tax_code_id.xcash_vat:
                    credit_vat_amount += credit_line.amount
            res[i] = credit_vat_amount
        return res

    _columns = {
        'authority_vat_amount': fields.function(
            _compute_authority_vat_amount,
            multi='sums',
            string='Authority VAT Amount'),
        'authority_vat_amount_net': fields.function(
            _compute_authority_vat_amount,
            multi='sums',
            string='Authority VAT Amount no interests'),
        'payable_vat_amount': fields.function(
            _compute_payable_vat_amount,
            method=True,
            string='Payable VAT Amount'),
        'deductible_vat_amount': fields.function(
            _compute_deductible_vat_amount,
            method=True,
            string='Deductible VAT Amount'),
        }

    def compute_amounts(self, cr, uid, ids, context=None):
        self.check_matured_invoice(cr, uid, ids, context)
        res = super(account_vat_period_end_statement, self).compute_amounts(
            cr, uid, ids, context)
        return res

    def check_matured_invoice(self, cr, uid, ids, context={}):
        invoice_obj = self.pool['account.invoice']
        period_obj = self.pool['account.period']
        company = self.pool['res.users'].browse(cr, uid, uid).company_id
        #period_ids = self.browse(cr, uid, ids[0]).period_ids
        old_periods = []
        for period in self.browse(cr, uid, ids[0]).period_ids:
            data_sca = datetime.strptime(period.date_start, '%Y-%m-%d')
            date_test = data_sca + relativedelta(years=-1)            
            periodo = period_obj.find(cr, uid, date_test)
            if periodo:
                old_periods.append(periodo[0])
        # ha definito il range  della liquidazione
        # ora cerchiamo le fatture di un anno indietro
        if company:
            # prepara la query per trovare tutte le fatture che rientrano
            #nel periodo
            cerca = []
            cerca.append(('period_id', 'in', old_periods))
            cerca.append(('company_id', '=', company.id))
            cerca.append(('state', 'in', ['open','paid']))
            cerca.append(('journal_id', 'in',
            [company.journal_purch_xcash_id.id,
                company.journal_sale_xcash_id.id]))
            cerca.append(('amount_tax_remain', '>', 0.1))
            invoice_ids = invoice_obj.search(cr, uid, cerca)
            if invoice_ids:
                #ci sono fatture che andrebbero stornate
                self.action_move_line_x_cash(cr, uid, ids, invoice_ids)
        return True

    def action_move_line_x_cash(self, cr, uid, ids, invoice_ids, data_reg=False, context={}):
        invoice_obj = self.pool['account.invoice']
        period_obj = self.pool['account.period']
        move_obj = self.pool['account.move']
        move_line_obj = self.pool['account.move.line']
        seq_obj = self.pool['ir.sequence']
        fpos_obj = self.pool['account.fiscal.position']
        link_account_obj = self.pool['xcash.link.account']
        company = self.pool['res.users'].browse(cr, uid, uid).company_id
        move_id = False
        for invoice in invoice_obj.browse(cr, uid, invoice_ids, context):
            if invoice.amount_tax_remain:
                if invoice.type in ['out_invoice', 'out_refund']:
                    journal = company.journal_sale_xcash_matured_id
                else:
                    journal = company.journal_purch_xcash_matured_id
                if not invoice.fiscal_position:
                    continue
                if not invoice.fiscal_position.xcash_vat:
                    continue
                vat_x_cash = invoice.amount_tax_remain
                name = seq_obj.next_by_id(
                    cr, uid, journal.sequence_id.id, context)
                ref = ''
                if invoice.number:
                    ref = invoice.number
                # calcola data e periodo di riferimento
                data_sca = datetime.strptime(invoice.registration_date, '%Y-%m-%d')
                date_test = data_sca + relativedelta(years=+1)            
                if not data_reg:                
                    periodo = period_obj.find(cr, uid, date_test)                
                else:
                    periodo = period_obj.find(cr, uid, data_reg)                
                if periodo:
                    if not data_reg:
                        data_reg = period_obj.browse(cr,uid,periodo[0]).date_stop
                    move_id = move_obj.create(
                        cr, uid,
                        {'name': name,
                         'journal_id': journal.id,
                         'narration': 'storno iva x cassa Scadenza Termini',
                         'date': data_reg,
                         'ref': ref,
                         'period_id': periodo[0]})
                    # now create the line of move
                    # get the correct value from fiscal position
                    fpos = fpos_obj.browse(cr, uid, invoice.fiscal_position.id,
                                           context)
                    accounts = self._get_line_by_value(cr, uid, fpos, invoice,
                                                       vat_x_cash, context)
                    # registrazione di un incasso con iva in sospensione
                    if invoice.type in ['out_invoice', 'in_refund']:
                        move_line_obj.create(
                            cr, uid, {
                                'name': 'storno iva x cassa Scadenza Termini',
                                'debit': vat_x_cash ,
                                'partner_id': invoice.partner_id.id,
                                'account_id': accounts['account_id'],
                                'tax_code_id': accounts['tax_code_id'],
                                'tax_amount': vat_x_cash * -1,
                                'move_id': move_id,
                                # 'vat_x_cash_invoice_id': invoice.id,
                                # 'matured_move': True,
                                }, context)

                        account_id = link_account_obj._get_related_account(
                          cr, uid, accounts['account_id'], company.id, context)
                        move_line_obj.create(
                            cr, uid, {
                                'name': 'storno iva x cassa Scadenza Termini',
                                'credit': vat_x_cash,
                                'tax_amount': vat_x_cash,
                                'partner_id': invoice.partner_id.id,
                                'account_id': account_id,
                                'tax_code_id': accounts['rev_tax_code_id'],
                                'move_id': move_id,
                                'vat_x_cash_invoice_id': invoice.id,
                                'matured_move': True,
                                }, context)
                    # registrazione di un pagamento con iva in sospensione
                    if invoice.type in ['in_invoice', 'out_refund']:
                        move_line_obj.create(
                            cr, uid, {
                                'name': 'storno iva x cassa Scadenza Termini',
                                'credit': vat_x_cash,
                                'tax_amount': vat_x_cash ,
                                'partner_id': invoice.partner_id.id,
                                'account_id': accounts['account_id'],
                                'tax_code_id': accounts['tax_code_id'],
                                'move_id': move_id,
                                # 'vat_x_cash_invoice_id': invoice.id,
                                # 'matured_move': True,
                                }, context)

                        account_id = link_account_obj._get_related_account(
                          cr, uid, accounts['account_id'], company.id, context)
                        move_line_obj.create(
                            cr, uid, {
                                'name': 'storno iva x cassa Scadenza Termini',
                                'debit': vat_x_cash ,
                                'tax_amount': vat_x_cash * -1,
                                'partner_id': invoice.partner_id.id,
                                'account_id': account_id,
                                'tax_code_id': accounts['rev_tax_code_id'],
                                'move_id': move_id,
                                'vat_x_cash_invoice_id': invoice.id,
                                'matured_move': True,
                                }, context)
                    # now validate the move
                    move_obj.post(cr, uid, [move_id], context)
        return move_id

    def _get_line_by_value(self, cr, uid, fpos, invoice, amount, context={}):
        if not invoice or not amount or not fpos:
            return False
        res = {}
        for tax_line in invoice.tax_line:
            if amount <= fabs(tax_line.tax_amount):
                rev_tax_code_id = tax_line.tax_code_id.xcash_tax_code.id
                res = {'account_id': tax_line.account_id.id,
                       'tax_code_id': tax_line.tax_code_id.id,
                       'rev_tax_code_id': rev_tax_code_id}
            else:
                continue
        if not res:
            raise Warning(_('Importo del pagamento errato!'))
        return res
