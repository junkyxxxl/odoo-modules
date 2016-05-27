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
from openerp.tools.translate import _


class project_task_work(orm.Model):
    _inherit = "project.task.work"

    _columns = {'to_invoice': fields.many2one('hr_timesheet_invoice.factor',
                                              'Timesheet Invoicing Ratio'),
                }

    def get_user_related_details(self, cr, uid, user_id):
        res = {}
        emp_obj = self.pool.get('hr.employee')
        cmp_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', user_id), ('company_id', '=', cmp_id)])
        if not emp_id:
            user_name = self.pool.get('res.users').read(cr, uid, [user_id], ['name'])[0]['name']
            raise orm.except_orm(_('Bad Configuration!'),
                 _('Please define employee for user "%s". You must create one.')% (user_name,))
        emp = emp_obj.browse(cr, uid, emp_id[0])
        if not emp.product_id:
            raise orm.except_orm(_('Bad Configuration!'),
                 _('Please define product and product category property account on the related employee.\nFill in the HR Settings tab of the employee form.'))

        if not emp.journal_id:
            raise orm.except_orm(_('Bad Configuration!'),
                 _('Please define journal on the related employee.\nFill in the timesheet tab of the employee form.'))

        acc_id = emp.product_id.property_account_expense.id
        if not acc_id:
            acc_id = emp.product_id.categ_id.property_account_expense_categ.id
            if not acc_id:
                raise orm.except_orm(_('Bad Configuration!'),
                        _('Please define product and product category property account on the related employee.\nFill in the timesheet tab of the employee form.'))

        res['product_id'] = emp.product_id.id
        res['journal_id'] = emp.journal_id.id
        res['general_account_id'] = acc_id
        res['product_uom_id'] = emp.product_id.uom_id.id
        return res

    def create(self, cr, uid, vals, *args, **kwargs):
        if 'task_id' in vals:
            kwargs['context'].update({'task_id': vals['task_id']})
        res = super(project_task_work, self).create(cr, uid, vals, *args, **kwargs)
        line_obj = self.pool.get('account.analytic.line')
        work_data = self.browse(cr, uid, res)
        line_id = work_data.hr_analytic_timesheet_id.line_id.id
        if work_data.to_invoice:
            line_obj.write(cr, uid, line_id, {'to_invoice': work_data.to_invoice.id, })
        else:
            line_obj.write(cr, uid, line_id, {'to_invoice': None, })
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_task_work, self).write(cr, uid, ids, vals, context)
        line_obj = self.pool.get('account.analytic.line')
        work_data = self.browse(cr, uid, ids)
        line_id = work_data.hr_analytic_timesheet_id.line_id.id
        if work_data.to_invoice:
            line_obj.write(cr, uid, line_id, {'to_invoice': work_data.to_invoice.id, })
        else:
            line_obj.write(cr, uid, line_id, {'to_invoice': None, })
        return res
