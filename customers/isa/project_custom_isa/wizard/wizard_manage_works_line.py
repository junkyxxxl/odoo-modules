# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 ISA s.r.l. (<http://www.isa.it>).
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


class project_wizard_manage_works_line(orm.TransientModel):
    _name = 'project.wizard.manage.works.line'
    _description = 'Daily Works Line'

    def _hours_billing_work(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        for task_work in self.browse(cr, uid, ids, context=context):
            if(task_work.not_billing):
                res[task_work.id] = 0.0
            else:
                res[task_work.id] = task_work.hours
        return res

    _columns = {'manage_id': fields.many2one('project.wizard.manage.works',
                                             'Manage'),
                'project_id': fields.many2one('project.project',
                                              'Project'),
                'task_id': fields.many2one('project.task',
                                           'Task'),
                'user_id': fields.many2one('res.users',
                                           'User'),
                'type_id': fields.many2one('project.task.work.type',
                                           'Type of work',
                                           ondelete="cascade"),
                'program': fields.char('Program', size=50),
                'file': fields.char('File', size=50),
                'field': fields.char('Field', size=50),
                'ptf_code': fields.char('PTF code', size=50),
                'description': fields.text('Description'),
                'hours': fields.float('Hours'),
                'not_billing': fields.boolean('Not Billing'),
                'works_date': fields.date('Date'),
                'task_work': fields.many2one('project.task.work', 'Task Work'),
                'project_task_state': fields.char('State', size=10),
                'billable_hours': fields.function(_hours_billing_work,
                                                  method=True,
                                                  type='float',
                                                  string='Hours Billed'),
                }

    def action_edit_work(self, cr, uid, ids, context=None):
        task_work_obj = self.pool.get('project.task.work')
        t_work = self.browse(cr, uid, ids[0]).task_work.id

        res = task_work_obj.action_edit_work(cr, uid, [t_work], context=context)
        return res

    def delete_work(self, cr, uid, ids, context=None):
        t_line = self.browse(cr, uid, ids[0])
        t_task_work_id = t_line.task_work.id
        self.pool.get('project.task.work').unlink(cr, uid, [t_task_work_id])
        return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)
