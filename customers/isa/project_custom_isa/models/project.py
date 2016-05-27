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


class project(orm.Model):
    _inherit = 'project.project'

    def _get_isa_task(self, cr, uid, ids, context=None):
        result = {}
        for task in self.pool.get('project.task').browse(cr, uid, ids, context=context):
            if task.project_id:
                result[task.project_id.id] = True
        return result.keys()

    def _get_project_isa(self, cr, uid, ids, context=None):
        result = {}
        for t_project in self.browse(cr, uid, ids, context=context):
            result[t_project.id] = True
        return result.keys()

    def _get_project_task(self, cr, uid, ids, context=None):
        result = {}
        for work in self.pool.get('project.task.work').browse(cr, uid, ids, context=context):
            if work.task_id.project_id:
                result[work.task_id.project_id.id] = True
        return result.keys()

    def _hours_billing_project_get(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cr.execute("""SELECT project_id, SUM(COALESCE(isa_billing_hours,0.0))
                      FROM project_task
                      WHERE project_id IN %s GROUP BY project_id""",
                   (tuple(ids),))
        hours = dict(cr.fetchall())
        for t_project in self.browse(cr, uid, ids, context=context):
            res[t_project.id] = hours.get(t_project.id, 0.0)
        return res

    def _get_hrs_effective_proj(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        if ids:
            cr.execute("""SELECT project_id, SUM(COALESCE(effective_hours,0.0))
                          FROM project_task
                          WHERE project_id IN %s GROUP BY project_id""",
                       (tuple(ids),))
            hours = dict(cr.fetchall())
            for task in self.browse(cr, uid, ids, context=context):
                res[task.id] = hours.get(task.id, 0.0)
        return res

    def _get_fnct_state(self, cr, uid, ids, field_names, args, context=None):
        result = {}
        for data in self.browse(cr, uid, ids, context=context):
            if data.state:
                result[data.id] = data.state
            else:
                result[data.id] = ''
        return result

    def write(self, cr, uid, ids, vals, context=None):
        if 'billing_state' in vals and vals['billing_state'] == '01':
            for project_id in self.browse(cr, uid, ids, context=context):
                for task_id in project_id.tasks:
                    for work_id in task_id.work_ids:
                        self.pool.get('project.task.work').write(cr, uid, work_id.id, {'not_billing':True}, context=context)
        return super(project,self).write(cr, uid, ids, vals, context=context)

    def onchange_project_category(self, cr, uid, ids, category_id, context=None):

        if ids and category_id:
            category_team_obj = self.pool.get('project.category.team')

            project_data = self.browse(cr, uid, ids[0])
            new_members_id = []
            old_members = []
            new_members = []
            for mem in project_data.members:
                old_members.append(mem.id)
            category_team_ids = category_team_obj.search(cr, uid, [('project_category_id', '=', category_id)])
            for ct in category_team_obj.browse(cr, uid, category_team_ids):
                if ct.member_id.id not in old_members:
                    new_members_id.append(ct.member_id.id)

            new_members.append((6, 0, new_members_id + old_members))
            self.write(cr, uid, ids, {'members': new_members})

        return {'value': {}
                }

    def _state_search(self, cr, uid, obj, name, args, context=None):
        return []

    _columns = {
        'billing_state': fields.selection([('01', '01 - Not to be billed'),
                                           ('02', '02 - To be billed'),
                                           ('03', '03 - Billed')],
                                          'State billing',
                                          select=True),
        'billing_month': fields.selection([(1, 'January'),
                                           (2, 'February'),
                                           (3, 'March'),
                                           (4, 'April'),
                                           (5, 'May'),
                                           (6, 'June'),
                                           (7, 'July'),
                                           (8, 'August'),
                                           (9, 'September'),
                                           (10, 'October'),
                                           (11, 'November'),
                                           (12, 'December')],
                                          'Month billing'),
        'billing_year': fields.integer('Year billing'),
        'category_id': fields.many2one('project.category', 'Category'),

        'billing_hours_project': fields.function(_hours_billing_project_get,
                                                 method=True,
                                                 type='float',
                                                 string='Hours Billed',
                                                 store={'project.project': (_get_project_isa, ['tasks'], 10),
                                                        'project.task': (_get_isa_task,
                                                                         ['work_ids', 'isa_billing_hours'],
                                                                         10),
                                                        'project.task.work': (_get_project_task,
                                                                              ['billable_hours'],
                                                                              20),
                                                        }),
        'effective_hours_project': fields.function(_get_hrs_effective_proj,
                                                   method=True,
                                                   type='float',
                                                   string='Effective Hours'),
        'hours_for_partner': fields.related('effective_hours',
                                            type="float",
                                            relation='project.project',
                                            string='Hours worked for partners',
                                            store=True,
                                            readonly=True),
        'close_description': fields.text('Close Description'),
        'billing_as400': fields.boolean('Transfer as400'),
        'included_package': fields.boolean('included package hours'),
        'contract': fields.many2one('project.contract', 'Contract'),
        'contract_line': fields.many2one('project.contract.line',
                                         'Category Line'),
        'billing_as400_date': fields.datetime('Billing Date'),
        'contract_mod_date': fields.datetime('Contract Modify Date'),

        'datetime_end': fields.datetime('Project Closing Date Time',
                                        select=True),
        'fnct_state': fields.function(_get_fnct_state,
                                      method=True,
                                      string='Get State',
                                      type='char',
                                      store=False,
                                      fnct_search=_state_search),
        'budget_hours': fields.float('Ore Preventivate', digits=(16, 2)),
    }

    def set_done(self, cr, uid, ids, context=None):
        # aggiunge data chiusura alla "chiusura" del progetto
        # ed effettua i controlli
        context = dict(context or {})
        if isinstance(ids, (int, long)):
            ids = [ids]

        # controllo stato attività collegate al progetto
        self._check_open_task(cr, uid, ids, context)

        for project_data in self.browse(cr, uid, ids, context):

            end_date = project_data.date
            end_datetime = project_data.datetime_end

            if not end_date:
                end_date = time.strftime(DTF)
            if not end_datetime:
                end_datetime = time.strftime(DTF)

            # HelpBoard - ticket da assegnare
            # se user_id è stato lasciato == Help_board, non permettere la chiusura
            if project_data.user_id and project_data.user_id.login == 'helpboard':
                raise orm.except_orm(_('Error !'),
                                     _("""You cannot close a project with project manager HelpBoard."""))

            # non permettere la chiusura se billing_state non è specificato
            if not project_data.billing_state:
                raise orm.except_orm(_('Error !'),
                                     _("""You cannot close a project without billing state."""))

            # se ore fatturate = 0 solo se tipologia è "da non fatturare"
            if project_data.billing_state != '01':
                if project_data.billing_hours_project <= 0:
                    raise orm.except_orm(_('Error !'),
                                         _("""You cannot close a project with billing hours not correct."""))

            # Se il nome del progetto inizia con HB_ il progetto si può chiudere
            # solo se abbiamo valore per le note di chiusura
            if project_data.name[:3] == 'HB_':
                if not (project_data.closing_category_id and project_data.close_description):
                    raise orm.except_orm(_('Error !'),
                                         _("""You cannot close a project with name strting with "HB_" without closing informations."""))

            # Se la categoria del progetto è "85 - Assistenza presso clienti"
            # riga contratto è required
            if (project_data.category_id and project_data.category_id.code.find('85', 0, 2) == 0):
                if not project_data.contract_line:
                    raise orm.except_orm(_('Error !'),
                                         _("""You cannot close a project with category "85 - Assistenza presso clienti" without select contract line"""))

        self.write(cr, uid, ids, {'datetime_end': end_datetime, 'date': end_date}, context=context)

        res = super(project, self).set_done(cr, uid, ids, context)

        return res

    def _check_open_task(self, cr, uid, ids, context=None):
        # controllo stato attività collegate progetto
        for project_data in self.browse(cr, uid, ids):
            for task in project_data.tasks:
                if task.stage_id and task.stage_id.name not in ['Cancelled', 'Done']:
                    raise orm.except_orm(_('Warning !'),
                                         _("""Non si puo\' chiudere il progetto perche\' lo stato del lavoro "%s" non e\' "cancellato" o "terminato".""" % task.name))
        return True

    def onchange_contract(self, cr, uid, ids, context=None):

        act_date = time.strftime(DTF)

        return {'value': {'contract_mod_date': act_date}}
