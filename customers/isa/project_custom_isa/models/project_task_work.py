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
from openerp.tools.translate import _


class project_task_work(orm.Model):
    _inherit = 'project.task.work'

    def onchange_project_id(self, cr, uid, ids, project_id, context=None):

        return {'domain': {'task_id': [('project_id', '=', project_id),
                                       ('fnct_state', '=', 'open')]},
                'value': {'task_id': None}
                }

    def onchange_project(self, cr, uid, ids, project_id, task_id, context=None):
        if task_id:
            if 'wiew_task_form' not in context or not context['wiew_task_form']:
                return {'value': {'task_id': None}
                        }
        return {}

    _columns = {
        'type_id': fields.many2one('project.task.work.type',
                                   'Type of work',
                                   ondelete="cascade",
                                   required=False),
        'program': fields.char('Program', size=50, required=False),
        'file': fields.char('File', size=50, required=False),
        'field': fields.char('Field', size=50, required=False),
        'ptf_code': fields.char('PTF code', size=50, required=False),
        'description': fields.text('Description'),
        'billable_hours': fields.float('Billable hours'),
        'project_id': fields.related('task_id',
                                     'project_id',
                                     type="many2one",
                                     relation="project.project",
                                     string='Project',
                                     store=False),
        'project_name': fields.related('task_id',
                                       'project_id',
                                       'name',
                                       type="char",
                                       relation="project.project",
                                       string='Project Name',
                                       store=False),
        'project_task_name': fields.related('task_id',
                                            'name',
                                            type="char",
                                            relation="project.task",
                                            string='Project Task Name',
                                            store=False),
        'project_task_planned_hours': fields.related('task_id',
                                                     'planned_hours',
                                                     type="float",
                                                     relation="project.task",
                                                     string='Task Planned Hours',
                                                     store=False),
        'project_task_effective_hours': fields.related('task_id',
                                                       'effective_hours',
                                                       type="float",
                                                       relation="project.task",
                                                       string='Task Effective Hours',
                                                       store=False),
        'project_task_state': fields.related('task_id',
                                             'fnct_state',
                                             type="char",
                                             relation="project.task",
                                             string='Task State',
                                             store=False),
        'not_billing': fields.boolean('Not Billing'),
    }

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.task_id:
                raise orm.except_orm(_('Error'),
                                     _('Task not defined for this Work !'))
            t_state = rec.task_id.fnct_state
            if (t_state == 'Done' or t_state == 'Cancelled' or t_state == 'Pending'):
                raise orm.except_orm(_('Error'),
                                     _('You cannot delete a work which is not in open or draft state !'))
        return super(project_task_work, self).unlink(cr, uid, ids, context)

    def view_work(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project_custom_isa',
                                              'view_task_work_form_isa')
        view_id = result and result[1] or False

        work_id = context.get('line_id', None)
        return {'name': _("Work"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task.work',
                'type': 'ir.actions.act_window',
                'res_id': work_id,
                'view_id': view_id,
                'target': 'new',
                }

    def duplicate_work(self, cr, uid, ids, default={}, context=None):

        t_id = ids[0]
        if context is None:
            context = {}
        res = super(project_task_work, self).copy(cr, uid, t_id,
                                                  default, context)

        t_date = self.browse(cr, uid, t_id).date
        if t_date:
            context.update({'day': t_date[:10]})

        t_flag = default.get('default_day_works_flag') or default.get('day_works_flag')

        if t_flag:
            return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

        return res

    def action_edit_work(self, cr, uid, ids, default={}, context=None):
        if context is None:
            context = {}

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project',
                                              'view_task_work_form')
        view_id = result and result[1] or False
        return {'name': _('Add New Work'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task.work',
                'type': 'ir.actions.act_window',
                'res_id': ids[0],
                'view_id': view_id,
                'target': 'new',
                }

    def save_work_and_next(self, cr, uid, ids, default={}, context=None):

        t_id = ids[0]
        if context is None:
            context = {}
        value = self.browse(cr, uid, t_id)
        t_user = value.user_id.id
        t_task_id = value.task_id.id
        t_project_id = value.project_id.id
        t_type_id = value.type_id.id
        t_program = value.program
        t_file = value.file
        t_field = value.field
        t_ptf_code = value.ptf_code
        t_description = value.description
        t_not_billing = value.not_billing
        t_name = value.name
        t_date = value.date
        t_hours = value.hours

        context.update({
            'default_user_id': t_user,
            'default_project_id': t_project_id,
            'default_task_id': t_task_id,
            'default_type_id': t_type_id,
            'default_program': t_program or '',
            'default_file': t_file or '',
            'default_field': t_field or '',
            'default_ptf_code': t_ptf_code or '',
            'default_description': t_description or '',
            'default_not_billing': t_not_billing or False,
            'default_name': t_name or '',
            'default_date': t_date or '',
            'default_hours': t_hours or '',
            'wiew_task_form': True,
        })

        super(project_task_work, self).write(cr, uid, t_id,
                                             default, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project_custom_isa',
                                              'view_task_work_form_isa')
        view_id = result and result[1] or False
        return {'name': _('Add New Work'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task.work',
                'type': 'ir.actions.act_window',
                'context': context,
                'view_id': view_id,
                'target': 'new',
                }

    def save_work(self, cr, uid, ids, default={}, context=None):

        if context is None:
            context = {}
        res = super(project_task_work, self).write(cr, uid, ids,
                                                   default, context)

        t_date = self.browse(cr, uid, ids[0]).date
        if t_date:
            context.update({'day': t_date[:10]})

        t_flag = default.get('default_day_works_flag') or default.get('day_works_flag')

        if t_flag:
            return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

        return res

    def create(self, cr, uid, vals, context=None):

        if not vals['hours']:
            raise orm.except_orm(_('Error !'),
                                 _('You cannot close a work without hours.'))

        if 'not_billing' in vals and vals['not_billing']:
            vals['billable_hours'] = 0.0
        elif not vals['billable_hours']:
            vals['billable_hours'] = vals['hours']

        t_uid = vals['user_id']

        emp_obj = self.pool.get('hr.employee')
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', t_uid)])
        if not emp_id:
            if not context.get('no_analytic_entry', False):
                context.update({'no_analytic_entry': True})

        return super(project_task_work, self).create(cr,
                                                     uid,
                                                     vals,
                                                     context=context)

    def write(self, cr, uid, ids, vals, context=None):

        check_vals = self._check_billable_hours(cr, uid, ids, vals, context)
        return super(project_task_work, self).write(cr, uid, ids,
                                                    check_vals, context)

    # a seconda del flag di not_billing. Il controllo non viene
    # effettuato se il lavoro è di tipo
    # ZZ che serve per gestire il pregresso id=30    utilizzo l'id perchè
    # da vals ho solo l'id

    def _check_billable_hours(self, cr, uid, ids, vals, context=None):
        values = self.read(cr, uid, ids)
        if 'type_id' in vals and vals['type_id']:
            if vals['type_id'] == 30:
                return vals
        else:
            if values[0]['type_id'][0] == 30:
                return vals

        for key, val in vals.iteritems():
            if key in values[0]:
                values[0][key] = val

        if values[0]['not_billing']:
            vals['billable_hours'] = 0.00
        else:
            vals['billable_hours'] = values[0]['hours']
        return vals

    def onchange_task(self, cr, uid, ids, task_id):
        if not task_id:
            return {}
        task_data = self.pool.get('project.task').browse(cr, uid, task_id)

        t_task_planned = task_data.planned_hours
        t_task_effective = task_data.effective_hours

        return {'value': {'project_task_planned_hours': t_task_planned,
                          'project_task_effective_hours': t_task_effective,
                          }}
        return {}
