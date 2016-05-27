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


class wizard_customer_payment_specification(orm.TransientModel):
    _name = 'wizard.customer.payment.specification'
    _description = 'Wizard Customer Payment Specification'

    def _resume_page(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_wizard in self.browse(cr, uid, ids, context):
            t_actual = str(t_wizard.actual_page)
            t_total = str(t_wizard.total_pages)
            res[t_wizard.id] = t_actual + ' di ' + t_total
        return res

    def _is_last_page(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_wizard in self.browse(cr, uid, ids, context):
            t_actual = t_wizard.actual_page
            t_total = t_wizard.total_pages
            if t_actual == t_total:
                res[t_wizard.id] = True
            else:
                res[t_wizard.id] = False
        return res

    _columns = {
        'partner_id': fields.many2one('res.partner',
                                   'customer'),
        'maturity': fields.date('Maturity Maximum'),
        'journal_id':fields.many2one('account.journal', 'Journal'),
        'draft_ids': fields.one2many(
                              'wizard.customer.payment.specification.line',
                              'payment_specification_id',
                              domain=['|',
                                      ('is_selected', '!=', 'accepted'),
                                      ('is_selected', '=', None)],
                              string="Drafts",
                              readonly=True),
        'accepted_draft_ids': fields.one2many(
                              'wizard.customer.payment.specification.line',
                              'payment_specification_id',
                              domain=[('is_selected', '=', 'accepted')],
                              string="Accepted Drafts",
                              readonly=True),
        'bank_id': fields.many2one('res.partner.bank',
                                   'bank'),
        'all_customer': fields.boolean('All customers'),
        'it_customer': fields.boolean('Italian customers'),
        'ext_customer': fields.boolean('Foreign customers'),
        'riba': fields.boolean('Exclude Riba'),
        'actual_page': fields.integer('Actual Page'),
        'total_pages': fields.integer('Total Pages'),
        'pages_resume': fields.function(_resume_page,
                                  string='Page',
                                  type='text'),
        'is_last_page': fields.function(_is_last_page,
                                  string='Is Last Page',
                                  type='boolean'),
    }
    
    _defaults = {
                 'all_customer': False,
                 'actual_page': 1
                 }

    def get_wizard_customer_filters(self, cr, uid, context=None):
        filters = [('customer', '=', True)]
        t_country_obj = self.pool.get('res.country')
        t_italy_id = t_country_obj.search(cr, uid, [('name', '=', 'Italy')])
        t_it_customers = context.get('default_it_customer')
        t_ext_customers = context.get('default_ext_customer')

        if(t_it_customers and t_ext_customers):
            raise orm.except_orm(_('Error!'), _('Se si vogliono clienti sia Italiani che esteri lasciare vuote le caselle'))

        if(t_it_customers and (not t_ext_customers)):
            f = ('country_id', '=', t_italy_id)
            filters.append(f)

        if(t_ext_customers and (not t_it_customers)):
            f = ('country_id', '!=', t_italy_id)
            filters.append(f)

        if(len(filters) > 1):
            filters.insert(0, '&')

        return filters

    def get_wizard_filters(self, cr, uid, partner_ids, context=None):
        filters = []
        t_maturity = context.get('default_maturity', None)
        t_riba = context.get('default_riba', None)
        company_obj = self.pool.get('res.company')

        voucher_obj = self.pool.get('account.voucher')
        my_company_id = voucher_obj.get_company(cr, uid, context=None)
        my_company = company_obj.browse(cr, uid, my_company_id)

        t_active = my_company.bonus_active_account_id.id
        t_passive = my_company.bonus_passive_account_id.id
        list_account_to_ignore = [t_active, t_passive]
        if ('customer_credit_account_id' in my_company
             and my_company.customer_credit_account_id):
            t_cust_cr_account_id = my_company.customer_credit_account_id.id
            list_account_to_ignore.append(t_cust_cr_account_id)

        if t_maturity:           
            f = ('date_maturity', '<=', t_maturity)
            filters.append(f)
        if(t_riba):           
            f = ('payment_type_move_line', 'not in', ['D'])
            filters.append(f)
        filters.append(('is_wht', '!=', True))
        filters.append(('reconcile_id', '=', None))
        filters.append(('date_maturity', '!=', None))
        filters.append(('debit', '>', 0.0))
        filters.append('!')
        filters.append(('name', 'ilike', 'acconto pagabile'))
        filters.append(('account_id', 'not in', list_account_to_ignore))
        filters.append(('partner_id', 'in', partner_ids))
        return filters

    def check_move_line_out_invoice(self, cr, uid, t_move_line_ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        t_move_line_id = t_move_line_ids[0]
        t_move_line = move_line_obj.browse(cr, uid, t_move_line_id)
        t_move_id = t_move_line.move_id.id
        invoice_ids = invoice_obj.search(cr, uid, [('move_id', '=', t_move_id)])
        if(invoice_ids):
            t_invoice = invoice_obj.browse(cr, uid, invoice_ids[0])
            if (t_invoice.type == 'out_invoice' or t_invoice.type == 'out_refund'):
                return True
            return False
        return True

    def view_new_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_action_customer_payment_view')
        view_id = result and result[1] or False

        return {
              'name': _("Payment Action"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.customer.payment',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'target': 'new',
              }

    def set_confirm_payment_lines(self, cr, uid, ids, context=None):

        wizard_confirm_obj = self.pool.get('wizard.confirm.customer.payment')

        t_lines = []
        vals = {}

        context_partner_id = context.get('default_partner_id', None)
        t_journal_id = context.get('default_journal_id', None)
        t_all_customers = context.get('all_customer', None)
        t_maturity = context.get('default_maturity', None)
        t_it_customers = context.get('it_customer', None)
        t_ext_customers = context.get('ext_customer', None)
        t_riba = context.get('default_riba', None)

        vals['partner_id'] = context_partner_id
        if(t_all_customers):
            vals['partner_id'] = None
        vals['maturity'] = t_maturity
        vals['journal_id'] = t_journal_id
        vals['all_customer'] = t_all_customers
        vals['it_customer'] = t_it_customers
        vals['ext_customer'] = t_ext_customers
        vals['riba'] = t_riba

        res_id = wizard_confirm_obj.create(cr, uid, vals, context=context)

        t_wps = self.browse(cr, uid, ids[0])

        for line in t_wps.accepted_draft_ids:
            t_move_line = line['move_line_id']
            t_state = t_move_line.state
            t_pt = t_move_line.payment_type_move_line
            t_lines.append((0, 0, {
                                   'partner_id': line.partner_id.id,
                                   'account_id': line.account_id.id,
                                   'state': t_state,
                                   'is_selected': 'accepted',
                                   'move_line_id': t_move_line.id,
                                   'confirm_payment_id': res_id,
                                   'amount': line.amount,
                                   'amount_partial': line.amount,
                                   'payment_type': t_pt
                                   }))

        wizard_confirm_obj.write(cr, uid, [res_id], {'line_ids': t_lines})

        return res_id

    def view_confirm_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_confirm_customer_payment_view')
        view_id = result and result[1] or False

        t_ws = self.browse(cr, uid, ids[0])
        if(not t_ws.accepted_draft_ids and len(t_ws.accepted_draft_ids) < 1):
            raise orm.except_orm(_('Error!'),
                                 _('Selezionare almeno una riga se presente'))

        res_id = self.set_confirm_payment_lines(cr, uid, ids, context)

        return {
              'name': _("Confirm Payment Action"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.confirm.customer.payment',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview'
              }

    def action_move_all_forward(self, cr, uid, ids, context=None):
        res = None
        t_spec = self.browse(cr, uid, ids[0])
        line_obj = self.pool.get('wizard.customer.payment.specification.line')
        for line in t_spec.draft_ids:
            context.update({
                            'line_id': line.id
                            })
            res = line_obj.move_draft_forward(cr, uid, ids, context=context)
        return res
    
    def action_move_all_backward(self, cr, uid, ids, context=None):
        res = None
        t_spec = self.browse(cr, uid, ids[0])
        line_obj = self.pool.get('wizard.customer.payment.specification.line')
        for line in t_spec.accepted_draft_ids:
            context.update({
                            'line_id': line.id
                            })
            res = line_obj.move_draft_backward(cr, uid, ids, context=context)
        return res
    
    def move_page(self, cr, uid, ids, context=None):
        wizard_line_obj = self.pool.get('wizard.customer.payment.specification.line')
        data = self.browse(cr, uid, ids[0], context=context)
        t_maturity = data.maturity
        t_bank = data.bank_id.id
        t_journal = data.journal_id.id
        t_all_customer = data.all_customer
        t_it_customer = data.it_customer
        t_ext_customer = data.ext_customer
        t_riba = data.riba
        t_total_pages = data.total_pages
        
        t_skip = context.get('t_skip', None)
        if(data.actual_page == 1 and t_skip == -1):
            raise orm.except_orm(_('Error!'), _('Non puoi andare indietro!'))
        
        if(data.actual_page >= t_total_pages and t_skip == 1):
            raise orm.except_orm(_('Error!'), _("Hai raggiunto l'ultima pagina!"))

        t_page = data.actual_page + t_skip

        t_partner = None
        if not t_all_customer:
            t_partner = data.partner_id.id

        context.update({
            'default_partner_id': t_partner,
            'default_journal_id': t_journal,
            'default_maturity': t_maturity,
            'default_bank_id': t_bank,
            'default_all_customer': t_all_customer,
            'default_it_customer': t_it_customer,
            'default_ext_customer': t_ext_customer,
            'default_riba': t_riba,
            'default_actual_page': t_page,
            'default_total_pages': t_total_pages
        })

        res_id = wizard_line_obj.set_payment_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_customer_payment_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Wizard Customer Payment Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.customer.payment.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }
