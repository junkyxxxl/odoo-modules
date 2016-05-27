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
from openerp.tools.translate import _
from openerp.osv.orm import browse_record


class account_voucher_makeover(orm.Model):
    _inherit = 'account.voucher'

    def _default_accepted_lines(self, cr, uid, context):
        t_partner_id = context.get('partner_id', None)
        t_filter = []
        if(t_partner_id):
            t_filter = ['&',
                        ('partner_id', '=', t_partner_id),
                        ('is_selected', '=', 'accepted')]
        else:
            t_filter = [('is_selected', '=', 'accepted')]
        move_line_obj = self.pool.get('account.move.line')
        move_line_ids = move_line_obj.search(cr,
                                             uid,
                                             t_filter,
                                             context=context)
        return move_line_ids

    def _get_account(self, cr, uid, ids, partner_id, journal_id, context=None):
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
       
        journal = journal_pool.browse(cr,
                                      uid,
                                      journal_id,
                                      context=context)
        partner = partner_pool.browse(cr,
                                      uid,
                                      partner_id,
                                      context=context)
        account_id = False
        if journal.type in ('sale', 'sale_refund'):
            account_id = partner.property_account_receivable.id
        elif journal.type in ('purchase', 'purchase_refund', 'expense'):
            account_id = partner.property_account_payable.id
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        return account_id

    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        move_line = {}
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        
        if voucher.tax_id and voucher.tax_id.price_include:
            return move_line
        return super(account_voucher_makeover,self).writeoff_move_line_get(cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context= context)

    def action_move_line_create(self, cr, uid, ids, context=None):
        inv_pool = self.pool.get('account.invoice')
        move_pool = self.pool.get('account.move')
        curr_pool = self.pool.get('res.currency')
        term_pool = self.pool.get('account.payment.term')

        for voucher in self.browse(cr, uid, ids, context):
            if (not voucher.period_id):
                raise orm.except_orm(_('Error!'),
                                     _('Non è stato definito alcun periodo!'))

            if (not voucher.period_id.fiscalyear_id):
                raise orm.except_orm(_('Error!'),
                                     _('Non è stato definito alcun anno fiscale per il periodo selezionato!'))

        res = super(account_voucher_makeover, self).action_move_line_create(cr,
                                                    uid, ids, context)
        for voucher in self.browse(cr, uid, ids, context):
            
            for move_line in voucher.move_ids:
                self.pool.get('account.move').write(cr,uid,move_line.move_id.id,{'date':voucher.date})
                self.pool.get('account.move.line').write(cr,uid,move_line.id,{'date_created':voucher.date}, check=False, update_check=False)

            if (not self.wht_already_reconciled(cr, uid, voucher, context)):
                inv_amounts = self._get_amounts_grouped_by_invoice(cr, uid,
                                                    voucher, context)
                for inv_id in inv_amounts:
                    invoice = inv_pool.browse(cr, uid, inv_id, context)
                    if invoice.wht_amount:
                        if(invoice.partner_id.property_account_payable.id == invoice.partner_id.wht_account_id.account_id.id):
                            raise orm.except_orm(_('Error!'), _('Il conto per la ritenuta di acconto è lo stesso di quello del partner'))
                        self._check_constraints(voucher, invoice)

                        # compute the new amount
                        currency_id = voucher.company_id.currency_id
                        t_wht_amount = inv_amounts[invoice.id]['wht-tax']
                        new_line_amount = curr_pool.round(cr, uid,
                                                currency_id,
                                                t_wht_amount)

                        # compute the due date
                        t_wht_account = invoice.partner_id.wht_account_id
                        t_wht_payment_term = t_wht_account.wht_payment_term
                        due_list = term_pool.compute(
                            cr, uid, t_wht_payment_term.id, new_line_amount,
                            date_ref=voucher.date or invoice.date_invoice,
                            context=context)
                        self._check_computed_due_list(t_wht_payment_term.name,
                                                      due_list)

                        t_new_name = _('Payable withholding - ') + \
                                        invoice.number
                        new_move = {
                            'journal_id': t_wht_account.wht_journal_id.id,
                            'partner_id': invoice.partner_id.id,
                            'line_id': [
                                (0, 0, {
                                    'name': invoice.number,
                                    'partner_id': invoice.partner_id.id,
                                    'account_id': invoice.account_id.id,
                                    'debit': new_line_amount,
                                    'credit': 0.0,
                                    'state': 'valid',
                                    }),
                                (0, 0, {
                                    'name': t_new_name,
                                    'partner_id': invoice.partner_id.id,
                                    'account_id': t_wht_account.account_id.id,
                                    'debit': 0.0,
                                    'credit': new_line_amount,
                                    'date_maturity': due_list[0][0],
                                    'wht_state': 'confirmed',
                                    'state': 'valid',
                                    }),
                                ]
                            }
                        move_id = move_pool.create(cr,
                                                   uid,
                                                   new_move,
                                                   context=context)
                        t_move_data = move_pool.browse(cr, uid, move_id, context)
                        self.reconcile_withholding_move(cr,
                                                        uid,
                                                        invoice,
                                                        t_move_data,
                                                        context)
                        voucher.write({'wht_move_ids': [(4, move_id)]})
        return res

    def get_company(self, cr, uid, context=None):
        user_pool = self.pool.get('res.users')
        company_pool = self.pool.get('res.company')
        user = user_pool.browse(cr, uid, uid, context=context)
        company_id = user.company_id
        if not company_id:
            company_id = company_pool.search(cr, uid, [])
        return company_id and company_id.id or False

    def _get_amount_supplier(self, cr, uid, wizard_line_ids):
        t_amount = 0.0
        wizard_line_obj = self.pool.get('wizard.confirm.payment.line')
        for t_wizard_line_data in wizard_line_obj.browse(cr, uid, wizard_line_ids):
            t_move_line = t_wizard_line_data.move_line_id
            if (t_move_line.credit > 0):
                t_amount = t_amount + t_wizard_line_data.amount_partial
            else:
                t_amount = t_amount - t_wizard_line_data.amount_partial
        
        return t_amount

    def _get_amount_customer(self, cr, uid, wizard_line_ids):
        t_amount = 0.0
        wizard_line_obj = self.pool.get('wizard.confirm.customer.payment.line')
        for t_wizard_line_data in wizard_line_obj.browse(cr, uid, wizard_line_ids):
            t_move_line = t_wizard_line_data.move_line_id
            if (t_move_line.debit > 0):
                t_amount = t_amount + t_wizard_line_data.amount_partial
            else:
                t_amount = t_amount - t_wizard_line_data.amount_partial
        
        return t_amount

    def _get_journal_id(self, cr, uid, t_bank_id):
        bank_obj = self.pool.get('res.partner.bank')
        t_bank = bank_obj.browse(cr, uid, t_bank_id)
        if (not t_bank or
            not t_bank.journal_id):
            raise orm.except_orm(_('Error!'), 
                _('Please define a journal for the bank "%s".') % (t_bank.bank_name))

        return t_bank.journal_id.id

    def _get_account_id(self, cr, uid, t_journal_id):
        journal_obj = self.pool.get('account.journal')
        t_journal = journal_obj.browse(cr, uid, t_journal_id)
        if (not t_journal or
            not t_journal.default_credit_account_id or 
            not t_journal.default_debit_account_id):
            raise orm.except_orm(_('Error!'), 
                _('Please define default credit/debit accounts on the journal "%s".') % (t_journal.name))
        t_cr_id = t_journal.default_credit_account_id.id
        t_dr_id = t_journal.default_debit_account_id.id
        t_account_id = t_cr_id or t_dr_id
        return t_account_id

    def _set_move_lines_valid(self, cr, uid, context, partner_type, t_wizard, t_partner_id):
        move_line_obj = self.pool.get('account.move.line')
        wizard_line_obj = self.pool.get('wizard.confirm.payment.line')
        if partner_type == 'customer_id':
            wizard_line_obj = self.pool.get('wizard.confirm.customer.payment.line')
        move_line_ids = []
        w_move_line_ids = wizard_line_obj.search(cr, uid, 
                                ['&', '&', 
                                 ('partner_id', '=', t_partner_id), 
                                 ('confirm_payment_id', '=', t_wizard), 
                                 ('is_selected', '=', 'accepted')], 
                                context=context)
        if w_move_line_ids:
            t_wizard_line_data = wizard_line_obj.browse(cr, uid, w_move_line_ids)
            for t_wizard_line in t_wizard_line_data:
                t_move_line_id = t_wizard_line.move_line_id.id
                if t_move_line_id not in move_line_ids:
                    move_line_ids.append(t_move_line_id)

        move_line_obj.write(cr, uid, move_line_ids, {'state':'valid'})

    def _create_supplier_voucher(self, cr, uid, ids, context=None):

        invoice_obj =           self.pool.get('account.invoice')
        move_line_obj =         self.pool.get('account.move.line')
        wizard_line_obj =       self.pool.get('wizard.confirm.payment.line')

        context_partner_id =    context.get('partner_id', None)
        t_date_op =             context.get('operation_date', None)
        t_currency_date =       context.get('currency_date', None)
        t_bank =                context.get('bank_id', None)
        t_period =              context.get('period_id', None)
        t_wizard =              context.get('wizard_id', None)

        t_journal_id = self._get_journal_id(cr, uid, t_bank)
        t_account_id = self._get_account_id(cr, uid, t_journal_id)

        list_partner = []

        if context_partner_id:
            list_partner = [context_partner_id]

        if not context_partner_id:
            selected_line_ids = wizard_line_obj.search(cr,
                                                     uid,
                                                     ['&',
                                                      ('is_selected', '=', 'accepted'),
                                                      ('confirm_payment_id', '=', t_wizard)],
                                                     context=context)

            if selected_line_ids:
                t_wizard_line_data = wizard_line_obj.browse(cr, uid, selected_line_ids)
                for t_wizard_line in t_wizard_line_data:
                    t_partner_id = None
                    if t_wizard_line.partner_id:
                        t_partner_id = t_wizard_line.partner_id.id
                    if t_partner_id not in list_partner:
                        list_partner.append(t_partner_id)

        for t_partner_inlist_id in list_partner:

            self._set_move_lines_valid(cr,
                                       uid,
                                       context,
                                       'supplier_id',
                                       t_wizard,
                                       t_partner_inlist_id)

            partner_bank_ids = []
            selected_partner_line_ids = wizard_line_obj.search(cr,
                                                     uid,
                                                     ['&', '&',
                                                      ('is_selected', '=', 'accepted'),
                                                      ('partner_id', '=', t_partner_inlist_id),
                                                      ('confirm_payment_id', '=', t_wizard)],
                                                     context=context)

            if selected_partner_line_ids:
                t_wizard_line_data = wizard_line_obj.browse(cr, uid, selected_partner_line_ids)
                for t_wizard_line in t_wizard_line_data:
                    t_partner_bank_id = None
                    if t_wizard_line.partner_bank_id:
                        t_partner_bank_id = t_wizard_line.partner_bank_id.id
                    else:
                        if t_wizard_line.payment_type == 'B':
#                           # FIXME in tal caso la banca dovrebbe essere ricavata dalla fattura ?
                            raise orm.except_orm(_('Error!'),
                                _('Per il pagamento tramite bonifico con ID %s non è stata definita alcuna banca di appoggio.') % (t_wizard_line.id))
                    if t_partner_bank_id not in partner_bank_ids:
                        partner_bank_ids.append(t_partner_bank_id)

            for t_partner_bank_id in partner_bank_ids:

                wizard_line_ids = wizard_line_obj.search(cr,
                                                        uid,
                                                        ['&',
                                                         ('partner_id', '=', t_partner_inlist_id),
                                                         ('is_selected', '=', 'accepted'),
                                                         ('confirm_payment_id', '=', t_wizard),
                                                         ('partner_bank_id', '=', t_partner_bank_id)],
                                                        context=context)

                if wizard_line_ids:
                    t_amount = self._get_amount_supplier(cr, uid, wizard_line_ids)

                    vals = {}
                    vals['amount'] = t_amount
                    vals['account_id'] = t_account_id
                    vals['partner_id'] = t_partner_inlist_id
                    vals['comment'] = 'Write_off'
                    vals['type'] = 'payment'
                    vals['is_multi_currency'] = False
                    vals['pay_now'] = 'pay_now'
                    vals['company_id'] = self.get_company(cr, uid, context)
                    vals['state'] = 'posted'
                    vals['pre_line'] = False

                    # FIXME ???
                    vals['payment_rate'] = 1

                    vals['payment_option'] = 'without_writeoff'
                    vals['active'] = True
                    vals['journal_id'] = t_journal_id
                    vals['operation_date'] = t_date_op
                    vals['date'] = t_date_op
                    vals['document_date'] = t_date_op
                    vals['currency_date'] = t_currency_date

                    vals['bank_id'] = t_bank
                    # FIXME evitare a priori che t_bank sia di tipo browse_record
                    if isinstance(t_bank, browse_record):
                        vals['bank_id'] = t_bank.id

                    vals['partner_bank_id'] = t_partner_bank_id
                    vals['period_id'] = t_period
                    vals['document_number'] = None
                    vals['tax_id'] = None
                    vals['tax_amount'] = None
                    vals['name'] = None
                    vals['analytic_id'] = None
                    vals['reference'] = None
                    vals['writeoff_acc_id'] = None
                    vals['narration'] = None
                    vals['date_due'] = None

                    res = self.create(cr, uid, vals, context=None)
                    t_res = int(res)

                    t_lines = []

                    for line_id in wizard_line_obj.browse(cr, uid, wizard_line_ids):
                        t_wht_lines = []

                        t_move_line = line_id.move_line_id
                        t_company_data = t_move_line.move_id.company_id
                        t_bonus_active_account_id = t_company_data.bonus_active_account_id.id
                        t_bonus_passive_account_id = t_company_data.bonus_passive_account_id.id

                        move_line_obj.write(cr,
                                            uid,
                                            [t_move_line.id],
                                            {'payment_type': line_id.payment_type,
                                             'is_selected': None
                                             })
                        t_type = 'cr'
                        if(t_move_line.credit > 0):
                            t_type = 'dr'

                        if(line_id.allowance == True):
                            t_invoice_ids = invoice_obj.search(cr, uid,
                                                               [('move_id', '=', t_move_line.move_id.id)])
                            if not t_invoice_ids:
                                raise orm.except_orm(_('Error!'),
                                                     _('Nessuna fattura per la movimentazione') % (t_move_line.move_id.id))
                            t_invoice_id = t_invoice_ids[0]
                            t_invoice = invoice_obj.browse(cr, uid, t_invoice_id)
                            if((line_id.amount_allowance > 0.0 and t_invoice.type=='in_invoice') or (line_id.amount_allowance < 0.0 and t_invoice.type=='in_refund')):
                                t_account_allowance = t_bonus_active_account_id
                                t_allowance_type = 'cr'
                                t_allowance_amount = line_id.amount_allowance
                                if(t_invoice.type=='in_refund'):
                                    t_allowance_amount = -line_id.amount_allowance
                            else:
                                t_account_allowance = t_bonus_passive_account_id
                                t_allowance_type = 'dr'
                                t_allowance_amount = -line_id.amount_allowance
                                if(t_invoice.type=='in_refund'):
                                    t_allowance_amount = line_id.amount_allowance
                            t_lines.append((0, 0, {
                                                'name': t_move_line.ref,
                                                'voucher_id': t_res,
                                                'account_id': t_move_line.account_id.id,
                                                'move_line_id': t_move_line.id,
                                                'type': t_type,
                                                'amount': line_id.amount_partial + line_id.amount_allowance,
                                                'amount_original': (t_move_line.debit or t_move_line.credit),
                                                'amount_unreconciled': line_id.amount_partial - (t_move_line.debit or t_move_line.credit)
                                                 }))
                            t_lines.append((0, 0, {
                                                'name': t_move_line.ref,
                                                'voucher_id': t_res,
                                                'account_id': t_account_allowance,
                                                'move_line_id': None,
                                                'type': t_allowance_type,
                                                'amount': t_allowance_amount,
                                                'amount_original': line_id.amount_allowance,
                                                'amount_unreconciled': 0.0,
                                                 }))
                        else:
                            t_lines.append((0, 0, {
                                                'name': t_move_line.ref,
                                                'voucher_id': t_res,
                                                'account_id': t_move_line.account_id.id,
                                                'move_line_id': t_move_line.id,
                                                'type': t_type,
                                                'amount': line_id.amount_partial,
                                                'amount_original': (t_move_line.debit or t_move_line.credit),
                                                'amount_unreconciled': line_id.amount_partial - (t_move_line.debit or t_move_line.credit)
                                                 }))
                        wht_lines = move_line_obj.search(cr, uid,
                                                         [('move_id', '=', t_move_line.move_id.id),
                                                          ('is_wht', '=', True),
                                                          ('reconcile_id', '=', False)])
                        for wht_id in move_line_obj.browse(cr, uid, wht_lines):
                            t_wht_lines = []
                            twht_type = 'cr'
                            if(wht_id.credit > 0):
                                twht_type = 'dr'

                            t_wht_lines.append((0, 0, {
                                                 'name': wht_id.name,
                                                 'voucher_id': t_res,
                                                 'account_id': wht_id.account_id.id,
                                                 'move_line_id': wht_id.id,
                                                 'type': twht_type,
                                                 'amount': 0.0,
                                                 'amount_original': (t_move_line.debit or t_move_line.credit),
                                                 'reconcile': False,
                                                  }))
                        self.write(cr, uid, [t_res], {'line_ids': t_wht_lines})
                    self.write(cr, uid, [t_res], {'line_dr_ids': t_lines})

        return True

    def create_wht_voucher(self, cr, uid, ids, context=None):

        journal_obj =     self.pool.get('account.journal')
        move_line_obj =   self.pool.get('account.move.line')
        wizard_line_obj = self.pool.get('wizard.confirm.payment.wht.line')

        t_date_op = context.get('operation_date', None)
        t_currency_date = context.get('currency_date', None)
        t_bank = context.get('bank_id', None)
        t_period = context.get('period_id', None)
        t_wizard = context.get('wizard_id', None)

        t_journal_id = self._get_journal_id(cr, uid, t_bank)
        t_journal = journal_obj.browse(cr, uid, t_journal_id)
        if (not t_journal
               or not t_journal.default_credit_account_id.id
               or not t_journal.default_debit_account_id.id):
            raise orm.except_orm(_('Error!'),
                                _('Please define default credit/debit accounts on the journal "%s".') % (t_journal.name))

        t_account_id = self._get_account_id(cr, uid, t_journal_id)

        account_move_line_ids = []

        wizard_line_ids = wizard_line_obj.search(cr,
                                                 uid,
                                                 ['&',
                                                  ('state', '=', 'selected'),
                                                  ('confirm_payment_wht_id', '=', t_wizard)],
                                                 context=context)

        if wizard_line_ids:
            t_wizard_line_data = wizard_line_obj.browse(cr, uid, wizard_line_ids)
            for t_wizard_line in t_wizard_line_data:
                t_line_id = t_wizard_line.move_line_id.id
                if t_line_id not in account_move_line_ids:
                    account_move_line_ids.append(t_line_id)

        created_vouchers = []
        vals = {}


        cr.execute('SELECT account_id, reconcile_id '\
                   'FROM account_move_line '\
                   'WHERE id IN %s '\
                   'GROUP BY account_id,reconcile_id',
                   (tuple(account_move_line_ids), ))
        r = cr.dictfetchall()

        account_ids = [x['account_id'] for x in r]

        for t_acc in account_ids:

            cr.execute('SELECT partner_id '\
                       'FROM account_move_line '\
                       'WHERE id IN %s AND account_id = %s '\
                       'GROUP BY partner_id',
                       (tuple(account_move_line_ids), t_acc ))
            r = cr.dictfetchall()
    
            partner_ids = [x['partner_id'] for x in r]

            for t_partner in partner_ids:

                t_amount = 0.0
    
                t_filter2 = ['&',
                             ('state', '=', 'selected'),
                             ('account_id', '=', t_acc),
                             ('partner_id', '=', t_partner),
                             ('confirm_payment_wht_id', '=', t_wizard)]
                wizard_line_ids = wizard_line_obj.search(cr,
                                                        uid,
                                                        t_filter2,
                                                        context=context)
                if wizard_line_ids:
                    for t_wl in wizard_line_obj.browse(cr, uid, wizard_line_ids):
                        t_ml = t_wl.move_line_id
                        if(t_ml.credit > 0):
                            t_amount = t_amount + t_wl.amount
                        else:
                            t_amount = t_amount - t_wl.amount
        
                    vals['amount'] = t_amount
                    vals['account_id'] = t_account_id
                    vals['partner_id'] = t_partner
                    vals['comment'] = 'Write_off'
                    vals['type'] = 'payment'
                    vals['pay_now'] = 'pay_now'
                    vals['company_id'] = self.get_company(cr, uid, context)
                    vals['state'] = 'posted'
                    vals['pre_line'] = False
                    vals['payment_rate'] = 1
                    vals['payment_option'] = 'without_writeoff'
                    vals['active'] = True
                    vals['journal_id'] = t_journal_id
                    vals['operation_date'] = t_date_op
                    vals['date'] = t_date_op
                    vals['document_date'] = t_date_op
                    vals['currency_date'] = t_currency_date
                    vals['bank_id'] = t_bank
                    vals['period_id'] = t_period
                    vals['document_number'] = None
                    vals['tax_id'] = None
                    vals['tax_amount'] = None
                    vals['name'] = None
                    vals['analytic_id'] = None
                    vals['date_due'] = None
                    vals['reference'] = None
                    vals['writeoff_acc_id'] = None
                    vals['narration'] = None
    
                    move_line_obj.write(cr,
                                        uid,
                                        account_move_line_ids,
                                        {'wht_state':'paid'})
    
                    res = None
                    res = self.create(cr, uid, vals, context=None)
                    t_res = int(res)
        
                    t_lines = []
                   
                    for line_id in wizard_line_obj.browse(cr, uid, wizard_line_ids):
        
                        t_move_line = line_id.move_line_id
                        if(t_move_line.credit > 0):
                            t_type = 'dr'
                        else: 
                            t_type = 'cr'
        
                        t_lines.append((0, 0, {
                                                'name': t_move_line.ref,
                                                'voucher_id': t_res,
                                                'account_id': t_move_line.account_id.id,
                                                'move_line_id': t_move_line.id,
                                                'type': t_type,
                                                'amount': line_id.amount,
                                                'amount_original': (t_move_line.debit or t_move_line.credit)
                                                 }))
                    self.write(cr, uid, [t_res], {'line_dr_ids': t_lines})
                    created_vouchers.append(t_res)

        return created_vouchers 

    def reconcile_allowance(self, cr, uid, ids):
        company_obj = self.pool.get('res.company')
        line_obj = self.pool.get('account.move.line')

        my_company_id = self.get_company(cr, uid, context=None)
        my_company = company_obj.browse(cr, uid, my_company_id)
        t_active = my_company.bonus_active_account_id.id
        t_passive = my_company.bonus_passive_account_id.id

        t_voucher_data = self.browse(cr, uid, ids)
        for t_voucher in t_voucher_data:
            t_move = t_voucher.move_id.id
            for t_move_line in t_voucher.move_id.line_id:
                if t_move_line.reconcile_id:
                    t_rec = t_move_line.reconcile_id.id
                    line_allowance_ids = line_obj.search(cr, uid,
                                                         [('move_id', '=', t_move),
                                                          ('reconcile_id', '=', None),
                                                          ('account_id', 'in', [t_active, t_passive]),
                                                          ('name', '=', t_move_line.name)])
                    line_obj.write(cr, uid, line_allowance_ids, {
                                                         'reconcile_id': t_rec
                                                         })
        return True

    def validate_all_voucher(self, cr, uid, ids, context=None): 
        draft_voucher_ids = self.search(cr, uid, [('state', '=', 'draft')])
        move_obj = self.pool.get('account.move')
        for v_id in draft_voucher_ids:
            self.action_move_line_create(cr, uid, [v_id])
            t_voucher = self.browse(cr, uid, v_id)
            self.reconcile_allowance(cr, uid, [v_id])
            t_move_id = t_voucher.move_id.id
            if(t_voucher.move_id.journal_id.entry_posted == True):
                move_obj.button_validate(cr, uid, [t_move_id], context)

        return True

    def validate_all_voucher_wht(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        for v_id in ids:
            self.action_move_line_create(cr, uid, [v_id])
            t_voucher = self.browse(cr, uid, v_id)
            self.reconcile_allowance(cr, uid, [v_id])
            t_move_id = t_voucher.move_id.id
            if(t_voucher.move_id.journal_id.entry_posted == True):
                move_obj.button_validate(cr, uid, [t_move_id], context)
        return True

    def create_validate_voucher(self, cr, uid, ids, context=None):
        self._create_supplier_voucher(cr, uid, ids, context)
        self.validate_all_voucher(cr, uid, ids, context)
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'post_payment_view')
        view_id = result and result[1] or False
 
        return {
               'name': _("Post Payment"),
               'view_type': 'form',
               'view_mode': 'form',
               'res_model': 'wizard.post.payment',
               'type': 'ir.actions.act_window',
               'view_id': view_id,
               'context': context,
               'target': 'inlineview',
               }

    def create_customer_voucher(self, cr, uid, ids, context=None):

        invoice_obj =           self.pool.get('account.invoice')
        wizard_line_obj =       self.pool.get('wizard.confirm.customer.payment.line')

        context_partner_id =    context.get('partner_id', None)
        t_date_op =             context.get('operation_date', None)
        t_currency_date =       context.get('currency_date', None)
        t_bank =                context.get('bank_id', None)
        t_period =              context.get('period_id', None)
        t_wizard =              context.get('wizard_id', None)

        t_journal_id = self._get_journal_id(cr, uid, t_bank)
        t_account_id = self._get_account_id(cr, uid, t_journal_id)

        list_partner = []

        if context_partner_id:
            list_partner = [context_partner_id]

        if not context_partner_id:
            selected_line_ids = wizard_line_obj.search(cr,
                                                     uid,
                                                     ['&',
                                                      ('is_selected', '=', 'accepted'),
                                                      ('confirm_payment_id', '=', t_wizard)],
                                                     context=context)

            if selected_line_ids:
                t_wizard_line_data = wizard_line_obj.browse(cr, uid, selected_line_ids)
                for t_wizard_line in t_wizard_line_data:
                    t_partner_id = None
                    if t_wizard_line.partner_id:
                        t_partner_id = t_wizard_line.partner_id.id
                    if t_partner_id not in list_partner:
                        list_partner.append(t_partner_id)

        for t_partner_inlist_id in list_partner:

            self._set_move_lines_valid(cr,
                                       uid,
                                       context,
                                       'customer_id',
                                       t_wizard,
                                       t_partner_inlist_id)

            wizard_line_ids = wizard_line_obj.search(cr,
                                                    uid,
                                                    ['&',
                                                     ('partner_id', '=', t_partner_inlist_id),
                                                     ('is_selected', '=', 'accepted'),
                                                     ('confirm_payment_id', '=', t_wizard)],
                                                    context=context)

            if wizard_line_ids:
                t_amount = self._get_amount_customer(cr, uid, wizard_line_ids)

                vals = {}
                vals['amount'] = t_amount
                vals['account_id'] = t_account_id
                vals['partner_id'] = t_partner_inlist_id
                vals['comment'] = 'Write_off'
                vals['type'] = 'receipt'
                vals['is_multi_currency'] = False
                vals['pay_now'] = 'pay_now'
                vals['company_id'] = self.get_company(cr, uid, context)
                vals['state'] = 'posted'
                vals['pre_line'] = False

                # FIXME ???
                vals['payment_rate'] = 1

                vals['payment_option'] = 'without_writeoff'
                vals['active'] = True
                vals['journal_id'] = t_journal_id
                vals['operation_date'] = t_date_op
                vals['date'] = t_date_op
                vals['document_date'] = t_date_op
                vals['currency_date'] = t_currency_date

                vals['bank_id'] = t_bank
                # FIXME evitare a priori che t_bank sia di tipo browse_record
                if isinstance(t_bank, browse_record):
                    vals['bank_id'] = t_bank.id

                vals['period_id'] = t_period
                vals['document_number'] = None
                vals['tax_id'] = None
                vals['tax_amount'] = None
                vals['name'] = None
                vals['analytic_id'] = None
                vals['reference'] = None
                vals['writeoff_acc_id'] = None
                vals['narration'] = None
                vals['date_due'] = None

                res = self.create(cr, uid, vals, context=None)
                t_res = int(res)

                t_lines = []
               
                for line_id in wizard_line_obj.browse(cr, uid, wizard_line_ids):
                    t_move_line = line_id.move_line_id
                    t_company_data = t_move_line.move_id.company_id
                    t_bonus_active_account_id = t_company_data.bonus_active_account_id.id
                    t_bonus_passive_account_id = t_company_data.bonus_passive_account_id.id

                    t_type = 'dr'
                    if(t_move_line.debit > 0):
                        t_type = 'cr'

                    if(line_id.allowance == True):
                        t_invoice_ids = invoice_obj.search(cr, uid,
                                                           [('move_id', '=', t_move_line.move_id.id)])
                        if not t_invoice_ids:
                            raise orm.except_orm(_('Error!'),
                                                 _('Nessuna fattura per la movimentazione') % (t_move_line.move_id.id))
                        t_invoice_id = t_invoice_ids[0]
                        t_invoice = invoice_obj.browse(cr, uid, t_invoice_id)
                        if((line_id.amount_allowance > 0.0 and t_invoice.type=='out_invoice') or (line_id.amount_allowance < 0.0 and t_invoice.type=='out_refund')):
                            t_account_allowance = t_bonus_active_account_id
                            t_allowance_type = 'dr'
                            t_allowance_amount = -line_id.amount_allowance
                            if(t_invoice.type=='out_refund'):
                                t_allowance_amount = line_id.amount_allowance
                        else: 
                            t_account_allowance = t_bonus_passive_account_id
                            t_allowance_type = 'cr'
                            t_allowance_amount = line_id.amount_allowance
                            if(t_invoice.type=='out_refund'):
                                t_allowance_amount = -line_id.amount_allowance
                        t_lines.append((0, 0, {
                                            'name': t_move_line.ref,
                                            'voucher_id': t_res,
                                            'account_id': t_move_line.account_id.id,
                                            'move_line_id': t_move_line.id,
                                            'type': t_type,
                                            'amount': line_id.amount_partial - line_id.amount_allowance,
                                            'amount_original': (t_move_line.debit or t_move_line.credit),
                                            'amount_unreconciled': line_id.amount_partial - (t_move_line.debit or t_move_line.credit)
                                             }))
                        t_lines.append((0, 0, {
                                            'name': t_move_line.ref,
                                            'voucher_id': t_res,
                                            'account_id': t_account_allowance,
                                            'move_line_id': None,
                                            'type': t_allowance_type,
                                            'amount': t_allowance_amount,
                                            'amount_original': line_id.amount_allowance,
                                            'amount_unreconciled': 0.0,
                                             }))
                    else:
                        t_lines.append((0, 0, {
                                            'name': t_move_line.ref,
                                            'voucher_id': t_res,
                                            'account_id': t_move_line.account_id.id,
                                            'move_line_id': t_move_line.id,
                                            'type': t_type,
                                            'amount': line_id.amount_partial,
                                            'amount_original': (t_move_line.debit or t_move_line.credit),
                                            'amount_unreconciled': line_id.amount_partial - (t_move_line.debit or t_move_line.credit)
                                             }))
                   
                self.write(cr, uid, [t_res], {'line_cr_ids': t_lines})
               
        return True 

    def create_validate_customer_voucher(self, cr, uid, ids, context=None):
        self.create_customer_voucher(cr, uid, ids, context)
        self.validate_all_voucher(cr, uid, ids, context)
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                               'account_voucher_makeover',
                                               'post_customer_payment_view')
        view_id = result and result[1] or False
 
        return {
               'name': _("Post Payment"),
               'view_type': 'form',
               'view_mode': 'form',
               'res_model': 'wizard.post.payment',
               'type': 'ir.actions.act_window',
               'view_id': view_id,
               'context': context,
               'target': 'inlineview',
               }
    
    def create_validate_wht_voucher(self, cr, uid, ids, context=None):
        created_wht_vouchers = self.create_wht_voucher(cr, uid, ids, context)
        self.validate_all_voucher_wht(cr, uid, created_wht_vouchers, context)
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                               'account_voucher_makeover',
                                               'post_payment_view')
        view_id = result and result[1] or False
 
        return {
               'name': _("Post Payment"),
               'view_type': 'form',
               'view_mode': 'form',
               'res_model': 'wizard.post.payment',
               'type': 'ir.actions.act_window',
               'view_id': view_id,
               'context': context,
               'target': 'inlineview',
               }
    
    _columns = {
        'period_id': fields.many2one('account.period',
                                     'Period'),
        'operation_date': fields.date('Operation Date',
                                      required=True),
        'currency_date': fields.date('Currency Date'),
        'bank_id': fields.many2one('res.partner.bank',
                                   'Banca da addebitare'),
        'partner_bank_id': fields.many2one('res.partner.bank',
                                   'Banca Appoggio Partner'),
        'journal_id':fields.many2one('account.journal',
                                     'Journal',
                                     required=True),
        'account_id':fields.many2one('account.account',
                                     'Account',
                                     required=True),
        'document_number': fields.char('Document Number',
                                     size=64),
        'document_date': fields.date('Document Date',
                                     required=True,
                                     states={'draft':[('readonly', False)]},
                                     select=True),
        'date':fields.date('Registration Date',
                                     readonly=True,
                                     select=True,
                                     states={'draft':[('readonly', False)]},
                                     help="Effective date for accounting entries"),
        'wht_move_ids': fields.many2many('account.move',
                                     'voucher_withholding_move_rel',
                                     'voucher_id',
                                     'move_id',
                                     'Withholding Tax Entries',
                                     readonly=True),
        'line_dr_ids':fields.one2many('account.voucher.line',
                                      'voucher_id',
                                      'Debits',
                                      domain=[('type', '=', 'dr'),
                                              ('move_line_id.is_wht', '!=', True)],
                                      context={'default_type':'dr'},
                                      readonly=True,
                                      states={'draft':[('readonly', False)]}),
                }

    _defaults = {
                 'move_ids': _default_accepted_lines,
                 'operation_date': fields.date.context_today,
                 'account_id': 1,
                 'document_date': fields.date.context_today,
                 }

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
        }

        # drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
        for line in line_pool.browse(cr, uid, line_ids, context=context):
            if line.type == 'cr':
                default['value']['line_cr_ids'].append((2, line.id))
            else:
                default['value']['line_dr_ids'].append((2, line.id))

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.pool['account.account'].browse(cr, uid, context['account_id'], context=context).type
        if ttype == 'payment':
            if not account_type:
                account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            if not account_type:
                account_type = 'receivable'

        if not context.get('move_line_ids', False):
            ids = move_line_pool.search(cr, uid, [('account_id','in',[partner.property_account_receivable.id, partner.property_account_payable.id]),('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_lines_found.append(line.id)
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_lines_found.append(line.id)
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        remaining_amount = price
        #voucher line creation
 
        
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': invoice_id and (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            remaining_amount -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            '''
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount
            '''
            if rs['move_line_id']:
                t_move_line_id = rs['move_line_id']
                
                move_line_obj = self.pool.get('account.move.line')
                move_line_res = move_line_obj.browse(cr, uid, t_move_line_id, context=None)
        
                if move_line_res and move_line_res.is_wht:
                    rs.update({'is_wht': True})   
                else:
                    rs.update({'is_wht': False})

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default

    def proforma_voucher(self, cr, uid, ids, context=None):
        update_ids = []
        for id in ids:
            if self.browse(cr,uid,id).type == 'sale':
                update_ids.append(id)
        if update_ids:
            self.compute_tax(cr, uid, update_ids, context=context)
        res = super(account_voucher_makeover, self).proforma_voucher(cr, uid, ids,
                                                            context=context)

        t_voucher_data = self.browse(cr, uid, ids, context=context)
        for t_voucher in t_voucher_data:
            t_move_id = t_voucher.move_id.id
            t_document_date = t_voucher.date
            t_document_number = t_voucher.document_number
    
            self.pool.get('account.move').write(cr, uid,
                                               [t_move_id],
                                               {
                                                'document_date': t_document_date,
                                                'document_number': t_document_number,
                                                })
            for line in t_voucher.move_ids:
                self.pool.get('account.move.line').write(cr,uid,line.id,{'credit': line.credit, 'debit': line.debit, 'tax_amount': line.tax_amount}, check=False, update_check=False)
        return res

    def reconcile_withholding_move(self, cr, uid,
                                   invoice, wh_move,
                                   context=None):
        rec_ids = []
        for inv_move_line in invoice.move_id.line_id:
            if (inv_move_line.account_id.type == 'payable' and
                    not inv_move_line.reconcile_id):
                rec_ids.append(inv_move_line.id)
        for wh_line in wh_move.line_id:
            t_wht_account = invoice.partner_id.wht_account_id
            if (wh_line.account_id.type == 'payable'
                    and t_wht_account
                    and t_wht_account.id != wh_line.account_id.id
                    and not wh_line.reconcile_id
                    and not wh_line.credit):
                rec_ids.append(wh_line.id)

        move_line_obj = self.pool.get('account.move.line')
        move_line_data = move_line_obj.browse(cr, uid, rec_ids, context=None)

        for t_move_line in move_line_data:
            if (t_move_line.is_wht):
                
                move_line_obj.write(cr, uid, rec_ids, {'state':'valid'})
                
                
                
        return move_line_obj.reconcile_partial(cr, uid, rec_ids,
                                           type='auto', context=context)

    def get_invoice_total(self, invoice):
        res = 0.0
        for inv_move_line in invoice.move_id.line_id:
            if inv_move_line.account_id.type in ('receivable', 'payable'):
                # can both be presents?
                res += inv_move_line.debit or inv_move_line.credit
        return res

    def _get_amounts_grouped_by_invoice(self, cr, uid, voucher, context=None):
        '''
        this method builds a dictionary in the following format
        {
            first_invoice_id: {
                'allocated': 120.0,
                'total': 120.0,
                'wht-tax': 20.0,
                }
            second_invoice_id: {
                'allocated': 50.0,
                'total': 100.0,
                'wht-tax': 0.0,
                }
        }
        every amount is expressed in company currency.
        '''
        res = {}
        company_currency = super(account_voucher_makeover,
                                 self)._get_company_currency(cr, uid,
                                            voucher.id, context)
        current_currency = super(account_voucher_makeover,
                                 self)._get_current_currency(cr, uid,
                                            voucher.id, context)
        for line in voucher.line_ids:
            t_inv = line.move_line_id.invoice
            if (line.amount
                    and line.move_line_id
                    and t_inv):
                t_invoice_id = t_inv.id
                if not t_invoice_id in res:
                    res[t_invoice_id] = {
                        'allocated': 0.0,
                        'total': 0.0,
                        'wht-tax': 0.0, }
                current_amount = line.amount
                invoice_total_amount = 0.0
                withholding_amount = 0.0
                if company_currency != current_currency:
                    current_amount = super(account_voucher_makeover,
                                        self)._convert_amount(cr, uid,
                                                line.amount, voucher.id,
                                                context)
                res[t_invoice_id]['allocated'] += current_amount
                invoice_total_amount = self.get_invoice_total(t_inv)
                res[t_invoice_id]['total'] = invoice_total_amount
                if (t_inv.wht_amount):
                    withholding_amount = t_inv.wht_amount
                res[t_invoice_id]['wht-tax'] = withholding_amount

        return res

    def wht_already_reconciled(self, cr, uid, voucher, context=None):
        for line in voucher.line_ids:
            if (line.move_line_id
                     and line.move_line_id.is_wht
                     and not line.move_line_id.reconcile_id
                     and not line.move_line_id.reconcile_partial_id):
                return False
        return True

    def _check_constraints(self, voucher, invoice):
        # only for supplier payments
        if voucher.type != 'payment':
            raise orm.except_orm(_('Error'),
                                 _('Can\'t handle withholding tax with voucher of type other than payment'))
        if not invoice.partner_id.wht_account_id:
            raise orm.except_orm(_('Error'),
                                 _('The partner does not have an associated Withholding account'))
        if not invoice.partner_id.wht_account_id.account_id:
            raise orm.except_orm(_('Error'),
                                 _('The Withholding account of the partner does not have an associated account'))
        if not invoice.partner_id.wht_account_id.wht_payment_term:
            raise orm.except_orm(_('Error'),
                                 _('The Withholding account does not have an associated Withholding Payment Term'))
        if not invoice.partner_id.wht_account_id.wht_journal_id:
            raise orm.except_orm(_('Error'),
                                 _('The Withholding account does not have an associated Withholding journal'))

    def _check_computed_due_list(self, name, due_list):
        if len(due_list) > 1:
            raise orm.except_orm(_('Error'),
                _('The payment term %s has too many due dates') % name)
        if len(due_list) == 0:
            raise orm.except_orm(_('Error'),
                _('The payment term %s does not have due dates') % name)

    def cancel_voucher(self, cr, uid, ids, context=None):
        res = super(account_voucher_makeover, self).cancel_voucher(cr, uid, ids,
                                                              context)

        move_pool = self.pool.get('account.move')
        for voucher in self.browse(cr, uid, ids, context=context):

            for move in voucher.wht_move_ids:
                move_pool.button_cancel(cr, uid, [move.id])
                move_pool.unlink(cr, uid, [move.id])
        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id,
                            amount, currency_id, ttype, date, context=None):

        res = super(account_voucher_makeover, self).onchange_partner_id(cr, uid,
                                                               ids, partner_id,
                                                               journal_id,
                                                               amount,
                                                               currency_id,
                                                               ttype,
                                                               date,
                                                               context)
        if res and 'value' in res and res['value'] and 'line_dr_ids' in res['value'] and res['value']['line_dr_ids']:
            t_counter = 0
            for line in res['value']['line_dr_ids']:
                if line['move_line_id']:
                    t_move_line_id = line['move_line_id']
                    
                    move_line_obj = self.pool.get('account.move.line')
                    move_line_res = move_line_obj.browse(cr, uid, t_move_line_id, context=None)
            
                    if move_line_res and move_line_res.is_wht:
                        res['value']['line_dr_ids'][t_counter].update({'is_wht': True})
                t_counter = t_counter + 1

        return res
