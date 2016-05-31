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
from openerp import api
from openerp.osv import orm,fields
from openerp.tools.translate import _

class account_move_voucher_makeover(orm.Model):
    _inherit = "account.move"

    def button_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if not line.journal_id.update_posted:
                raise orm.except_orm(_('Error!'),
                                     _('You cannot modify a posted entry of this journal.\nFirst you should set the journal %s to allow cancelling entries.') % (line.journal_id.name))
        if ids:
            cr.execute('UPDATE account_move '\
                       'SET state=%s '\
                       'WHERE id IN %s', ('draft', tuple(ids),))
        return True

    def _check_change_due_date(self, cr, uid, ids, context=None):
        t_move = ids[0]
        inv_obj = self.pool.get('account.invoice')
        t_invoice_ids = inv_obj.search(cr, uid,
                                   [('move_id', '=', t_move)])
        if not t_invoice_ids:
            raise orm.except_orm(_('Error!'),
                                 _("Hai selezionato un movimento che non è collegato a nessuna fattura!"))
        
        t_invoice = inv_obj.browse(cr, uid, t_invoice_ids[0])
        t_wht_amount = t_invoice.wht_amount
        if(t_wht_amount > 0.0):
            raise orm.except_orm(_('Error!'),
                                 _("La fattura per questa movimentazione è soggetta a ritenuta d'acconto!"))
        return True
    
    def _set_wizard_due_date(self, cr, uid, ids, context=None):
        wizard_obj = self.pool.get('wizard.change.due.date')
        inv_obj = self.pool.get('account.invoice')
        move_line_obj = self.pool.get('account.move.line')
        t_lines = []
        t_lines_new = []
        t_move = ids[0]
        t_invoice = inv_obj.search(cr, uid,
                                   [('move_id', '=', t_move)])

        vals = {
                'move_id': t_move,
        }
        
        if t_invoice:
            self._check_change_due_date(cr, uid, [t_move], context)        
            vals.update({'invoice_id': t_invoice[0]})
                
        
        
        res_id = wizard_obj.create(cr, uid, vals)
        
        for t_move_line in self.browse(cr, uid, t_move).line_id:
            if(t_move_line.date_maturity and not t_move_line.reconcile_id.id and not t_move_line.is_wht):
                if t_invoice:
                    t_amount = t_move_line.debit or t_move_line.credit
                else:
                    t_amount = t_move_line.debit or -t_move_line.credit                    
                if(t_move_line.reconcile_partial_id.id):
                    line_partial_ids = move_line_obj.search(cr, uid, [('move_id', '!=', t_move_line.move_id.id),
                                                                      ('reconcile_partial_id', '=', t_move_line.reconcile_partial_id.id)])
                    for line_partial in move_line_obj.browse(cr , uid, line_partial_ids):
                        if t_invoice:
                            t_amount = t_amount - (line_partial.debit or line_partial.credit)
                        else:
                            t_amount = t_amount - (line_partial.debit or -line_partial.credit)                            
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
                                        'payment_type': t_move_line.payment_type_move_line
                                    }))

        ''' Aggiunto per l'inserimento di default dei valori delle scadenze new'''
        for t_move_line in self.browse(cr, uid, t_move).line_id:
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
