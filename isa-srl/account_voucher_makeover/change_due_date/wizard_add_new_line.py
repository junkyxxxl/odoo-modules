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


class wizard_add_new_line(orm.TransientModel):
    _name = 'wizard.add.new.line'
    _description = 'Wizard Add New Line'

    _columns = {
                'change_id': fields.many2one('wizard.change.due.date',
                                         'Change Due Date',
                                         ondelete="cascade",
                                         required=True),
                'amount':fields.float('Amount'),
                'payment_type': fields.selection([('C', 'Cash'),
                                                  ('B', 'Bank Transfer'),
                                                  ('D', 'Bank Draft')],
                                                 'Payment Type'),
                'date_due': fields.date('Date Maturity'),
          
    }

    def confirm(self, cr, uid, ids, context=None):
        wizard_obj = self.pool.get('wizard.change.due.date')
        form = self.read(cr, uid, ids)[0]
        t_due_date = form["date_due"]
        t_payment_type = form["payment_type"]
        t_amount = form["amount"]
        
        t_total = 0.0
        for line in self.browse(cr,uid,ids[0]).change_id.old_ids:
            t_total += line.amount        

        if(t_total > 0.0 and t_amount <= 0.0):
            raise orm.except_orm(_('Error!'),
                                 _("Inserire importo positivo e non nullo!"))
        elif(t_total <= 0.0 and t_amount >= 0.0):
            raise orm.except_orm(_('Error!'),
                                 _("Inserire importo negativo e non nullo!"))            

        t_wizard = self.browse(cr, uid, ids[0])
        t_change = t_wizard.change_id
        t_line = t_change.old_ids[0]
        t_lines = []
        
        '''
        if t_payment_type == 'D':
           if not t_change.invoice_id or not t_change.invoice_id.bank_account:
            if not t_change.partner_id or not t_change.partner_id.bank_ids:
                raise orm.except_orm(_('Error!'),
                                 _("Non puoi impostare scadenze Ri.Ba. poichè nella fattura non è specificato alcuno conto bancario per il cliente, ed il cliente non ha associato alcun conto bancario."))
        '''
            
        t_lines.append((0, 0, {
                                'partner_id': t_line.partner_id.id,
                                'account_id': t_line.account_id.id,
                                'move_line_id': None,
                                'change_id': t_change.id,
                                'amount': t_amount,
                                'date_due': t_due_date,
                                'line_state': 'new',
                                'payment_type': t_payment_type
                            }))
        
        wizard_obj.write(cr, uid, [t_change.id], {'new_ids': t_lines, })
        
        return True
