# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


class HrAnalyticTimesheet(osv.osv):
    _inherit = "hr.analytic.timesheet"

    def on_change_account_id(self, cr, uid, ids, account_id, user_id=False):
        res = {}
        t_factor_id = None
        factor_obj = self.pool.get('hr_timesheet_invoice.factor')

        factor_ids = factor_obj.search(cr, uid,
                                       [('not_invoice', '=', True)],
                                       limit=1,
                                       context=None)
        if factor_ids:
            t_factor_id = factor_ids[0]

        if not account_id:
            res['value'] = {}
            res['value']['to_invoice'] = t_factor_id or None
            return res

        res = super(HrAnalyticTimesheet, self).on_change_account_id(cr, uid, ids, account_id, user_id=user_id)

        res['value']['to_invoice'] = t_factor_id or None

        return res

    def onchange_task(self, cr, uid, ids, task_id, context=None):

        t_account_id = None
        if task_id:
            task_data = self.pool.get('project.task').browse(cr, uid, task_id)
            if task_data.project_id and task_data.project_id.analytic_account_id:
                t_account_id = task_data.project_id.analytic_account_id.id

        return {'value': {'account_id': t_account_id,
                          }}

    _columns = {
        'timesheet_line_type': fields.many2one('account.analytic.timesheet.type',
                                               'Categoria Attività'),
        'task_id': fields.many2one('project.task',
                                   'Riferimento'),
    }

    def _default_to_invoice(self, cr, uid, context=None):
        factor_obj = self.pool.get('hr_timesheet_invoice.factor')

        factor_ids = factor_obj.search(cr, uid,
                                       [('not_invoice', '=', True)],
                                       limit=1,
                                       context=None)
        if factor_ids:
            return factor_ids[0]
        return None

    _defaults = {
        'to_invoice': _default_to_invoice,
    }
