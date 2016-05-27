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

    def _get_display_button(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for work_data in self.browse(cr, uid, ids, context=context):
            res[work_data.id] = False

            if work_data.type_id:
                pt_obj = self.pool.get('accreditation.task.work.type')
                pt_data = pt_obj.browse(cr, uid, work_data.type_id.id)

                if pt_data.create_audit \
                    or pt_data.create_line_to_invoice \
                    or pt_data.create_quotation \
                    or pt_data.create_purchase_requisition \
                    or pt_data.create_sale_quotation \
                    or pt_data.update_agenda \
                    or pt_data.accreditation_request_generation \
                    or pt_data.set_obtained_accreditation \
                    or pt_data.del_obtained_accreditation \
                    or pt_data.create_maintenance_fee_tasks \
                    or pt_data.create_maintenance_fee_offer \
                    or pt_data.create_child_project \
                    or pt_data.get_accreditation_test \
                    or pt_data.req_supervision \
                    or pt_data.doclite_action:

                    res[work_data.id] = True
        return res

    def _display_date_obtained_accreditation(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for work_data in self.browse(cr, uid, ids, context=context):
            res[work_data.id] = False
            if work_data.type_id and work_data.type_id.set_obtained_accreditation:
                res[work_data.id] = True
        return res

    _columns = {'type_id': fields.many2one('accreditation.task.work.type',
                                           'Type of work',
                                           ondelete="cascade"),
                'description': fields.text('Description'),
                'phase_id': fields.related('task_id',
                                           'phase_id',
                                           type="many2one",
                                           relation="project.phase",
                                           string='Audit',
                                           store=False),
                'department_id': fields.related('task_id',
                                                'project_id',
                                                'analytic_account_id',
                                                'department_id',
                                                type="many2one",
                                                relation="hr.department",
                                                string='Dipartimento',
                                                store=False),
                'project_state': fields.related('task_id',
                                                'project_id',
                                                'state',
                                                type="char",
                                                relation="project.project",
                                                string='Project State',
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
                'not_billing': fields.boolean('Not Billing'),
                'project_task_state': fields.related('task_id',
                                                     'state',
                                                     type="char",
                                                     relation="project.task",
                                                     string='Task State',
                                                     store=False),
                'person_id': fields.many2one('res.partner',
                                             domain=[('individual', '=', True),
                                                     ],
                                             string='Persona Fisica'),
                'customer_order_reference': fields.char('Riferimento ordine cliente',
                                                        size=64),
                'meeting_id':  fields.many2one('calendar.event', 'Meeting'),
                'unit_id': fields.many2one('accreditation.units', 'Unità'),
                'date_end': fields.date('Data Finale'),

                'audit_visit_doc_review': fields.boolean('Attività di Visita/Esame documentale'),
                'audit_visit_accompaniment': fields.boolean('Attività di Visita in Accompagnamento'),

                'display_button': fields.function(_get_display_button,
                                                  type='boolean',
                                                  string="Hidden",
                                                  store=False),
                'display_date_obtained_accreditation': fields.function(
                    _display_date_obtained_accreditation, type='boolean', string="Hidden", store=False),
                'date_obtained_accreditation': fields.date('Data di Accreditamento'),
                'exec_date': fields.datetime('Data e Ora Esecuzione'),
                'last_protocol': fields.char(size=100,
                                             string='Ultimo Protocollo'),
                }

    _defaults = {'date': None,
                 'date_obtained_accreditation': None,
                 }

    def onchange_project(self, cr, uid, ids, project_id, task_id, context=None):

        if task_id and context:
            if not context.get('wiew_task_form', False):
                return {'value': {'task_id': None,
                                  'unit_id': None,
                                  }
                        }
        return {'value': {'unit_id': None,
                          }
                }

    def onchange_type_id(self, cr, uid, ids, type_id, context=None):
        if type_id:
            pt_obj = self.pool.get('accreditation.task.work.type')
            pt_data = pt_obj.browse(cr, uid, type_id)

            t_display_button = False
            if pt_data.create_audit \
              or pt_data.create_line_to_invoice \
              or pt_data.create_quotation \
              or pt_data.create_purchase_requisition \
              or pt_data.create_sale_quotation \
              or pt_data.update_agenda \
              or pt_data.accreditation_request_generation \
              or pt_data.set_obtained_accreditation \
              or pt_data.del_obtained_accreditation \
              or pt_data.create_maintenance_fee_tasks \
              or pt_data.create_maintenance_fee_offer \
              or pt_data.create_child_project \
              or pt_data.get_accreditation_test \
              or pt_data.req_supervision \
              or pt_data.doclite_action:
                t_display_button = True

            return {'value': {'audit_visit_doc_review': pt_data.audit_visit_doc_review,
                              'audit_visit_accompaniment': pt_data.audit_visit_accompaniment,
                              'display_button': t_display_button,
                              }
                    }
        return {'value': {'audit_visit_doc_review': None,
                          'audit_visit_accompaniment': None,
                          'display_button': False,
                          }
                }

    def duplicate_work(self, cr, uid, ids, default={}, context=None):
        context = context or {}
        if default is None:
            default = {}
        default.update({'date_end': None,
                        'date': None,
                        'exec_date': None,
                        })
        t_person = default.get('person_id')
        context.update({'person_id': t_person})
        res = super(project_task_work, self).duplicate_work(cr, uid, ids, default, context)
        return res

    def copy(self, cr, uid, ids, default=None, context=None):
        context = context or {}
        if default is None:
            default = {}
        default.update({'date_end': None,
                        'date': None,
                        'exec_date': None,
                        })
        res = super(project_task_work, self).copy(cr, uid, ids, default, context)
        return res

    def save_work_and_next(self, cr, uid, ids, default={}, context=None):

        if context is None:
            context = {}

        super(project_task_work, self).write(cr, uid, ids, default, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'project_accredia',
                                              'view_project_task_work_form_accredia')
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

        t_date = self.browse(cr, uid, ids[0]).date
        if t_date:
            context.update({'day': t_date[:10]})
        t_user_id = default.get('user_id')
        context.update({'user_id': t_user_id})

        t_flag = default.get('default_day_works_flag') or default.get('day_works_flag')

        if t_flag:
            return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

        return res

    def save_work_complete_task(self, cr, uid, ids, default={},
                                context=None):
        if context is None:
            context = {}
        res = super(project_task_work, self).write(cr, uid, ids, default, context)
        value = self.browse(cr, uid, ids)[0]
        t_task = value.task_id.id
        task_obj = self.pool.get('project.task')
        data = task_obj.browse(cr, uid, [t_task])
        if data and data[0]:
            # task_obj._check_child_task(cr, uid, ids, context=context)
            task_obj.case_close(cr, uid, [t_task], context=context)

        t_date = self.browse(cr, uid, ids[0]).date
        context.update({'day': t_date and t_date[:10] or None})
        t_user_id = default.get('user_id')
        context.update({'user_id': t_user_id})

        t_flag = default.get('default_day_works_flag') or default.get('day_works_flag')

        if t_flag:
            return self.pool.get('wizard.select.date').view_day_works(cr, uid, ids, context)

        return res

    # a seconda del flag di not_billing. Il controllo non viene
    # effettuato se il lavoro è di tipo
    # ZZ che serve per gestire il pregresso id=30    utilizzo l'id perchè
    # da vals ho solo l'id

    def onchange_task(self, cr, uid, ids, task_id, context=None):
        if not task_id:
            return {}
        task_data = self.pool.get('project.task').browse(cr, uid, task_id)
        t_task_planned = task_data.planned_hours
        t_task_effective = task_data.effective_hours

        return {'value': {'project_task_planned_hours': t_task_planned,
                          'project_task_effective_hours': t_task_effective,
                          }}
        return {}

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if not context.get('no_analytic_entry', False):
            ctx.update({'no_analytic_entry': True})

        task_res = super(project_task_work, self).create(cr,
                                                         uid,
                                                         vals,
                                                         context=ctx)
        return task_res

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for data in self.browse(cr, uid, ids):
            t_date = data.date or ''
            descr = ("%s %s") % (data.name, t_date)
            if not data.name:
                if data.type_id and data.type_id.name:
                    descr = ("%s %s") % (data.type_id.name, t_date)

            res.append((data.id, descr))
        return res
