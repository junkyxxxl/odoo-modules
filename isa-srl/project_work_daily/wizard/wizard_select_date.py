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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, timedelta
from openerp.tools.translate import _


class wizard_select_date(orm.TransientModel):
    _name = 'wizard.select.date'
    _description = 'Wizard Select Date'

    _columns = {
        'day': fields.date('Date'),
        'user_id': fields.many2one('res.users',
                                   'Persona Fisica'),
    }

    _defaults = {
        'day': fields.date.context_today,
    }

    def _set_works_lines(self, cr, uid, ids, context=None):

        t_lines = []
        t_day = context.get('day', None)
        t_user_id = context.get('user_id', None)
        res_id = self.pool.get('project.wizard.manage.works').create(cr, uid, {'day': t_day, 'user_id': t_user_id}, context=context)

        work_line_obj = self.pool.get('project.task.work')
        t_from_day = t_day
        t_to_day = str(datetime.strptime(t_day[:10], DF) + timedelta(days=1))
        work_ids = work_line_obj.search(cr, uid,
                                        [('user_id', '=', t_user_id),
                                         ('date', '<', t_to_day),
                                         ('date', '>=', t_from_day)],
                                        context=context)

        for line in work_line_obj.browse(cr, uid, work_ids):
                            t_line_id = line.id
                            t_project = line.project_id.id
                            t_lines.append((0, 0, {'project_id': t_project,
                                                   'task_id': line.task_id.id,
                                                   'user_id': t_user_id,
                                                   'hours': line.hours,
                                                   'works_date': t_day,
                                                   'task_work': t_line_id,
                                                   }))

        self.pool.get('project.wizard.manage.works').write(cr, uid, [res_id], {'work_ids': t_lines, })

        return res_id

    def view_day_works(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project_work_daily',
                                              'wizard_project_manage_works_view')

        res_id = self._set_works_lines(cr, uid, ids, context)

        context.update({'day_works_flag': True})
        view_id = result and result[1] or False

        return {'name': _("Day Works"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.wizard.manage.works',
                'type': 'ir.actions.act_window',
                'res_id': res_id,
                'view_id': view_id,
                'context': context,
                'target': 'inline'
                }
