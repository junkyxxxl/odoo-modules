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


class wizard_payment_specification_line(orm.TransientModel):
    _name = 'wizard.payment.specification.line'
    _description = 'Wizard Payment Specification Line'
    
    def _sign_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            t_move_line = self.pool.get('account.move.line').browse(cr, uid, line.move_line_id.id) 
            if(t_move_line.credit > 0):
                res[line.id] = line.amount
            else: 
                res[line.id] = -line.amount
        return res

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Supplier', select=1),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('valid', 'Valid')], 'State'),
        'is_selected': fields.selection([
            ('draft', 'Draft'),
            ('accepted', 'Accepted'),
            ('valid', 'Valid')], 'Selection Type'),
        'account_id': fields.many2one('account.account', 'Account', select=1),
        'payment_specification_id': fields.many2one('wizard.payment.specification',
                                         'Payment Specification',
                                         ondelete="cascade",
                                         required=True),
        'date_original': fields.related('move_line_id', 'date', type='date', relation='account.move.line', string='Original Date', readonly=1),
        'date_due': fields.related('move_line_id', 'date_maturity', type='date', relation='account.move.line', string='Due Date', readonly=1),
        'payment_type': fields.selection([('C', 'Cash'),
                                                  ('B', 'Bank Transfer'),
                                                  ('D', 'Bank Draft')],
                                                 'Payment Type',
                                                 readonly=True),
        'move_line_id': fields.many2one('account.move.line', 'Journal Item'),
        'amount':fields.float('Amount'),
        'fnct_amount': fields.function(_sign_amount,
                                  string='Amount',
                                  type='float'),
        'document_number': fields.related('move_line_id', 'move_id', 'document_number', type='char', relation='account.move', string='Document Number', readonly=1),
    }

    def set_payment_lines(self, cr, uid, context=None):
        
        wizard_obj = self.pool.get('wizard.payment.specification')
        account_move_line_obj = self.pool.get('account.move.line')
        wizard_sup_obj = self.pool.get('wizard.supplier.payment')
        res_partner_obj = self.pool.get('res.partner')
        
        list_partner = []
        t_limit = 50
        t_lines = []
        t_all_supplier = False
        
        t_partner_id = context.get('default_partner_id', None)
        t_page = context.get('default_actual_page', None)

        if(t_partner_id):
            list_partner.append(t_partner_id)
        else:
            s_filters = wizard_obj.get_wizard_supplier_filters(cr, uid, context)
            list_partner = res_partner_obj.search(cr, uid, s_filters)
            t_all_supplier = True

        v_filters = wizard_obj.get_wizard_filters(cr, uid, list_partner, context)
        v_filters.append(('|'))
        v_filters.append(('is_selected', '=', None))
        v_filters.append(('is_selected', '!=', 'accepted'))
        
        t_total_pages = wizard_sup_obj.get_total_pages(cr, uid, v_filters, t_limit)
        
        if(t_page > t_total_pages or t_total_pages == 1):
            t_page = t_total_pages
            context.update({
                            'default_actual_page': t_page,
                           })
        
        t_offset = t_limit * (t_page - 1)
        
        res_id = wizard_obj.create(cr, uid, {
                                             'all_supplier': t_all_supplier,
                                             'total_pages': t_total_pages,
                                             }, context)
        
        account_move_line_valid_ids = account_move_line_obj.search(cr, uid, v_filters,
                                                             order='date_maturity, id',
                                                             limit=t_limit,
                                                             offset=t_offset,
                                                             context=context)
        for t_move_line in account_move_line_obj.browse(cr, uid, account_move_line_valid_ids):
            t_state = t_move_line.state
            t_is_selected = t_move_line.is_selected
            t_is_in_invoice = wizard_obj.check_move_line_in_invoice(cr, uid, [t_move_line.id], context)
            if(t_is_in_invoice):
                t_lines.append((0, 0, {
                                   'partner_id': t_move_line.partner_id.id,
                                   'account_id': t_move_line.account_id.id,
                                   'state': t_state,
                                   'is_selected': t_is_selected,
                                   'move_line_id': t_move_line.id,
                                   'payment_specification_id': res_id,
                                   'amount': t_move_line.amount_residual_currency,
                                   'payment_type': t_move_line.payment_type_move_line
                                    }))
        wizard_obj.write(cr, uid, [res_id], {'draft_ids': t_lines, })

        t_lines = []
        t_filters = wizard_obj.get_wizard_filters(cr, uid, list_partner, context)
        t_filters.append(('is_selected', '=', 'accepted'))
        account_move_line_accepted_ids = account_move_line_obj.search(cr, uid, t_filters,
                                                             order='date_maturity, id',
                                                             context=context)
        for t_move_line in account_move_line_obj.browse(cr, uid, account_move_line_accepted_ids):
            t_state = t_move_line.state
            t_is_selected = t_move_line.is_selected
            t_is_in_invoice = wizard_obj.check_move_line_in_invoice(cr, uid, [t_move_line.id], context)
            if(t_is_in_invoice):
                t_lines.append((0, 0, {
                                   'partner_id': t_move_line.partner_id.id,
                                   'account_id': t_move_line.account_id.id,
                                   'state': t_state,
                                   'is_selected': t_is_selected,
                                   'move_line_id': t_move_line.id,
                                   'payment_specification_id': res_id,
                                   'amount': t_move_line.amount_residual_currency,
                                   'payment_type': t_move_line.payment_type_move_line
                                    }))
        wizard_obj.write(cr, uid, [res_id], {'accepted_draft_ids': t_lines, })
        return res_id
 
    def move_draft(self, fb, cr, uid, ids, context=None):
        if context is None:
            context = {}

        line_id = context.get('line_id', None)
        data = self.browse(cr, uid, line_id, context=context)
        t_maturity = data.payment_specification_id.maturity
        t_bank = data.payment_specification_id.bank_id.id
        t_journal = data.payment_specification_id.journal_id.id
        t_all_supplier = data.payment_specification_id.all_supplier
        t_it_supplier = data.payment_specification_id.it_supplier
        t_ext_supplier = data.payment_specification_id.ext_supplier
        t_page = data.payment_specification_id.actual_page

        t_partner = None
        if not t_all_supplier:
            t_partner = data.payment_specification_id.partner_id.id

        t_state = 'valid'
        if fb:
            t_state = 'accepted'

        draft_obj = self.pool.get('account.move.line')
        t_move_id = data.move_line_id.id
        draft_obj.write(cr, uid, [t_move_id], {
            'is_selected': t_state,
        })
        t_move = data.move_line_id.move_id
        wht_lines = draft_obj.search(cr, uid, [('move_id', '=', t_move.id), ('is_wht', '=', True), ('reconcile_id', '=', False)])
        for wht_id in wht_lines:
            draft_obj.write(cr, uid, [wht_id], {
            'is_selected': t_state,
            })

        context.update({
            'default_partner_id': t_partner,
            'default_journal_id': t_journal,
            'default_maturity': t_maturity,
            'default_bank_id': t_bank,
            'default_all_supplier': t_all_supplier,
            'default_it_supplier': t_it_supplier,
            'default_ext_supplier': t_ext_supplier,
            'default_actual_page': t_page,
        })

        res_id = self.set_payment_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_payment_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Wizard Payment Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.payment.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }

    def move_draft_forward(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.move_draft(1, cr, uid, ids, context)

    def move_draft_backward(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.move_draft(0, cr, uid, ids, context)
