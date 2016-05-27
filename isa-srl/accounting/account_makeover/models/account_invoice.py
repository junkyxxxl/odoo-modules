# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
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
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import copy
import time
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import tools
from openerp.osv.orm import browse_record
from openerp.exceptions import ValidationError

from openerp import workflow, api
from openerp.exceptions import except_orm, Warning, RedirectWarning

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}

class account_invoice_line_makeover(orm.Model):
    _inherit = "account.invoice.line"
    
    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, company_id=None):    
        res = super(account_invoice_line_makeover,self).product_id_change(product, uom_id, qty=qty, name=name, type=type, partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id, company_id=company_id)
        if res and res['value'] and partner_id and product and type=='out_invoice':
            if not 'price_unit' in res['value'] or ('price_unit' in res['value'] and (not res['value']['price_unit'] or res['value']['price_unit'] == price_unit)):
                pricelist = self.pool.get('res.partner').browse(self._cr, self._uid, partner_id, context=self._context).property_product_pricelist
                if pricelist:
                    price_unit = self.pool.get('product.pricelist').price_get(self._cr, self._uid, [pricelist.id], product, qty, partner_id, context=self._context)[pricelist.id]                    
                else:
                    price_unit = self.pool.get('product.product').browse(self._cr, self._uid, product, context=self._context).lst_price  
                res['value']['price_unit'] = price_unit          
        return res

    @api.one
    @api.constrains('product_id','invoice_line_tax_id')
    def _check_tax_presence(self):
        if self.product_id and not self.invoice_line_tax_id:
            raise ValidationError(_("You should set a tax for each non-descriptive invoice line!"))

class account_invoice_makeover(orm.Model):
    _inherit = "account.invoice"

    def _get_withholding_payment_term(self):
        p_term_obj = self.pool.get('account.payment.term')
        p_term_search = p_term_obj.search(self._cr, self._uid,
                                          [('name', '=',
                                            '16th Next Month')],
                                          limit=1)
        if not p_term_search:
            raise orm.except_orm(_('Error!'),
                (_('Payment term "16th Next Month" missing!')))

        p_term_res = p_term_obj.browse(self._cr, self._uid, p_term_search,
                                           context=False)
        p_term_id = p_term_res and p_term_res[0].id
        p_term_name = p_term_res and p_term_res[0].name
        return p_term_id, p_term_name

    def _get_min_payment_term(self, move_lines):
        date_maturity_list = []
        for t_line in move_lines:
            t_date_maturity = t_line[2]['date_maturity']
            if t_date_maturity:
                date_maturity_list.append(t_date_maturity)
        
        t_min_payment_term = min(string for string in date_maturity_list)
        
        return t_min_payment_term

    def _new_wht_payment_term(self, move_lines, date_due,
                              withholding_amount):
        p_term_id, p_term_name = self._get_withholding_payment_term()
        t_min_payment_term = self._get_min_payment_term(move_lines)
        if not t_min_payment_term:
            t_min_payment_term = date_due
        payment_term_obj = self.pool.get('account.payment.term')
        new_payment_term = payment_term_obj.compute(self._cr,
                                                    self._uid,
                                                    p_term_id,
                                                    withholding_amount,
                                                    date_ref=t_min_payment_term or False)

        if len(new_payment_term) > 1:
            raise orm.except_orm(_('Error'),
                _('The payment term %s has too many due dates')
                % p_term_name)

        if len(new_payment_term) == 0:
            raise orm.except_orm(_('Error'),
                _('The payment term %s does not have due dates')
                % p_term_name)

        return new_payment_term

    def _recreate_move_lines(self, invoice_browse, m_lines, old_pt,
                             new_pt, add_pt):
        last_move_line = None
        for t_mline in range(len(m_lines)):
            t_suppl_inv_number = invoice_browse.supplier_invoice_number
            if (m_lines[t_mline][2]['date_maturity'] and
                    m_lines[t_mline][2]['credit'] > 0 and 
                    m_lines[t_mline][2]['name'] == t_suppl_inv_number):

                last_move_line = m_lines[t_mline]

                for i in range(len(old_pt)):
                    new_pt_date = new_pt[i][0]
                    new_pt_credit = new_pt[i][1]
                    if (old_pt[i][0] == m_lines[t_mline][2]['date_maturity']
                        and old_pt[i][1] == m_lines[t_mline][2]['credit']):
                        m_lines[t_mline][2]['date_maturity'] = new_pt_date
                        m_lines[t_mline][2]['credit'] = new_pt_credit
        if last_move_line:
            new_move_line = copy.deepcopy(last_move_line)
#            date_formatted = datetime.strptime(add_pt[0][0],
#                                                DF).strftime('%d/%m/%Y')
            t_date = self.pool.get('account.payment.term').check_if_holiday(add_pt[0][0])
            new_move_line[2]['date_maturity'] = datetime.strptime(t_date, '%Y-%m-%d')
            new_move_line[2]['credit'] = invoice_browse.wht_amount
            # invoice_browse.number not yet defined
            new_move_line[2]['name'] = _('Payable withholding - ') + '/'
            new_move_line[2]['is_wht'] = True
            new_move_line[2]['wht_state'] = 'open'
            new_move_line[2]['state'] = 'valid'
            m_lines.append(new_move_line)

        return m_lines

    def _calculate_payment_terms(self, move_lines, date_invoice):
        obj_pt = self.pool.get('account.payment.term')

        old_pt = obj_pt.compute(self._cr, self._uid, self.payment_term.id,
            self.amount_total,
            date_ref=date_invoice)

        new_pt = obj_pt.compute(self._cr, self._uid,
            self.payment_term.id,
            self.net_pay,
            date_ref=date_invoice)

        add_pt = self._new_wht_payment_term(move_lines,
                                            self.date_due,
                                            self.wht_amount)

        return old_pt, new_pt, add_pt

    def _check_withholding_integrity(self, invoice):

        if not invoice.partner_id.wht_account_id:
            raise orm.except_orm(_('Error'),
                  _('The partner does not have an associated Withholding account'))

        if not invoice.partner_id.wht_account_id.wht_payment_term:
            raise orm.except_orm(_('Error'),
                  _('The Withholding account does not have an associated Withholding Payment Term'))

        return

    @api.model
    def line_get_convert(self, line, part, date):
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'date': date,
            'debit': line['price']>0 and line['price'],
            'credit': line['price']<0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_lines': line.get('analytic_lines', []),
            'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'tax_code_id': line.get('tax_code_id', False),
            'tax_amount': line.get('tax_amount', False),
            'ref': line.get('ref', False),
            'quantity': line.get('quantity',1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uos_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
            'payment_type_move_line': line.get('payment_type_move_line', False),
        }

    def onchange_withholding_amount(self, cr, uid, ids, wht_amount=False,
                                    amount_total=False, context=None):
        if not ids:
            return {'value': {
                    'wht_amount': 0.0,
                    'has_wht': False,
                    'net_pay': amount_total,
                    }
            }

        return {'value': {
                    'wht_amount': wht_amount,
                    'has_wht': True,
                    'net_pay': amount_total - wht_amount,
                    }
        }

    def onchange_supplier_invoice_number(self, cr, uid, ids, partner_id,
                                         supplier_invoice_number, context=None):
        warning = {}
        t_invoice_ids = self.search(cr, uid,
                                    [('partner_id', '=', partner_id),
                                     ('supplier_invoice_number', '=', supplier_invoice_number)])
        if t_invoice_ids:
            warning = {
                       'title': _('Warning!'),
                       'message': _('There is another invoice with the same number for this supplier')
                       }
        return {'value': {},
                'warning': warning
                 }

    def group_lines(self, iml, line):
        line = super(account_invoice_makeover,self).group_lines(iml, line)
        if self.journal_id.group_invoice_lines:
            line2 = {}
            other_lines = []
            for x, y, l in line:
                tmp =   (
                            l['account_id'],
                            l.get('tax_code_id', 'False'),
                            l.get('analytic_account_id', 'False'),
                            l.get('date_maturity', 'False'),
                        )   
                if tmp in line2 and not tmp[2]:
                    am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
                    line2[tmp]['debit'] = (am > 0) and am or 0.0
                    line2[tmp]['credit'] = (am < 0) and -am or 0.0
                    line2[tmp]['tax_amount'] += l['tax_amount']
                    line2[tmp]['analytic_lines'] += l['analytic_lines']
                    line2[tmp]['product_id'] = False
                    if l['account_id']:
                        line2[tmp]['name'] = self.pool.get('account.account').browse(self._cr, self._uid, l['account_id']).name
                    else:
                        line2[tmp]['name'] = 'Raggruppamento'
                elif tmp not in line2:
                    line2[tmp] = l
                else:
                    other_lines.append(l)
            line = []
            for key, val in line2.items():
                line.append((0,0,val))
            for l in other_lines:
                line.append((0,0,l))
        return line

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(account_invoice_makeover,self).finalize_invoice_move_lines(move_lines)
        if (self.type in ('in_invoice')
                    and self.partner_id.wht_account_id
                    and self.wht_amount > 0):

            self._check_withholding_integrity(self)

            date_invoice = self.date_invoice
            if not date_invoice:
                date_invoice = time.strftime(DF)

            old_pt, new_pt, add_pt = self._calculate_payment_terms(move_lines,
                                                                   date_invoice)

            move_lines = self._recreate_move_lines(self,
                                                   move_lines, old_pt,
                                                   new_pt, add_pt)

        return move_lines

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id:
                raise orm.except_orm(_('Error!'),
                    _('Journal not defined for this invoice!'))
            if not inv.journal_id.iva_registry_id:
                raise orm.except_orm(_('Error!'),
                    _('You must link %s with a VAT registry!') % (inv.journal_id.name))

            if not inv.journal_id.sequence_id:
                raise orm.except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise orm.except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if 'company_id' not in ctx:
                ctx['company_id'] = inv.company_id.id

            period_id = inv.period_id and inv.period_id.id or False
            if not period_id:
                period_obj = self.pool.get('account.period')
                period_ids = period_obj.find(self._cr, self._uid, inv.registration_date, context=self._context)
                period_id = period_ids and period_ids[0] or False
                if period_id:
                    self.with_context(ctx).write({'period_id': period_id})

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv)
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env['res.users'].has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise orm.except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise orm.except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id !=  company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.name or inv.supplier_invoice_number or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                        'payment_type_move_line': t[2]
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref,
                    'payment_type_move_line': None
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise orm.except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.registration_date,
                'document_date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            move = account_move.with_context(ctx).create(move_vals)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
    
    
    @api.multi
    def button_reset_taxes(self):

        self.button_display_withholding_amount()
        result = super(account_invoice_makeover,self).button_reset_taxes()

        return result
    
    
    def _check_invoice_partner(self, cr, uid, invoice_type, invoice_partner, is_autoinvoice):
        partner_obj = self.pool.get('res.partner')
        partner_data = partner_obj.browse(cr, uid, invoice_partner)
        if invoice_type in ['in_invoice', 'in_refund']:
            if not partner_data.supplier:
                raise orm.except_orm(_('Error!'),
                                     _('The selected partner must be a Supplier'))
        if invoice_type in ['out_invoice', 'out_refund']:
            if not partner_data.customer and is_autoinvoice != True:
                raise orm.except_orm(_('Error!'),
                                     _('The selected partner must be a Customer'))
        return True

    @api.v7
    def _set_invoice_tax(self, cr, user, t_id, ctx):
        if not ctx.get('skip_step'):
            ait_obj = self.pool.get('account.invoice.tax')
            cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (t_id,))
            for taxe in ait_obj.compute(cr, user, t_id, context=ctx).values():
                ait_obj.create(cr, user, taxe)

    def _set_partner_context(self, cr, user, context, invoice_partner):
        ctx = context.copy()
        partner_obj = self.pool.get('res.partner')
        partner_data = partner_obj.browse(cr, user, invoice_partner)
        if partner_data.lang:
            ctx.update({'lang':partner_data.lang})
        return ctx

    def _payment_term_contains_bank_transfer(self, cr, user, payment_term_ids):
        p_term_obj = self.pool.get('account.payment.term')
        p_term_data = p_term_obj.browse(cr, user, payment_term_ids)
        for p_term in p_term_data:
            p_term_line_data = p_term.line_ids
            for p_term_line in p_term_line_data:
                if (p_term_line.payment_type and p_term_line.payment_type == 'B'):
                    return True
        return False

    def check_intracee(self, cr, uid, fiscal_position_id, context=None):
        c_fiscal_position_id = None
        if context and 'company_id' in context and context['company_id']:
            c_fiscal_position_id = self.pool.get('res.company').browse(cr, uid, context['company_id'], context=context).intracee_fiscal_position.id        
        fiscal_position_obj = self.pool.get('account.fiscal.position')
        for rec in fiscal_position_obj.browse(cr, uid, [fiscal_position_id]):
            if (rec.id == c_fiscal_position_id):
                return True
        return False

    def check_reverse_charge(self, cr, uid, fiscal_position_id, context=None):
        t_bool = False
        c_fiscal_position_id = None
        if context and 'company_id' in context and context['company_id']:
            c_fiscal_position_id = self.pool.get('res.company').browse(cr, uid, context['company_id'], context=context).reverse_charge_fiscal_position.id                
        fiscal_position_obj = self.pool.get('account.fiscal.position')
        for rec in fiscal_position_obj.browse(cr, uid, [fiscal_position_id]):
            if (rec.id == c_fiscal_position_id):
                t_bool = True
        return t_bool

    def create(self, cr, user, vals, context=None):
        if context is None:
            context = {}

        invoice_type = context.get('type')
        if (invoice_type in ['in_invoice', 'in_refund'] and 'registration_date' in vals and 'date_invoice' in vals):
            t_registration_date = vals["registration_date"]
            t_date_invoice = vals["date_invoice"]
            if(t_registration_date and t_date_invoice and t_date_invoice > t_registration_date):
                raise orm.except_orm(_('Error!'),_('Document Date must be less then Registration Date'))
        if (invoice_type in ['in_invoice', 'in_refund'] and 'payment_term' in vals and ('partner_bank_id' not in vals or not vals["partner_bank_id"])):
            if self._payment_term_contains_bank_transfer(cr, user, [vals["payment_term"]]):
                t_partner_data = self.pool.get('res.partner').browse(cr, user, vals["partner_id"])
                if t_partner_data.bank_ids:
                    vals['partner_bank_id'] = t_partner_data.bank_ids[0].id
                    for t_bank in t_partner_data.bank_ids:
                        if t_bank.default_bank:
                            vals['partner_bank_id'] = t_bank.id
                            break

        invoice_partner = vals["partner_id"]

        is_autoinvoice = False
        if ("fiscal_position" in vals and vals["fiscal_position"] and self.check_intracee(cr, user, vals["fiscal_position"])):
            is_autoinvoice = True
        self._check_invoice_partner(cr, user, invoice_type, invoice_partner, is_autoinvoice)

        res = super(account_invoice_makeover, self).create(cr, user, vals, context)
        t_id = int(res)

        ctx = None
        if 'recompute_values' in vals and vals['recompute_values']:
            ctx = self._set_partner_context(cr, user, context, invoice_partner)
            self._set_invoice_tax(cr, user, t_id, ctx)

        t_dict = {}

        t_acc_inv = self.browse(cr, user, t_id)
        if(t_acc_inv.type == "in_invoice" or t_acc_inv.type == "in_refund"):
            if(t_acc_inv.supplier_invoice_number):
                t_dict['document_number'] = t_acc_inv.supplier_invoice_number

        wt_amount, t_invoice_id = self._model._get_wht_amount(cr, user, t_id, ctx=context)
        if t_invoice_id:
            if (wt_amount):
                t_dict['wht_amount'] = wt_amount
        if t_dict:
            self.write(cr, user, [t_id], t_dict, context)

        return res

    def _check_bank_account_riba(self, cr, uid, vals, t_id):
        t_acc_inv = self.browse(cr, uid, t_id)
        invoice_type = t_acc_inv.type
        if (invoice_type == "out_invoice" or invoice_type == "out_refund"):
            p_term_lines = None
            is_riba = False
            if t_acc_inv.payment_term and not 'payment_term' in vals:
                p_term_lines = t_acc_inv.payment_term.line_ids
            if ('payment_term' in vals and vals['payment_term']):
                p_term_obj = self.pool.get('account.payment.term')
                p_term_data = p_term_obj.browse(cr, uid, vals['payment_term'])
                p_term_lines = p_term_data.line_ids
            if p_term_lines:
                for p_term_line in p_term_lines:
                    if p_term_line.payment_type == 'D':
                        is_riba = True
            if is_riba:
                if (('bank_account' in vals and not vals['bank_account']) or 
                    'bank_account' not in vals and not t_acc_inv.bank_account):
                    return False
        return True

    def write(self, cr, uid, ids, vals, context=None):
        #if vals and ('type' in vals or 'registration_date' in vals or 'date_invoice' in vals or 'partner_id' in vals or 'is_autoinvoice' in vals or 'supplier_invoice_number' in vals or 'payment_term' in vals or 'partner_bank_id' in vals):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]

        for t_id in ids:
            try:
                t_acc_inv = self.browse(cr, uid, t_id)

                invoice_type = t_acc_inv.type
                invoice_partner = t_acc_inv.partner_id.id

                if 'type' in vals or 'registration_date' in vals or 'date_invoice' in vals:
                    if 'type' in vals:
                        invoice_type = vals['type']

                    if ('registration_date' in vals):
                        t_registration_date = vals["registration_date"]
                    else:
                        t_registration_date = t_acc_inv.registration_date

                    if ('date_invoice' in vals):
                        t_date_invoice = vals["date_invoice"]
                    else:
                        t_date_invoice = t_acc_inv.date_invoice

                    if (t_registration_date and t_date_invoice and t_date_invoice > t_registration_date and (invoice_type in ['in_invoice', 'in_refund'])):
                        raise orm.except_orm(_('Error!'), _('Document Date must be less then Registration Date'))


                if 'partner_id' in vals or 'is_autoinvoice' in vals:
                    if 'partner_id' in vals:
                        invoice_partner = vals["partner_id"]

                    if 'is_autoinvoice' in vals:
                        is_autoinvoice = vals["is_autoinvoice"]
                    else:
                        is_autoinvoice = t_acc_inv.is_autoinvoice

                    self._check_invoice_partner(cr, uid, invoice_type, invoice_partner, is_autoinvoice)

                if(invoice_type == "in_invoice" or invoice_type == "in_refund"):
                    if('supplier_invoice_number' in vals):
                        vals["document_number"] = vals["supplier_invoice_number"]

                if 'payment_term' in vals or 'partner_bank_id' in vals:
                    if 'payment_term' in vals:
                        t_payment_term = vals["payment_term"]
                    else:
                        t_payment_term = t_acc_inv.payment_term

                    if 'partner_bank_id' in vals:
                        t_partner_bank_id = vals["partner_bank_id"]
                    else:
                        t_partner_bank_id = t_acc_inv.partner_bank_id
                    if isinstance(t_payment_term, browse_record):
                        t_payment_term = t_payment_term.id

                    if (invoice_type in ['in_invoice', 'in_refund'] and t_payment_term and not t_partner_bank_id):
                        if self._payment_term_contains_bank_transfer(cr, uid, [t_payment_term]):
                            t_partner_data = self.pool.get('res.partner').browse(cr, uid, invoice_partner)
                            if t_partner_data.bank_ids:
                                vals['partner_bank_id'] = t_partner_data.bank_ids[0].id
                                for t_bank in t_partner_data.bank_ids:
                                    if t_bank.default_bank:
                                        vals['partner_bank_id'] = t_bank.id
                                        break

                if not self._check_bank_account_riba(cr, uid, vals, t_id):
                    t_partner_data = self.pool.get('res.partner').browse(cr, uid, invoice_partner)
                    '''
                    if not t_partner_data.bank_ids:
                        raise orm.except_orm(_('Error!'),
                            _('Il campo "Conto Bancario del Cliente" deve essere compilato poiché il termine di pagamento selezionato prevede le Ricevute Bancarie.'))

                    else:
                    '''
                    if t_partner_data.bank_ids:
                        vals['bank_account'] = t_partner_data.bank_ids[0].id
                        for t_bank in t_partner_data.bank_ids:
                            if t_bank.default_bank:
                                vals['bank_account'] = t_bank.id
                                break

                '''
                if 'tax_line' in vals:
                    t_recompute_vals = False
                    context.update({'skip_step': True,})
                elif 'recompute_values' in vals:
                    t_recompute_vals = vals['recompute_values']
                else:
                    t_recompute_vals = t_acc_inv.recompute_values

                if t_recompute_vals:
                    ctx = self._set_partner_context(cr, uid, context, invoice_partner)
                    self._set_invoice_tax(cr, uid, t_id, ctx=ctx)
                '''
                '''
                if 'partner_id' in vals or 'type' in vals or 'invoice_line' in vals:
                    wt_amount, t_invoice_id = self._model._get_wht_amount(cr, uid, t_id, ctx=context)

                if t_invoice_id:
                    vals["wht_amount"] = 0.0
                    if wt_amount:
                        vals["wht_amount"] = wt_amount

                if t_invoice_id and context.get('recompute', True):

                    prev_lines_obj = self.pool.get('account.invoice.maturity.preview.lines')
                    invoice_unlink_ids = prev_lines_obj.search(cr, uid, [('invoice_id', '=', t_invoice_id)])
                    prev_lines_obj.unlink(cr, uid, invoice_unlink_ids, context=context)
                '''

            except :
                pass

        res = super(account_invoice_makeover, self).write(cr, uid, ids, vals, context)
        return res

    @api.multi
    def button_display_withholding_amount(self):
        ctx = dict(self._context)
        if ctx is None:
            ctx = {}
        for t_id in self._ids:
            prev_wht_amount = self._model.browse(self._cr, self._uid, t_id, context=ctx).wht_amount
            wt_amount, t_invoice_id = self._model._get_wht_amount(self._cr, self._uid, t_id, ctx=ctx)
            if t_invoice_id:
                set_amount = wt_amount or 0.0
                if set_amount != prev_wht_amount:
                    self._model.write(self._cr, self._uid, [t_invoice_id], {'wht_amount': set_amount }, context=ctx)
        return True

    def _get_wht_amount(self, cr, uid, res_id, ctx):
        inv_data = self.browse(cr, uid, res_id, context=ctx)
        wt_amount = 0.0
        t_invoice_id = inv_data.id or False
        t_account_id = inv_data.partner_id.wht_account_id or False
        
        if (inv_data.type == 'in_invoice' and t_account_id):
            t_wht_tax_rate = t_account_id.wht_tax_rate / 100
            t_wht_base = t_account_id.wht_base_amount / 100            
            for line in inv_data.invoice_line:
                if (line.product_id.has_wht == True):
                    t_price_unit = line.price_unit
                    t_quantity = line.quantity
                    wt_amount = wt_amount + t_quantity * t_price_unit * t_wht_tax_rate * t_wht_base
        return wt_amount, t_invoice_id

    @api.multi
    def onchange_partner_id(self, type, partner_id,
                                date_invoice=False, payment_term=False,
                                partner_bank_id=False, company_id=False):
        """
                Extends the onchange.
        """
        result = super(account_invoice_makeover,
                       self).onchange_partner_id(type, partner_id,
                                                 date_invoice=date_invoice,
                                                 payment_term=payment_term,
                                                 partner_bank_id=partner_bank_id,
                                                 company_id=company_id)

        self.button_display_withholding_amount()

        bank_id = None
        if partner_id and type in ('out_invoice', 'out_refund'):
                t_partner_data = self.pool.get('res.partner').browse(self._cr, self._uid, partner_id)
                if t_partner_data.bank_ids:
                    bank_id = t_partner_data.bank_ids[0].id
        if 'value' in result:
            result['value']['bank_account'] = bank_id
        return result

    def _net_pay(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            res[invoice.id] = invoice.amount_total - invoice.wht_amount
        return res

    def _has_withholding(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            res[invoice.id] = True if (invoice.wht_amount > 0) else False
        return res

    def _wht_code(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            res[invoice.id] = ''
            if invoice.partner_id and invoice.partner_id.wht_account_id:
                t_wht_name = invoice.partner_id.wht_account_id.name
                t_wht_descr = invoice.partner_id.wht_account_id.description
                res[invoice.id] = t_wht_name + "  " + t_wht_descr
        return res

    def _wht_tax_rate(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            res[invoice.id] = invoice.partner_id.wht_account_id.wht_tax_rate
        return res

    def _wht_base_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            t_base_amount = invoice.partner_id.wht_account_id.wht_base_amount
            res[invoice.id] = t_base_amount
        return res
    
    def _default_last_date_registration(self, cr, uid, context=None):

        t_type = context.get('type', None)
        if not t_type:
            t_type = context.get('inv_type', None)
        datetime_today = datetime.strptime(fields.date.context_today(self, cr, uid, context=context), tools.DEFAULT_SERVER_DATE_FORMAT)
        if not t_type:
            return datetime_today.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        if t_type in ['out_invoice', 'out_refund']:
            return datetime_today.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

        invoice_ids = self.search(cr, uid,
                                  [('partner_id.supplier', '=', True),
                                   ('type', 'in', ['in_invoice']),
                                   ('state', 'not in', ['cancel'])],
                                  limit=1,
                                  order='id desc')
        t_invoice = None
        if invoice_ids:
            t_invoice = self.read(cr, uid, invoice_ids[0], ['registration_date'])
            if t_invoice['registration_date']:
                return t_invoice['registration_date']

        return datetime_today.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

    def onchange_registration_date(self, cr, uid, ids, date_invoice, registration_date, context=None):
        warning = {}
        if(date_invoice and date_invoice and (date_invoice > registration_date)):
            warning = {
                       'title': _('Warning!'),
                       'message': _('Document Date must be less then Registration Date')
                       }
        return {'value': {},
                'warning': warning,
                 }

    def _get_withholding_maturity_term(self, cr, uid):
        p_term_obj = self.pool.get('account.payment.term')
        p_term_search = p_term_obj.search(cr, uid,
                                          [('name', '=',
                                            '16th Next Month')],
                                          limit=1)
        if not p_term_search:
            raise orm.except_orm(_('Error!'),
                (_('Payment term "16th Next Month" missing!')))

        p_term_data = p_term_obj.browse(cr, uid, p_term_search[0],
                                           context=False)

        if not p_term_data.line_ids:
            raise orm.except_orm(_('Error!'),
                (_('Il calcolo del termine di pagamento "%s" non è corretto!' % p_term_data.name)))

        return p_term_data.id

    def _get_wht_due_line(self, cr, uid, invoice, pterm_list):
        date_maturity_list = []
        for t_line in pterm_list:
            t_date_maturity = t_line[0]
            date_maturity_list.append(t_date_maturity)
        
        t_min_payment_term = min(string for string in date_maturity_list)
        t_currency_name = invoice.currency_id.name
        p_term_id = self._get_withholding_maturity_term(cr, uid)
        pt_obj = self.pool.get('account.payment.term')
        t_wht_amount = invoice.wht_amount
        t_wht_pterm_list = pt_obj.compute(cr, uid, p_term_id,
                                      t_wht_amount,
                                      date_ref=t_min_payment_term or False)
        t_date = t_wht_pterm_list[0][0]
        
        t_date_check = self.pool.get('account.payment.term').check_if_holiday(t_date)
        
        t_new_pterm = {
            'date':t_date_check,
            'amount':invoice.wht_amount,
            'currency_name':t_currency_name}
        return t_new_pterm

    @api.onchange('payment_term','date_invoice','amount_total')
    def onchange_paymentterm(self):
        
        if not self.payment_term:
            return
        payment_term = self.payment_term.id
        date_invoice = self.date_invoice
        amount_total = self.amount_total
        
        p_type = _('Not specified')
        payments_preview = []
        invoice = self
        t_amount_total = amount_total
        if hasattr(invoice, 'has_wht') and invoice.has_wht:
            t_amount_total = invoice.net_pay
        obj_pt = self.pool.get('account.payment.term')
        if payment_term:
            p_type = obj_pt.name_get(self._cr, self._uid, [payment_term], self._context)[0][1]
            pterm_list = obj_pt.compute(self._cr, self._uid, payment_term,
                                        t_amount_total, date_ref=date_invoice)
            if pterm_list:
                for line in pterm_list:
                    t_pline = self._get_preview_line(invoice, line)
                    payments_preview.append(t_pline)

                if hasattr(invoice, 'has_wht') and invoice.has_wht:
                    t_new_pterm = self._get_wht_due_line(self._cr, self._uid,
                                                      invoice, pterm_list)
                    payments_preview.append(t_new_pterm)

        self.payments_preview = payments_preview
        self.payment_term = payment_term
        
    def _get_preview_line(self, invoice, line):
        currency_name = invoice.currency_id.name

        t_pterm = {
                   'date': line[0],
                   'amount': line[1],
                   'currency_name': currency_name}
        return t_pterm

    def _protocol_number(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for invoice_data in self.browse(cr, uid, ids):
            res[invoice_data.id] = ''
            if invoice_data.move_id:
                move_data = invoice_data.move_id
                if move_data.protocol_number:
                    res[invoice_data.id] = move_data.protocol_number
        return res

    def _get_payments_overview(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids):
            result[invoice.id] = []
            if invoice.move_id:
                for line in invoice.move_id.line_id:
                    if line.date_maturity:
                        result[invoice.id].append(line.id)
        return result

    @api.model
    def _default_journal(self):
        jour_obj = self.pool.get('account.journal')

        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]                
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        company_id = self.pool.get('res.company').browse(self._cr, self._uid, company_id, context=self._context)
        cmp_id = company_id.id
        
        if inv_type == 'out_invoice':
            if company_id.sale_journal_default:
                return company_id.sale_journal_default
            else:
                return self.env['account.journal'].search([('type','=','sale'),('company_id','=', cmp_id)], limit=1)
                
        if inv_type == 'in_invoice':
            if company_id.purchase_journal_default:
                return company_id.purchase_journal_default
            else:
                return self.env['account.journal'].search([('type','=','purchase'),('company_id','=', cmp_id)], limit=1)
                
        if inv_type == 'out_refund':
            if company_id.sale_refund_journal_default:
                return company_id.sale_refund_journal_default     
            else:
                return self.env['account.journal'].search([('type','=','sale_refund'),('company_id','=', cmp_id)], limit=1)
                       
        if inv_type == 'in_refund':
            if company_id.purchase_refund_journal_default:
                return company_id.purchase_refund_journal_default
            else:
                return self.env['account.journal'].search([('type','=','purchase_refund'),('company_id','=', cmp_id)], limit=1)
        return None


    _columns = {
        'journal_id': fields.many2one('account.journal', string='Journal', required=True, readonly=True, 
                                      states={'draft': [('readonly',False)]},
                                      domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale_refund'], 'in_refund': ['purchase_refund'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]"),            
        'bank_account': fields.many2one('res.partner.bank',
                                    'Bank Account of Client',
                                    readonly=True,
                                    states={'draft':[('readonly', False)]}),
        'partner_bank_id': fields.many2one('res.partner.bank',
                                    'Company Bank', readonly=True,
                                    states={'draft':[('readonly', False)]}),
        'document_number': fields.char('Document Number',
                                    size=64),
        'registration_date':fields.date('Registration Date',
                                    states={'draft': [('readonly', False)],
                                            'paid': [('readonly', True)],
                                            'open' :[('readonly', True)],
                                            'close': [('readonly', True)]},
                                    select=True),
        'f_protocol_number': fields.function(_protocol_number,
                                    store=False,
                                    type="char",
                                    string="Protocol Number"),
        'force_protocol_number': fields.integer(string="Forza Numero Protocollo",copy=False),
        'protocol_date': fields.date('Protocol Date'),

        'wht_amount': fields.float('(-) Withholding amount',
                                    digits_compute=dp.get_precision('Account'),
                                    readonly=True,
                                    states={'draft':[('readonly', False)]}),
        'has_wht': fields.function(_has_withholding, type="boolean"),
        'net_pay': fields.function(_net_pay, type="float", string="Net Pay"),
        'wht_code': fields.function(_wht_code,
                                    readonly=True,
                                    type="char",
                                    string="Withholding Tax Code"),
        'wht_tax_rate': fields.function(_wht_tax_rate,
                                        type="float",
                                        string="Withholding Tax Rate"),
        'wht_base_amount': fields.function(_wht_base_amount,
                                           type="float",
                                           string="Withholding Base Amount"),
        'payments_preview': fields.one2many('account.invoice.maturity.preview.lines', 
                                            'invoice_id', 
                                            'Maturities preview (calculated at invoice validation time)'),

        'payments_overview':  fields.function(_get_payments_overview,
                                              type="one2many",
                                              relation='account.move.line',
                                              string="Payments overview",
                                              readonly=True),

        'recompute_values': fields.boolean('Ricalcola Importi al Salvataggio'),
        'is_autoinvoice': fields.boolean('Autofattura'),
        'ref_autoinvoice': fields.many2one('account.invoice',
                                    'Rif. Autofattura'),
    }

    _defaults = {
        'registration_date': _default_last_date_registration,
        'date_invoice': _default_last_date_registration,
        'recompute_values': True,
        'is_autoinvoice': False,
        'force_protocol_number': None,
        'journal_id':_default_journal,
    }

    @api.multi
    def onchange_company_id(self, company_id, part_id, inv_type, invoice_line, currency_id):

        res = super(account_invoice_makeover,self).onchange_company_id(company_id, part_id, inv_type, invoice_line, currency_id)
        if res and 'value' in res:

            if company_id and inv_type:
                company = self.env['res.company'].browse(company_id)
                journal = None
                if inv_type == 'out_invoice':
                    if company.sale_journal_default:
                        journal = company.sale_journal_default
                    else:
                        journal = self.env['account.journal'].search([('type','=','sale'),('company_id','=', company_id)], limit=1)
                        
                if inv_type == 'in_invoice':
                    if company.purchase_journal_default:
                        journal = company.purchase_journal_default
                    else:
                        journal = self.env['account.journal'].search([('type','=','purchase'),('company_id','=', company_id)], limit=1)
                        
                if inv_type == 'out_refund':
                    if company.sale_refund_journal_default:
                        journal = company.sale_refund_journal_default     
                    else:
                        journal = self.env['account.journal'].search([('type','=','sale_refund'),('company_id','=', company_id)], limit=1)
                               
                if inv_type == 'in_refund':
                    if company.purchase_refund_journal_default:
                        journal = company.purchase_refund_journal_default
                    else:
                        journal = self.env['account.journal'].search([('type','=','purchase_refund'),('company_id','=', company_id)], limit=1)
                if journal:   
                    res['value'].update({'journal_id':journal.id})
        return res

    def invoice_validate(self, cr, uid, ids, context=None):

        res = super(account_invoice_makeover, self).invoice_validate(cr, uid, ids,
                                                             context=context)
        if res:
            t_invoices_data = self.browse(cr, uid, ids, context=context)
            for t_invoice_data in t_invoices_data:
                t_move_id = t_invoice_data.move_id.id
                t_date_invoice = t_invoice_data.date_invoice
                t_registration_date = t_invoice_data.registration_date
                t_document_number = t_invoice_data.document_number

                if not t_invoice_data.f_protocol_number and not t_invoice_data.force_protocol_number:
                    obj_seq = self.pool.get('ir.sequence')
                    t_seq_id = t_invoice_data.journal_id.iva_registry_id.sequence_iva_registry_id.id
    
                    number_next = obj_seq.next_by_id(cr, uid, t_seq_id)

                    self.pool.get('account.move').write(cr, uid,
                                                       [t_move_id],
                                                       {
                                                        'date': t_registration_date,
                                                        'document_date': t_date_invoice,
                                                        'document_number': t_document_number,
                                                        'protocol_number': number_next,
                                                        })
                elif t_invoice_data.force_protocol_number and not t_invoice_data.move_id.protocol_number:
                    self.pool.get('account.move').write(cr, uid,
                                                       [t_move_id],
                                                       {
                                                        'date': t_registration_date,
                                                        'document_date': t_date_invoice,
                                                        'document_number': t_document_number,
                                                        'protocol_number': str(t_invoice_data.force_protocol_number),
                                                        })
                else:
                    if not t_invoice_data.force_protocol_number and not t_invoice_data.move_id.protocol_number:
                        self.pool.get('account.move').write(cr, uid,
                                                           [t_move_id],
                                                           {
                                                            'date': t_registration_date,
                                                            'document_date': t_date_invoice,
                                                            'document_number': t_document_number,
                                                            'protocol_number': t_invoice_data.f_protocol_number,
                                                            })
        return res

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        pay_wizard = super(account_invoice_makeover,self).invoice_pay_customer(cr, uid, ids, context=None)
        inv = self.browse(cr, uid, ids[0], context=context)
        if (inv.type == 'in_invoice'):
            pay_wizard['context']['default_amount'] = inv.net_pay
        return pay_wizard

    def invoice_open(self, cr, uid, ids, context=None):
        for t_id in ids:
            workflow.trg_validate(uid, 'account.invoice', t_id, 'invoice_open', cr)
        return True
