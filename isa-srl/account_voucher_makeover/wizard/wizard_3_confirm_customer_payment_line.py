# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ISA s.r.l. (<http://www.isa.it>).
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


class wizard_confirm_customer_payment_line(orm.TransientModel):
    
    _name = 'wizard.confirm.customer.payment.line'
    _description = 'Wizard Confirm Customer Payment Line'

    def _sign_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            t_move_line = self.pool.get('account.move.line').browse(cr, uid, line.move_line_id.id) 
            if(t_move_line.debit > 0):
                res[line.id] = line.amount_partial
            else: 
                res[line.id] = -line.amount_partial
        return res

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', select=1),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('valid', 'Valid')], 'State'),
        'is_selected': fields.selection([
            ('draft', 'Draft'),
            ('accepted', 'Accepted'),
            ('valid', 'Valid')], 'Selection Type'),
        'account_id': fields.many2one('account.account', 'Account', select=1),
        'confirm_payment_id': fields.many2one('wizard.confirm.customer.payment',
                                         'Confirm Customer Payment',
                                         ondelete="cascade",
                                         required=True),
        'payment_type': fields.selection([('C', 'Cash'),
                                                  ('B', 'Bank Transfer'),
                                                  ('D', 'Bank Draft')],
                                                 'Payment Type',
                                                 readonly=True),
        'move_line_id': fields.many2one('account.move.line', 'Journal Item'),
        'amount':fields.float('Amount'),
        'amount_partial':fields.float('Amount Partial'),
        'fnct_amount': fields.function(_sign_amount,
                                  string='Amount Partial',
                                  type='float'),
        'currency_date': fields.date('Currency Date'),
        'document_number': fields.related('move_line_id',
                                          'move_id',
                                          'document_number',
                                           type='char',
                                           relation='account.move',
                                           string='Document Number',
                                           readonly=1),
        'amount_allowance': fields.float('Amount allowance'),
        'allowance': fields.boolean('allowance'),
        'partner_bank_id': fields.many2one('res.partner.bank',
                                           'Partner Bank'),
    }
    
    _defaults = {
                 'amount_allowance': 0.0,
                 'allowance': False,
                 'partner_bank_id': None
                 }

    def set_partial_amount(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_customer_set_partial_amount_account_voucher_makeover_view')
        
        t_line = self.browse(cr, uid, ids[0])
        context.update({
            'default_line_id': t_line.id,
            'default_amount_partial': t_line.amount_partial,
            'default_amount_initial': t_line.amount,
            'default_amount_residual': t_line.amount,
            'default_allowance': t_line.allowance,
            'default_partner_id': t_line.partner_id.id,
            'default_partner_bank_id': t_line.partner_bank_id.id,
            'default_payment_type': t_line.payment_type
        })
        view_id = result and result[1] or False

        return {
              'name': _("Conferma Impostazione Valori"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.customer.set.partial.amount',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'target': 'new',
              }

    def delete_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        line_id = context.get('line_id', None)
        data = self.browse(cr, uid, line_id, context=context)
        t_maturity = data.confirm_payment_id.maturity
        t_journal = data.confirm_payment_id.journal_id.id
        t_all_customer = data.confirm_payment_id.all_customer
        t_it_customer = data.confirm_payment_id.it_customer
        t_ext_customer = data.confirm_payment_id.ext_customer
        t_riba = data.confirm_payment_id.riba
        t_period = data.confirm_payment_id.period_id.id
        t_bank = data.confirm_payment_id.bank_id.id
        t_wizard = data.confirm_payment_id.id
        t_operation_date = data.confirm_payment_id.operation_date
        t_currency_date = data.confirm_payment_id.currency_date
        t_partner = None
        if not t_all_customer:
            t_partner = data.confirm_payment_id.partner_id.id

        t_state = 'valid'

        draft_obj = self.pool.get('account.move.line')
        t_move_id = data.move_line_id.id
        draft_obj.write(cr, uid, [t_move_id], {
            'state': t_state,
            'is_selected': None,
        })

        context.update({
            'default_partner_id': t_partner,
            'default_journal_id': t_journal,
            'default_maturity': t_maturity,
            'default_all_customer': t_all_customer,
            'default_it_customer': t_it_customer,
            'default_ext_customer': t_ext_customer,
            'default_riba': t_riba,
            'default_period_id': t_period,
            'default_bank_id': t_bank,
            'default_wizard_id': t_wizard,
            'default_operation_date': t_operation_date,
            'default_currency_date': t_currency_date,
        })

        res_id = self.set_confirm_payment_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_confirm_customer_payment_view')
        view_id = result and result[1] or False

        return {
              'name': _("Confirm Customer Payment Action"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.confirm.customer.payment',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }

    def set_confirm_payment_lines(self, cr, uid, context=None):

        t_lines = []
        list_partner = []
        vals = {}

        context_partner_id = context.get('default_partner_id', None)
        t_journal_id = context.get('default_journal_id', None)
        t_all_customers = context.get('default_all_customer', None)
        t_it_customers = context.get('default_it_customer', None)
        t_ext_customers = context.get('default_ext_customer', None)
        t_maturity = context.get('default_maturity', None)
        t_wizard = context.get('default_wizard_id', None)
        t_operation_date = context.get('default_operation_date', None)
        t_currency_date = context.get('default_currency_date', None)

        vals['partner_id'] = context_partner_id
        vals['maturity'] = t_maturity
        vals['journal_id'] = t_journal_id
        vals['all_customer'] = t_all_customers
        vals['it_customer'] = t_it_customers
        vals['ext_customer'] = t_ext_customers
        vals['operation_date'] = t_operation_date
        vals['currency_date'] = t_currency_date
        list_partner.append(context_partner_id)
        if(t_all_customers):
            customer_filter = []
            f = ('customer', '=', True)
            customer_filter.append(f)
            if(t_it_customers):
                t_country_obj = self.pool.get('res.country')
                t_italy_id = t_country_obj.search(cr, uid, [('name', '=', 'Italy')])
                f = ('country_id', '=', t_italy_id)
                customer_filter.append(f)
            if(t_ext_customers):
                t_country_obj = self.pool.get('res.country')
                t_italy_id = t_country_obj.search(cr, uid, [('name', '=', 'Italy')])
                f = ('country_id', '!=', t_italy_id)
                customer_filter.append(f)
            if(len(customer_filter) > 1):
                customer_filter.insert(0, '&')
            list_partner = []
            vals['partner_id'] = None
            list_partner = self.pool.get('res.partner').search(cr, uid, customer_filter)

        res_id = self.pool.get('wizard.confirm.customer.payment').create(cr, uid, vals, context=context)

        for t_partner_id in list_partner:
            vals = {}
            t_filter2 = ['&', ('partner_id', '=', t_partner_id), ('move_line_id.is_selected', '=', 'accepted'), ('confirm_payment_id', '=', t_wizard)]

            wizard_line_ids = self.search(cr, uid, t_filter2, context=context)

            if(wizard_line_ids and len(wizard_line_ids) > 0):
                for line_id in self.browse(cr, uid, wizard_line_ids):
                    t_move_line = line_id.move_line_id
                    t_state = t_move_line.state
                    t_lines.append((0, 0, {
                                          'partner_id': t_move_line.partner_id.id,
                                          'account_id': t_move_line.account_id.id,
                                          'state': t_state,
                                          'move_line_id': t_move_line.id,
                                          'confirm_payment_id': res_id,
                                          'amount': line_id.amount,
                                          'amount_partial': line_id.amount_partial,
                                          'payment_type': line_id.payment_type,
                                          'partner_bank_id': line_id.partner_bank_id.id,
                                          'allowance': line_id.allowance,
                                          'amount_allowance': line_id.amount_allowance
                                          }))
            
        self.pool.get('wizard.confirm.customer.payment').write(cr, uid, [res_id], {'line_ids': t_lines})

        return res_id
