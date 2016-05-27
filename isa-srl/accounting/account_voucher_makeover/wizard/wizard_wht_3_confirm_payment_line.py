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


class wizard_confirm_payment_wht_line(orm.TransientModel):
    
    _name = 'wizard.confirm.payment.wht.line'
    _description = 'Wizard Confirm Payment Wht Line'
 
    _columns = {
        'is_selected': fields.selection([
            ('confirmed', 'Confirmed'),
            ('accepted', 'Accepted'),
            ('selected', 'Selected')], 'Selection Type'),
        'state': fields.selection([
            ('confirmed', 'Confirmed'),
            ('selected', 'Selected')], 'State'),
        'confirm_payment_wht_id': fields.many2one('wizard.confirm.payment.wht',
                                         'Confirm Payment',
                                         ondelete="cascade",
                                         required=True),
        'move_line_id': fields.many2one('account.move.line', 'Journal Item'),
        'account_id': fields.many2one('account.account', 'Account'),
        'partner_id': fields.many2one('res.partner', 'Supplier'),
        'amount':fields.float('Amount'), }

    def delete_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        line_id = context.get('line_id', None)
        data = self.browse(cr, uid, line_id, context=context)
        t_journal = data.confirm_payment_wht_id.journal_id.id
        t_period = data.confirm_payment_wht_id.period_id.id
        t_maturity = data.confirm_payment_wht_id.maturity
        t_bank = data.confirm_payment_wht_id.bank_id.id
        t_operation_date = data.confirm_payment_wht_id.operation_date
        t_currency_date = data.confirm_payment_wht_id.currency_date
        t_state = 'confirmed'
                    
        draft_obj = self.pool.get('account.move.line')
        t_move_id = data.move_line_id.id
        draft_obj.write(cr, uid, [t_move_id], {
            'wht_state': t_state,
        })
        
        context.update({
            'default_journal_id': t_journal,
            'default_period_id': t_period,
            'default_maturity': t_maturity,
            'default_bank_id': t_bank,
            'default_operation_date': t_operation_date,
            'default_currency_date': t_currency_date,
        })
       
        res_id = self.set_confirm_payment_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_confirm_payment_wht_view')
        view_id = result and result[1] or False

        return {
              'name': _("Confirm Payment Action"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.confirm.payment.wht',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }

    def set_confirm_payment_lines(self, cr, uid, context=None):

        t_lines = []
        vals = {}
        t_journal_id = context.get('default_journal_id', None)
        t_maturity = context.get('default_maturity', None)
        t_operation_date = context.get('default_operation_date', None)
        t_currency_date = context.get('default_currency_date', None)
        
       
        vals['maturity'] = t_maturity
        vals['journal_id'] = t_journal_id
        vals['operation_date'] = t_operation_date
        vals['currency_date'] = t_currency_date
        
        res_id = self.pool.get('wizard.confirm.payment.wht').create(cr, uid, vals, context=context)
     
        t_filter = [('wht_state', '=', 'selected')]
        account_move_line_obj = self.pool.get('account.move.line')
        account_move_line_ids = account_move_line_obj.search(cr,
                                                                uid,
                                                                t_filter,
                                                                context=context)

        if(account_move_line_ids and len(account_move_line_ids) > 0):
            for line_id in account_move_line_ids:
                t_move_line = account_move_line_obj.browse(cr, uid, line_id)                   
                t_state = t_move_line.wht_state
                t_lines.append((0, 0, {
                                       'state': t_state,
                                       'move_line_id': t_move_line.id,
                                       'partner_id': t_move_line.partner_id.id,
                                       'account_id': t_move_line.account_id.id,
                                       'confirm_payment_wht_id': res_id,
                                       'amount': (t_move_line.debit or t_move_line.credit)
                                       }))
            
        self.pool.get('wizard.confirm.payment.wht').write(cr, uid, [res_id], {'line_ids': t_lines})
              
        return res_id
