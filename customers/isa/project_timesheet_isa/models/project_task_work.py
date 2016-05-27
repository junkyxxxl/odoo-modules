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

from openerp.osv import orm


class ProjectTaskWork(orm.Model):
    _inherit = "project.task.work"

    def _create_analytic_entries(self, cr, uid, vals, context):
        if not context:
            context = {}
        timeline_id = super(ProjectTaskWork, self)._create_analytic_entries(cr, uid, vals, context=context)

        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        factor_obj = self.pool.get('hr_timesheet_invoice.factor')
        if 'set_to_invoice_not_billing' in context:
            t_factor_id = None
            if context.get('set_to_invoice_not_billing', False):

                factor_ids = factor_obj.search(cr, uid,
                                               [('gratis', '=', True)],
                                               limit=1,
                                               context=None)
                if factor_ids:
                    t_factor_id = factor_ids[0]
                updv = {'to_invoice': t_factor_id}
                timesheet_obj.write(cr, uid, [timeline_id], updv, context=context)
            else:
                timeline_data = timesheet_obj.browse(cr, uid, timeline_id)
                to_invoice_data = timeline_data.line_id.account_id.to_invoice
                t_factor_id = to_invoice_data and to_invoice_data.id or None
                if t_factor_id:
                    updv = {'to_invoice': t_factor_id}
                    timesheet_obj.write(cr, uid, [timeline_id], updv, context=context)

        task_obj = self.pool['project.task']
        task_data = task_obj.browse(cr, uid, vals['task_id'], context=context)
        included_package = task_data.project_id and task_data.project_id.included_package or False
        if included_package:
            t_factor_id = None
            factor_ids = factor_obj.search(cr, uid,
                                           [('package_hours', '=', True)],
                                           limit=1,
                                           context=None)
            if factor_ids:
                t_factor_id = factor_ids[0]
            updv = {'to_invoice': t_factor_id}
            timesheet_obj.write(cr, uid, [timeline_id], updv, context=context)

        return timeline_id

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if 'not_billing' in vals and vals['not_billing']:
            ctx.update({'set_to_invoice_not_billing': True})

        task_res = super(ProjectTaskWork, self).create(cr, uid, vals, context=ctx)
        return task_res

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        if not isinstance(ids, list):
            ids = [ids]
        t_not_billing = None
        for data in self.browse(cr, uid, ids):
            t_not_billing = data.not_billing
            break
        if 'not_billing' in vals:
            t_not_billing = vals['not_billing']
        context.update({'set_to_invoice_not_billing': t_not_billing})

        for data in self.browse(cr, uid, ids):
            if data.hr_analytic_timesheet_id:
                factor_obj = self.pool.get('hr_timesheet_invoice.factor')
                timesheet_obj = self.pool.get('hr.analytic.timesheet')
                t_factor_id = None
                if t_not_billing:
                    factor_ids = factor_obj.search(cr, uid,
                                                   [('gratis', '=', True)],
                                                   limit=1,
                                                   context=None)
                    if factor_ids:
                        t_factor_id = factor_ids[0]
                else:
                    to_invoice_data = data.hr_analytic_timesheet_id.line_id.account_id.to_invoice
                    t_factor_id = to_invoice_data and to_invoice_data.id or None
                updv = {'to_invoice': t_factor_id}
                timesheet_obj.write(cr, uid, [data.hr_analytic_timesheet_id.id], updv, context=context)

        return super(ProjectTaskWork, self).write(cr, uid, ids, vals, context)
