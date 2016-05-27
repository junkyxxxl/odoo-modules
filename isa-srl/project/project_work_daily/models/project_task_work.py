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

    _columns = {'project_id': fields.related('task_id',
                                             'project_id',
                                             type="many2one",
                                             relation="project.project",
                                             string='Project',
                                             store=False),
                }

    def action_edit_work(self, cr, uid, ids, default={}, context=None):

        if context is None:
            context = {}

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project',
                                              'view_task_work_form')

        context.update({'modify_view': True,
                        'readonly_view': False,
                        })

        view_id = result and result[1] or False
        return {'name': _('Add New Work'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task.work',
                'type': 'ir.actions.act_window',
                'res_id': ids[0],
                'view_id': view_id,
                'context': context,
                'target': 'new',
                }

    def view_work(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project',
                                              'view_task_work_form')
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

    def onchange_project(self, cr, uid, ids, project_id, task_id, context=None):

        if task_id and context:
            if not context.get('wiew_task_form', False):
                return {'value': {'task_id': None,
                                  }
                        }
        return {'value': {'unit_id': None,
                          }
                }

    def duplicate_work(self, cr, uid, ids, default={}, context=None):

        t_id = ids[0]
        if context is None:
            context = {}
        res = super(project_task_work, self).copy(cr, uid, t_id,
                                                  default, context)

        work_data = self.browse(cr, uid, ids[0])
        t_date = work_data.date
        if t_date:
            context.update({'day': t_date[:10]})
        t_user = work_data.user_id
        if t_user:
            context.update({'user_id': t_user.id})

        t_flag = default.get('default_day_works_flag') or default.get('day_works_flag')

        if t_flag:
            return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

        return res

    def copy(self, cr, uid, id, default=None, context=None):
        context = context or {}
        if default is None:
            default = {}
        default.update({'date': None,
                        })
        res = super(project_task_work, self).copy(cr, uid, id, default, context)
        return res

    def save_work_and_next(self, cr, uid, ids, default={}, context=None):

        if context is None:
            context = {}

        super(project_task_work, self).write(cr, uid, ids, default, context)

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
                'context': context,
                'view_id': view_id,
                'target': 'new',
                }

    def save_work(self, cr, uid, ids, default={}, context=None):

        if context is None:
            context = {}
        res = super(project_task_work, self).write(cr, uid, ids, default, context)

        work_data = self.browse(cr, uid, ids[0])
        t_date = work_data.date
        if t_date:
            context.update({'day': t_date[:10]})
        t_user = work_data.user_id
        if t_user:
            context.update({'user_id': t_user.id})

        t_flag = default.get('default_day_works_flag') or default.get('day_works_flag')

        if t_flag:
            return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

        return res

    def save_work_complete_task(self, cr, uid, ids, default={},
                                context=None):
        if context is None:
            context = {}
        res = super(project_task_work, self).write(cr, uid, ids, default, context)
        work_data = self.browse(cr, uid, ids)[0]
        t_task = work_data.task_id.id
        task_obj = self.pool.get('project.task')
        data = task_obj.browse(cr, uid, [t_task])
        if data and data[0]:
            # TODO disabilitare per accredia
            task_obj.do_close(cr, uid, [t_task], context=context)

        t_date = work_data.date
        if t_date:
            context.update({'day': t_date[:10]})
        t_user = work_data.user_id
        if t_user:
            context.update({'user_id': t_user.id})

        t_flag = default.get('default_day_works_flag') or default.get('day_works_flag')

        if t_flag:
            return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

        return res
