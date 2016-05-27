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

import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.osv import fields, orm
from openerp.tools.translate import _


class project_task(orm.Model):
    _inherit = 'project.task'

    def onchange_planned(self, cr, uid, ids, planned=0.0, effective=0.0):
        remaining = 0.0
        if isinstance(planned, float) and isinstance(effective, float):
            remaining = planned - effective
        return {'value': {'remaining_hours': remaining}}

    def _hours_billing_get(self, cr, uid, ids, field_names, args,
                           context=None):
        res = {}
        cr.execute("""SELECT task_id, SUM(COALESCE(billable_hours,0.0))
                      FROM project_task_work
                      WHERE task_id IN %s
                      GROUP BY task_id""", (tuple(ids),))
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = hours.get(task.id, 0.0)
        return res

    def _get_project_task(self, cr, uid, ids, context=None):
        result = {}
        for work in self.pool.get('project.task.work').browse(cr, uid, ids,
                                                              context=context):
            if work.task_id:
                result[work.task_id.id] = True
        return result.keys()

    def _get_fnct_state(self, cr, uid, ids, field_names, args, context=None):
        result = {}
        for data in self.browse(cr, uid, ids, context=context):
            if data.stage_id.name:
                result[data.id] = data.stage_id.name
            elif ('state' in data and data.state):
                result[data.id] = data.state
            else:
                result[data.id] = ''
        return result

    def _issue_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        t_project_issue_obj = self.pool.get('project.issue')
        issue_ids = t_project_issue_obj.search(cr, uid, [('task_id', 'in', ids)])
        for issue in t_project_issue_obj.browse(cr, uid, issue_ids, context):
            if issue.stage_id and issue.stage_id.name not in ('Done', 'Cancelled'):
                res[issue.task_id.id] += 1
        return res

    def _default_task_stage_id(self, cr, uid, context=None):
        type_obj = self.pool.get('project.task.type')
        task_type_ids = type_obj.search(cr, uid,
                                        ['|',
                                         ('name', '=', 'Bozza'),
                                         ('name', '=', 'Draft')])
        if task_type_ids:
            return task_type_ids[0]
        return None

    def _state_search(self, cr, uid, obj, name, args, context=None):
        # TODO
        return []

    _columns = {
        'category_id': fields.many2one('project.task.category',
                                       'Category',
                                       ondelete="cascade"),
        'ticket_reference': fields.char('Ticket reference',
                                        size=50,
                                        required=False),
        'need_ticket': fields.boolean(),
        'isa_billing_hours': fields.function(_hours_billing_get,
                                             method=True,
                                             string='Billable Hours',
                                             type='float',
                                             store={
                                                 'project.task': (lambda self, cr, uid, ids, c={}: ids,
                                                                  ['work_ids', 'isa_billing_hours'], 10),
                                                 'project.task.work': (_get_project_task,
                                                                       ['billable_hours'],
                                                                       10),
                                             }),
        'billing_as400_date': fields.datetime('Billing Date'),
        'billing_as400': fields.boolean('Transfer as400'),
        'fnct_state': fields.function(_get_fnct_state,
                                      method=True,
                                      string='Get State',
                                      type='char',
                                      store=False,
                                      fnct_search=_state_search),
        'issue_count': fields.function(_issue_count, type='integer', string="Unclosed Issues"),

        'datetime_end': fields.datetime('Task Closing Date Time',
                                        select=True),
    }

    _defaults = {'stage_id': _default_task_stage_id,
                 }

    def onchange_project(self, cr, uid, ids, project_id, context=None):
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid,
                                                              project_id,
                                                              context=context)
            if project.partner_id:
                return {'value': {'partner_id': project.partner_id.id}}
            elif project.parent_id and project.parent_id.partner_id:
                return {'value': {'partner_id': project.parent_id.partner_id.id
                                  }
                        }
        return {}

    def onchange_category(self, cr, uid, ids, category_id):
        if not category_id:
            return {}

        data = self.pool.get('project.task.category').browse(cr, uid, category_id)
        result = {'need_ticket': False,
                  }
        if data.ticket_required is True:
            result = {'need_ticket': True,
                      }
        return {'value': result}

    def action_close(self, cr, uid, ids, context=None):

        task_id = len(ids) and ids[0] or False
        self._check_child_task(cr, uid, ids, context=context)
        if not task_id:
            return False

        task_data = self.browse(cr, uid, task_id)

        if not task_data.user_id:
            raise orm.except_orm(_('Error !'),
                                 _('You cannot close an activity without a responsible.'))

        if task_data.user_id.login == 'helpboard':
            raise orm.except_orm(_('Error !'),
                                 _('You cannot close an activity with responsible HelpBoard.'))

        end_datetime = task_data.datetime_end or time.strftime(DTF)

        task_type_obj = self.pool.get('project.task.type')
        task_type_ids = task_type_obj.search(cr, uid, [('is_done', 'in', ids)])
        if task_type_ids:
            self.write(cr, uid, [task_id],
                       {'stage_id': task_type_ids[0],
                        'datetime_end': end_datetime,
                        },
                       context=context)

        return True
