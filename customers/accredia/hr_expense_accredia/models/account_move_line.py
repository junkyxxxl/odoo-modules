# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, osv


class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def create_analytic_lines(self, cr, uid, ids, context=None):
        res = super(account_move_line, self).create_analytic_lines(cr, uid, ids, context=context)

        # recupero id per to_invoice
        to_invoice_not = None
        to_invoice_confirmed = None
        factor_obj = self.pool.get('hr_timesheet_invoice.factor')

        factor_ids = factor_obj.search(cr, uid,
                                       [('not_invoice', '=', True)],
                                       limit=1,
                                       context=None)
        if factor_ids:
            to_invoice_not = factor_ids[0]

        factor_ids = factor_obj.search(cr, uid,
                                       [('to_be_confirmed', '=', True)],
                                       limit=1,
                                       context=None)
        if factor_ids:
            to_invoice_confirmed = factor_ids[0]

        analytic_line_obj = self.pool.get('account.analytic.line')
        for move_line in self.browse(cr, uid, ids, context=context):
            t_line_partner_id = move_line.partner_id.id
            for line in move_line.analytic_lines:

                # calcolo fatturabilità da ruolo nel team
                t_to_invoice = None
                if line.task_id and line.partner_id:
                    t_to_invoice = to_invoice_not
                    for task_team_data in line.task_id.task_team_ids:
                        if task_team_data.user_id:
                            t_team_partner_id = task_team_data.user_id.partner_id.id
                            if t_team_partner_id == t_line_partner_id:
                                t_to_invoice = to_invoice_not
                                if task_team_data.role_id:
                                    if task_team_data.role_id.billable:
                                        t_to_invoice = to_invoice_confirmed

                                analytic_line_obj.write(cr, uid, line.id, {
                                    'to_invoice': t_to_invoice,
                                    }, context=context)
        return res

    def _prepare_analytic_line(self, cr, uid, obj_line, context=None):
        res = super(account_move_line, self)._prepare_analytic_line(cr, uid, obj_line, context=context)
        t_task_id = obj_line.task_id and obj_line.task_id.id or False
        t_expense_line_id = obj_line.expense_line_id and obj_line.expense_line_id.id or False
        t_name_line = obj_line.name or ''
        t_name_expense = obj_line.expense_line_id and obj_line.expense_line_id.expense_id.user_id and obj_line.expense_line_id.expense_id.user_id.partner_id.name or ''
        t_name_separator = t_name_expense and ' - ' or ''
        t_name = t_name_expense + t_name_separator + t_name_line
        res['task_id'] = t_task_id
        res['expense_line_id'] = t_expense_line_id
        res['name'] = t_name

        # utente e persona fisica
        res['partner_id'] = obj_line.expense_line_id and obj_line.expense_line_id.expense_id.user_id and obj_line.expense_line_id.expense_id.user_id.partner_id.id or None  # TODO partner_id è readonly perchè è function
        res['user_id'] = obj_line.expense_line_id and obj_line.expense_line_id.expense_id.user_id and obj_line.expense_line_id.expense_id.user_id.id or None

        return res

    _columns = {
        'task_id': fields.many2one('project.task',
                                   'Audit'),
        'expense_line_id': fields.many2one('hr.expense.line',
                                           'Riga Nota Spese'),
        }
