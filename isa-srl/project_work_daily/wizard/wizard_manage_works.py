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
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class project_wizard_manage_works(orm.TransientModel):
    _name = 'project.wizard.manage.works'
    _description = 'Manage Works'

    def onchange_day(self, cr, uid, ids, user_id, day, context=None):
        work_ids = []
        if user_id:
            t_to_day = str(datetime.strptime(day[:10],
                                             DF) + timedelta(days=1))
            work_obj = self.pool.get('project.task.work')
            work_ids = work_obj.search(cr, uid,
                                       [('user_id', '=', user_id),
                                        ('date', '<', t_to_day),
                                        ('date', '>=', day)],
                                       context=context)
        return {'value': {'work_ids': work_ids}
                }

    def _get_weekday_name(self, cr, uid, weekday, context=None):
        _weekdays = {0: _('Monday'),
                     1: _('Tuesday'),
                     2: _('Wednesday'),
                     3: _('Thursday'),
                     4: _('Friday'),
                     5: _('Saturday'),
                     6: _('Sunday')}
        return _weekdays[weekday]

    def _get_week_day(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids):
            t_day_week = datetime.strptime(rec.day, DF).weekday()
            result[rec.id] = self._get_weekday_name(cr, uid, t_day_week)
        return result

    _columns = {
        'user_id': fields.many2one('res.users',
                                   'Utente',
                                   required=True),

        'day': fields.date('Date', select=True, store=True),

        'work_ids': fields.one2many('project.wizard.manage.works.line',
                                    'manage_id',
                                    string="Work Lines",
                                    readonly=True),
        'week_day': fields.function(_get_week_day,
                                    string='Day',
                                    type='char')
    }

    _defaults = {
        'day': fields.date.context_today,
    }

    def action_update_work_list(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)[0]
        user_id = data.user_id.id
        day = data.day
        self.onchange_day(cr, uid, ids, user_id, day, context)
        return True

    def action_manage_work(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        t_day = context.get('default_date', None)
        t_person = context.get('default_user_id', None)
        if(t_day):
            t_day = str(datetime.strptime(t_day, DF) + timedelta(hours=7, minutes=30))

        context.update({'default_task_id': False,
                        'default_project_id': False,
                        'default_type_id': False,
                        'default_hours': False,
                        'default_description': False,
                        'default_user_id': t_person,
                        'default_date': t_day,
                        'default_day_works_flag': True,
                        'modify_view': False,
                        })
        work_ids = []

        t_user_id = uid
        if t_user_id:
            work_obj = self.pool.get('project.task.work')
            work_ids = work_obj.search(cr, uid,
                                       [('user_id', '=', t_person)],
                                       context=context)
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project',
                                              'view_task_work_form')
        view_id = result and result[1] or False

        return {'name': _("Add New Work"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task.work',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'context': context,
                'target': 'new',
                'value': {'work_ids': work_ids},
                }

    def day_forward(self, cr, uid, ids, context=None):
        t_day = context.get('day', None)
        t_day_after = str(datetime.strptime(t_day[:10], DF) + timedelta(days=1))
        context.update({'day': t_day_after[:10]})
        return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

    def day_back(self, cr, uid, ids, context=None):
        t_day = context.get('day', None)
        t_day_after = str(datetime.strptime(t_day[:10], DF) - timedelta(days=1))
        context.update({'day': t_day_after[:10]})
        return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

    def select_new_date(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project_work_daily',
                                              'wizard_select_date_view')

        context.update({'user_id': None,
                        'default_user_id': None})

        view_id = result and result[1] or False

        return {'name': _("New Date"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.select.date',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'context': context,
                'target': 'new'
                }
