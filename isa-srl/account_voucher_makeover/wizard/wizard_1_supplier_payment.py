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


class wizard_supplier_payment(orm.TransientModel):
    _name = 'wizard.supplier.payment'
    _description = 'Wizard Supplier Payment Makover'

    _columns = {
        'partner_id': fields.many2one('res.partner',
                                   'Supplier'),
        'maturity': fields.date('Maturity Maximum'),
        'it_supplier': fields.boolean('Italian Suppliers'),
        'ext_supplier': fields.boolean('Foreign Suppliers'),
        'include_customers': fields.boolean('Include Customers'),
        'journal_id':fields.many2one('account.journal', 'Journal'),
        'bank_id': fields.many2one('res.partner.bank', 'Bank'),
        'authorization':fields.selection([
            ('Authorized', 'Authorized'),
            ('All', 'All'),
        ], 'Authorization'),
    }
    
    _defaults = {
                 'authorization': 'All',
                 }
    
    def get_total_pages(self, cr, uid, v_filters, t_limit):
        move_line_obj = self.pool.get('account.move.line')
        valid_all_ids = move_line_obj.search(cr, uid,
                                             v_filters, 
                                             order='date_maturity, id')
        t_total_pages = 1
        if valid_all_ids:
            t_total_pages = int(len(valid_all_ids) / t_limit)
            if (len(valid_all_ids) % t_limit) > 0:
                t_total_pages += 1
        return t_total_pages

    def set_payment_lines(self, cr, uid, context=None):
        t_lines = []
        t_all_supplier = False
        res_partner_obj = self.pool.get('res.partner')
        wizard_obj = self.pool.get('wizard.payment.specification')
        t_partner_id = context.get('default_partner_id', None)
        account_move_line_obj = self.pool.get('account.move.line')
        list_partner = []
        t_limit = 50
        
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

        t_total_pages = self.get_total_pages(cr, uid, v_filters, t_limit)
        
        res_id = wizard_obj.create(cr, uid, {
                                             'all_supplier': t_all_supplier,
                                             'total_pages': t_total_pages
                                             }, context)
        
        account_move_line_valid_ids = account_move_line_obj.search(cr, uid, v_filters,
                                                             order='date_maturity, id',
                                                             limit=t_limit,
                                                             offset=0,
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
    
    def check_company_accounting(self, cr, uid):
        company_obj = self.pool.get('res.company')
        partner_bank = self.pool.get('res.partner.bank')

        voucher_obj = self.pool.get('account.voucher')
        my_company_id = voucher_obj.get_company(cr, uid, context=None)
        my_company = company_obj.browse(cr, uid, my_company_id)

        company_bank_ids = partner_bank.search(cr, uid, [('company_id', '=', my_company.id)])
        
        if not company_bank_ids:
            raise orm.except_orm(_('Error!'), _('Non è stata impostata nessuna banca aziendale'))
        
        if (not my_company.bonus_active_account_id.id):
            raise orm.except_orm(_('Error!'), _('Non è stato impostato conto aziendale per gli abbuoni attivi'))
        
        if (not my_company.bonus_passive_account_id.id):
            raise orm.except_orm(_('Error!'), _('Non è stato impostato conto aziendale per gli abbuoni passivi'))
        
        return True

    def view_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        self.check_company_accounting(cr, uid)
        
        t_partner_id = []
        t_allsupplier = True
        t_bank_id = []
        
        form = self.read(cr, uid, ids)[0]
        if(form["partner_id"]):
            t_partner_id = form["partner_id"][0]
            t_allsupplier = False
        t_maturity = form["maturity"]
        t_it = form["it_supplier"]
        t_ext = form["ext_supplier"]
        t_include = form["include_customers"]
        if(form["bank_id"]):
            t_bank_id = form["bank_id"][0]
        t_authorization = form["authorization"]
        
        context.update({
            'default_partner_id': t_partner_id,
            'default_maturity': t_maturity,
            'default_it_supplier': t_it,
            'default_ext_supplier': t_ext,
            'default_journal_id': self.pool.get('account.voucher')._get_journal(cr, uid),
            'default_bank_id': t_bank_id,
            'default_authorization': t_authorization,
            'default_include_customers': t_include,
            'default_all_supplier': t_allsupplier,
        })

        res_id = self.set_payment_lines(cr, uid, context)
        
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_payment_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Payment Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.payment.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview'
              }
