# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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

class hr_expense_expense(orm.Model):
    _inherit="hr.expense.expense"
    
    def action_move_create(self, cr, uid, ids, context=None):
        res = super(hr_expense_expense,self).action_move_create(cr,uid,ids,context)
        if res:
            analytic_line_obj = self.pool.get('account.analytic.line')
            move_line_obj = self.pool.get('account.move.line')            
            lines = self.browse(cr,uid,ids)
            lines = lines.line_ids
            for expense_line in lines:
                if expense_line.expense_id.account_move_id:
                    move_id = expense_line.expense_id.account_move_id.id
                    for move_line_id in move_line_obj.search(cr,uid,[('move_id','=',move_id)]):
                        analytic_line_id = analytic_line_obj.search(cr,uid,[('move_id','=',move_line_id)])
                        if analytic_line_id:
                            if expense_line.to_invoice:
                                analytic_line_obj.write(cr,uid,analytic_line_id,{'to_invoice':expense_line.to_invoice.id,})
                            else:
                                analytic_line_obj.write(cr,uid,analytic_line_id,{'to_invoice':None,})             
        return res

    def set_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
