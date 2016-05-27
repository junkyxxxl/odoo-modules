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

import time
from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_invoice_intracee(orm.Model):

    _inherit = 'account.invoice'

    def _create_autofattura(self, cr, uid, invoice_id, flag_intracee, context=None):
        acc_move_line_obj = self.pool.get('account.move.line')
        seq_obj = self.pool.get('ir.sequence')

        orig_invoice_data = self.browse(cr, uid, invoice_id, context=None)
        orig_move_data = orig_invoice_data.move_id

        sezionale_autofattura = orig_invoice_data.company_id.reverse_charge_journal_id
        if flag_intracee:
            sezionale_autofattura = orig_invoice_data.company_id.intracee_journal_id

        # creazione di una copia della fattura in account_invoice
        # con le realtive modifiche
        autofattura_invoice_id = self.copy(cr,
                                           uid,
                                           orig_invoice_data.id,
                                           {},
                                           context=None)

        t_autofattura_seq_id = sezionale_autofattura.sequence_id.id
        t_autofattura_number_next = seq_obj.next_by_id(cr, uid, t_autofattura_seq_id, context=context)

        dict_inv = {'journal_id': sezionale_autofattura.id,
                    'move_id': None,
                    'state': 'draft',
                    'date_due': orig_invoice_data.date_due,
                    'date_invoice': orig_invoice_data.date_invoice,
                    'internal_number': t_autofattura_number_next,
                    'move_name': '/',
                    'period_id': orig_invoice_data.period_id.id,
                    'type': 'out_invoice',
                    'name': orig_invoice_data.name or '',
                    'number': t_autofattura_number_next,
                    'is_autoinvoice': True,
                    'ref_autoinvoice': orig_invoice_data.id,
                    }

        self.write(cr, uid, [autofattura_invoice_id], dict_inv, context=None)

        autofattura_lines = self.browse(cr, uid, autofattura_invoice_id).invoice_line
        for line in autofattura_lines:
            t_ids = []
            for tax in line.invoice_line_tax_id:
                if tax.autoinvoice_related_tax:
                    t_ids.append(tax.autoinvoice_related_tax.id)
                else:
                    t_ids.append(tax.id)
            self.pool.get('account.invoice.line').write(cr, uid, line.id, {'invoice_line_tax_id':[(6,0,t_ids)]})        
        self.button_reset_taxes(cr, uid, [autofattura_invoice_id], context=context)
        
        self.invoice_open(cr, uid, [autofattura_invoice_id], context=context)
        self.write(cr, uid, autofattura_invoice_id, {'number': t_autofattura_number_next}, context=context) # TODO è necessario?

        autofattura_line_ids = []
        origfattura_line_ids = []

        autofattura_data = self.pool.get('account.invoice').browse(cr, uid, autofattura_invoice_id)
        for move_line in autofattura_data.move_id.line_id:
            if not move_line.product_id:
                autofattura_line_ids.append(move_line.id)

        for move_line in orig_move_data.line_id:
            if not move_line.product_id:
                origfattura_line_ids.append(move_line.id)

        line_to_reconcile_ids = autofattura_line_ids + origfattura_line_ids

        cr.execute('SELECT account_id, reconcile_id '\
                   'FROM account_move_line '\
                   'WHERE id IN %s AND tax_code_id IS NULL '\
                   'GROUP BY account_id,reconcile_id',
                   (tuple(line_to_reconcile_ids), ))
        r = cr.dictfetchall()

        account_ids = [x['account_id'] for x in r]

        for t_acc in account_ids:
            line_ids = acc_move_line_obj.search(cr, uid,
                                                ['&',
                                                 ('id', 'in', line_to_reconcile_ids),
                                                 ('account_id', '=', t_acc), ],
                                                offset=0, limit=None, order=None,
                                                context=None, count=False)
            acc_move_line_obj.reconcile_partial(cr, uid, line_ids,
                                                type='auto', context=context)
        return autofattura_data.move_id.id

    def _giroconto(self, cr, uid, invoice_id, flag_intracee, auto_move_id=None, context=None):
        acc_move_obj = self.pool.get('account.move')
        acc_move_line_obj = self.pool.get('account.move.line')
        seq_obj = self.pool.get('ir.sequence')

        orig_invoice_data = self.browse(cr,
                                        uid,
                                        invoice_id,
                                        context=None)
        move_giroconto_id = self.giroconto_move_create(cr,
                                                       uid,
                                                       [invoice_id],
                                                       context=None)
        giroconto_obj = self.pool.get('account.move')
        giroconto_data = giroconto_obj.browse(cr, uid, move_giroconto_id)

        t_giro_credit = 0.0
        t_move_line_id = None
        for giro_line_data in giroconto_data.line_id:
            if not giro_line_data.is_wht and giro_line_data.debit == 0.0:
                t_giro_credit = giro_line_data.credit
                t_move_line_id = giro_line_data.id
                break

        for giro_line_data in giroconto_data.line_id:
            acc_move_line_obj.write(cr, uid,
                                    giro_line_data.id,
                                    {'tax_code_id': None,
                                     'tax_amount':0.0,
                                     })

        acc_move_line_obj.write(cr, uid,
                                [t_move_line_id],
                                {'credit': t_giro_credit,
                                 })

        sezionale_giroconto = orig_invoice_data.company_id.reverse_charge_giro_credit
        if flag_intracee:
            sezionale_giroconto = orig_invoice_data.company_id.intracee_giro_credit

        t_giroconto_number_next = orig_invoice_data.move_id.name
        t_giroconto_seq_id = sezionale_giroconto.sequence_id.id

        # impedire calcolo next_by_id per giroconto nel caso
        # t_giroconto_seq_id == orig_invoice_data.journal_id.sequence_id.id
        if t_giroconto_seq_id != orig_invoice_data.journal_id.sequence_id.id:
            t_giroconto_number_next = seq_obj.next_by_id(cr, uid, t_giroconto_seq_id, context=context)

        acc_move_obj.write(cr, uid,
                           [move_giroconto_id],
                           {'name': t_giroconto_number_next,
                            'partner_id': orig_invoice_data.move_id.partner_id.id,
                            'company_id': orig_invoice_data.move_id.company_id.id,
                            'period_id': orig_invoice_data.move_id.period_id.id,
                            'narration': orig_invoice_data.move_id.narration,
                            'balance': orig_invoice_data.move_id.balance,
                            'date': orig_invoice_data.move_id.date,
                            'document_date': orig_invoice_data.date_invoice,
                            'ref': orig_invoice_data.move_id.ref,
                            'to_check': orig_invoice_data.move_id.to_check,
                            'journal_id': sezionale_giroconto.id,
                            'document_number': orig_invoice_data.number,
                            })

        # validazione degli altri record rimanenti
        acc_move_obj.validate(cr, uid, [move_giroconto_id], context=context)

        for giro_line_data in giroconto_data.line_id:
            acc_move_line_obj.write(cr, uid,
                                    giro_line_data.id,
                                    {'intra_move_originator_id': orig_invoice_data.move_id.id,
                                     'auto_move_originator_id': auto_move_id,
                                     })

        ctx = context.copy()
        ctx.update({'invoice': orig_invoice_data})
        acc_move_obj.post(cr, uid, [move_giroconto_id], context=ctx)

    def invoice_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {} 
        ctx = {}
        for item in context.items():
            ctx[item[0]] = item[1]      
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(account_invoice_intracee,
                    self).invoice_validate(cr, uid, ids, context=None)
        t_invoice_data = self.browse(cr, uid, ids, context=None)
        for t_invoice in t_invoice_data:
            ctx['company_id'] = t_invoice.company_id.id    
            ctx['fiscalyear_id'] = t_invoice.period_id.fiscalyear_id.id  
            if t_invoice.fiscal_position and t_invoice.type == 'in_invoice':
                flag_intracee = self.check_intracee(cr, uid, t_invoice.fiscal_position.id, context=ctx)
                flag_reverse_charge = self.check_reverse_charge(cr, uid, t_invoice.fiscal_position.id, context=ctx)
                if flag_intracee or flag_reverse_charge:

                    # Creazione autofattura
                    auto_move_id = self._create_autofattura(cr, uid, t_invoice.id, flag_intracee, context=ctx)

                    # giroconto
                    self._giroconto(cr, uid, t_invoice.id, flag_intracee, auto_move_id, context=ctx)
        return res

    def action_move_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        t_invoice_data = self.browse(cr, uid, ids, context=context)
        for t_invoice in t_invoice_data:
            ctx = {}
            for item in context.items():
                ctx[item[0]] = item[1]
            ctx['company_id'] = t_invoice.company_id.id

            if not t_invoice.company_id:
                raise orm.except_orm(_('Error!'),
                                     _('Company for this invoice not defined!'))
            if (t_invoice.fiscal_position
                    and t_invoice.type == 'in_invoice'
                    and self.check_intracee(cr, uid, t_invoice.fiscal_position.id, context=ctx)):

                if (hasattr(t_invoice, 'has_wht') and t_invoice.has_wht):
                    raise orm.except_orm(_('Error!'),
                                         _('La ritenuta d\'acconto non è gestibile con una Fattura Intracee!'))
                if not t_invoice.company_id.intracee_journal_id:
                    raise orm.except_orm(_('Error!'),
                                         _('Sezionale Autofattura Intracee non definito per questa Azienda!'))
                if not t_invoice.company_id.intracee_giro_credit:
                    raise orm.except_orm(_('Error!'),
                                         _('Sezionale Giroconto Intracee non definito per questa Azienda!'))
                if not(t_invoice.company_id.intracee_journal_id.iva_registry_id):
                    raise orm.except_orm(_('Error!'),
                                         _('Before validating an invoice you have to link %s with a VAT registry!') % (t_invoice.company_id.intracee_giro_credit.name))
                if t_invoice.company_id.intracee_giro_credit.iva_registry_id:
                    raise orm.except_orm(_('Error!'),
                                         _('Journal %s should not be linked with a VAT registry!') % (t_invoice.company_id.intracee_giro_credit.name))
            if (t_invoice.fiscal_position
                    and t_invoice.type == 'in_invoice'
                    and self.check_reverse_charge(cr, uid, t_invoice.fiscal_position.id, context=ctx)):

                if (hasattr(t_invoice, 'has_wht') and t_invoice.has_wht):
                    raise orm.except_orm(_('Error!'),
                                         _('La ritenuta d\'acconto non è gestibile con una Fattura Reverse Charge!'))
                if not t_invoice.company_id.reverse_charge_journal_id:
                    raise orm.except_orm(_('Error!'),
                                         _('Sezionale Autofattura Reverse Charge non definito per questa Azienda!'))
                if not t_invoice.company_id.reverse_charge_giro_credit:
                    raise orm.except_orm(_('Error!'),
                                         _('Sezionale Giroconto Reverse Charge non definito per questa Azienda!'))
                if not(t_invoice.company_id.reverse_charge_journal_id.iva_registry_id):
                    raise orm.except_orm(_('Error!'),
                                         _('Before validating an invoice you have to link %s with a VAT registry!') % (t_invoice.company_id.reverse_charge_giro_credit.name))
                if t_invoice.company_id.reverse_charge_giro_credit.iva_registry_id:
                    raise orm.except_orm(_('Error!'),
                                         _('Journal %s should not be linked with a VAT registry!') % (t_invoice.company_id.reverse_charge_giro_credit.name))
        res = super(account_invoice_intracee,
                    self).action_move_create(cr, uid, ids, context=None)
        return res

    def giroconto_move_create(self, cr, uid, ids, context=None):

        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):

            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id],
                           {'date_invoice': fields.date.context_today(self,
                                                                      cr,
                                                                      uid,
                                                                      context=context)},
                           context=ctx)
            company_currency = self.pool['res.company'].browse(cr, uid,
                                                               inv.company_id.id).currency_id

            # create the analytical lines
            # one move line per invoice line
            iml = super(account_invoice_intracee, self)._get_analytic_lines(cr, uid, inv.id, context=ctx)

            # I disabled the check_total feature
            group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
            group_check_total = self.pool.get('res.groups').browse(cr, uid,
                                                                   group_check_total_id,
                                                                   context=context)
            if group_check_total and uid in [x.id for x in group_check_total.users]:
                if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0)):
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

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = super(account_invoice_intracee, self)._convert_ref(cr, uid, inv.number)

            diff_currency_p = inv.currency_id.id != company_currency.id
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            acc_id = inv.account_id.id

            name = inv['name'] or inv['supplier_invoice_number'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                                                    uid,
                                                    inv.payment_term.id,
                                                    total,
                                                    inv.date_invoice or False,
                                                    context=ctx)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                for t_line in totlines:
                    if inv.currency_id.id != company_currency.id:
                        amount_currency = cur_obj.compute(cr, uid,
                                                          company_currency,
                                                          inv.currency_id.id,
                                                          t_line[1],
                                                          context=ctx)
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t_line[1],
                        'account_id': acc_id,
                        'date_maturity': t_line[0],
                        'amount_currency': diff_currency_p and amount_currency or False,
                        'currency_id': diff_currency_p and inv.currency_id.id or False,
                        'ref': ref,
                        'payment_type': t_line[2]
                    })
            else:
                iml.append({'type': 'dest',
                            'name': name,
                            'price': total,
                            'account_id': acc_id,
                            'date_maturity': inv.date_due or False,
                            'amount_currency': diff_currency_p and total_currency or False,
                            'currency_id': diff_currency_p and inv.currency_id.id or False,
                            'ref': ref,
                            'payment_type': None
                            })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')

            part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

            line = map(lambda x: (0, 0, self.line_get_convert(cr, uid, x, part.id, date, context=ctx)), iml)

            line = inv.group_lines(iml, line)

            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise orm.except_orm(_('User Error!'),
                                     _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.registration_date, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id

            ctx.update(invoice=inv)
            move_created = move_obj.create(cr, uid, move, context=ctx)

        return move_created
