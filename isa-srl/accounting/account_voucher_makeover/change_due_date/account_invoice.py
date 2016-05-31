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

from openerp.osv import orm
from openerp.tools.translate import _

class account_invoice_voucher_makeover(orm.Model):
    _inherit = "account.invoice"
    
    def _check_change_due_date(self, cr, uid, ids, context=None):
        t_invoice = self.browse(cr, uid, ids[0])
        t_wht_amount = t_invoice.wht_amount
        if(t_wht_amount > 0.0):
            raise orm.except_orm(_('Error!'),
                                 _("Hai selezionato fattura soggetta a ritenuta d'acconto!"))
        return True
    
    def _set_wizard_due_date(self, cr, uid, ids, context=None):
        wizard_obj = self.pool.get('wizard.change.due.date')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        t_lines = []
        t_lines_new = []
        t_invoice = ids[0]
        t_amount = 0.0
        
        self._check_change_due_date(cr, uid, [t_invoice], context)
        
        t_move = self.browse(cr, uid, t_invoice).move_id.id
        res_id = wizard_obj.create(cr, uid, {'move_id': t_move,
                                           'invoice_id': ids[0]})
        
        for t_move_line in move_obj.browse(cr, uid, t_move).line_id:
            if(t_move_line.date_maturity and not t_move_line.reconcile_id.id and not t_move_line.is_wht):
                t_amount = t_move_line.debit or t_move_line.credit
                if(t_move_line.reconcile_partial_id.id):
                    line_partial_ids = move_line_obj.search(cr, uid, [('move_id', '!=', t_move_line.move_id.id),
                                                                      ('reconcile_partial_id', '=', t_move_line.reconcile_partial_id.id)])
                    for line_partial in move_line_obj.browse(cr , uid, line_partial_ids):
                        t_amount = t_amount - (line_partial.debit or line_partial.credit) 
                    if(t_amount == 0.0):
                        continue
                t_lines.append((0, 0, {
                                        'partner_id': t_move_line.partner_id.id,
                                        'account_id': t_move_line.account_id.id,
                                        'move_line_id': t_move_line.id,
                                        'change_id': res_id,
                                        'amount': t_amount,
                                        'date_due': t_move_line.date_maturity,
                                        'line_state': 'old',
                                        'payment_type':t_move_line.payment_type_move_line
                                    }))

        ''' Aggiunto per l'inserimento di default dei valori delle scadenze new'''
        for t_move_line in move_obj.browse(cr, uid, t_move).line_id:
            if (t_move_line.date_maturity and not t_move_line.reconcile_id.id and not t_move_line.is_wht):
                t_amount = t_move_line.debit or t_move_line.credit
                if (t_move_line.reconcile_partial_id.id):
                    line_partial_ids = move_line_obj.search(cr, uid, [('move_id', '!=', t_move_line.move_id.id),
                                                                      ('reconcile_partial_id', '=',
                                                                       t_move_line.reconcile_partial_id.id)])
                    for line_partial in move_line_obj.browse(cr, uid, line_partial_ids):
                        t_amount = t_amount - (line_partial.debit or line_partial.credit)
                    if (t_amount == 0.0):
                        continue
                t_lines_new.append((0, 0, {
                    'partner_id': t_move_line.partner_id.id,
                    'account_id': t_move_line.account_id.id,
                    'move_line_id': t_move_line.id,
                    'change_id': res_id,
                    'amount': t_amount,
                    'date_due': t_move_line.date_maturity,
                    'line_state': 'new',
                    'payment_type': t_move_line.payment_type_move_line
                }))
        wizard_obj.write(cr, uid, [res_id], {'old_ids': t_lines, })
        wizard_obj.write(cr, uid, [res_id], {'new_ids': t_lines_new,})
        return int(res_id)

    def change_due_date(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        res_id = self._set_wizard_due_date(cr, uid, ids, context)
              
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_change_due_date_view')
        view_id = result and result[1] or False
        # "default_partner_id": self.pool.get('account.move').browse(cr, uid, self.browse(cr, uid, ids[0]).move_id.id).line_id[0].partner_id.id},

        return {
              'name': _("Change Due Date Action"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.change.due.date',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'res_id': res_id,
              'target': 'current',
              }