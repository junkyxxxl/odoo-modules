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

from openerp import fields, models, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime


class ProjectPhase(models.Model):

    _inherit = "project.phase"

    @api.multi
    def set_done(self):
        result = super(ProjectPhase, self).set_done()

        for phase in self:
            for task in phase.task_ids:
                task.case_close()
        return result

    @api.multi
    def set_cancel(self):

        for phase in self:
            for task in phase.task_ids:
                for work in task.work_ids:
                    for log in work.log_ids:
                        if log.analytic_line_id and log.analytic_line_id.invoice_id:
                            raise except_orm(_('Attenzione'),
                                             _("Impossibile annullare l'Audit: l'attività è già stata fatturata!"))
                        if log.purchase_order_id:
                            order_name = log.purchase_order_id.name
                            if log.purchase_order_id.state == 'approved' or log.purchase_order_id.state == 'done':
                                raise except_orm(_('Attenzione'),
                                                 _("Impossibile annullare l'Audit: il preventivo fornitore %s è stato trasformato in ordine!") % (order_name))

                        log.meeting_id and log.meeting_id.unlink()
                        log.purchase_order_id and log.purchase_order_id.action_cancel()
                        log.analytic_line_id and log.analytic_line_id.unlink()

        return super(ProjectPhase, self).set_cancel()

    @api.multi
    def do_plan(self):

        for phase_data in self:
            if not phase_data.project_id:
                raise except_orm(_('Attenzione'),
                                 _("Non è stata specificata la Pratica per l'Audit!"))
            t_unit_id = None
            task_plan_data = None

            if not phase_data.type_audit_type_id:
                raise except_orm(_('Attenzione'),
                                 _("Non è stato configurato lo Stadio Attività per l'Audit!"))
            if not phase_data.type_audit_visit:
                raise except_orm(_('Attenzione'),
                                 _("Non è stato configurato il Tipo Attività Visita per l'Audit!"))
            if not phase_data.type_audit_doc_review:
                raise except_orm(_('Attenzione'),
                                 _("Non è stato configurato il Tipo Attività Esame Documentale per l'Audit!"))

            # recupero unità principale
            for unit_data in phase_data.project_id.project_unit_ids:
                if unit_data.is_main:
                    t_unit_id = unit_data.id
                    break

            t_department_id = phase_data.project_id.department_id.id
            t_stage_id = phase_data.type_audit_type_id and phase_data.type_audit_type_id.id

            # per ogni membro del team creo due righe
            for team_data in phase_data.project_id.team_ids:

                if phase_data.action_type_id:
                    task_plan_data = self.env['accreditation.task.plan'].search([('department_id', '=', t_department_id),
                                                                                 ('task_work_type_id', '=', phase_data.action_type_id.id),
                                                                                 ('stage_id', '=', t_stage_id),
                                                                                 ('role_id', '=', team_data.role_id.id)
                                                                                 ],
                                                                                limit=1)

                dict_data = {
                    'unit_id': t_unit_id,
                    'user_id': team_data.user_id.id,
                    'role_id': team_data.role_id.id,
                    'phase_id': phase_data.id,
                }

                if not team_data.role_id.exclude_type_audit_visit or not phase_data.type_audit_visit:

                    # riga 1
                    dict_data.update({'task_audit_type_id': phase_data.type_audit_visit and phase_data.type_audit_visit.id or None, })
                    if task_plan_data:
                        t_days_audit_visit = task_plan_data.days_audit_visit
                        dict_data.update({'num_days': t_days_audit_visit, })
                    self.env['project.user.allocation'].create(dict_data)

                if not team_data.role_id.exclude_type_audit_doc_review or not phase_data.type_audit_doc_review:

                    # riga 2
                    dict_data.update({'task_audit_type_id': phase_data.type_audit_doc_review and phase_data.type_audit_doc_review.id or None, })
                    if task_plan_data:
                        t_days_audit_doc_review = task_plan_data.days_audit_doc_review
                        dict_data.update({'num_days': t_days_audit_doc_review, })
                    self.env['project.user.allocation'].create(dict_data)

        return True

    @api.multi
    def do_confirm(self):

        for phase_data in self:
            if not phase_data.type_audit_type_id:
                raise except_orm(_('Attenzione'),
                                 _("Non è stato configurato lo Stadio Attività per l'Audit!"))

            t_task_type_id = phase_data.type_audit_type_id and phase_data.type_audit_type_id.id or None
            t_type_audit_category_id = phase_data.type_audit_category_id and phase_data.type_audit_category_id.id or None

            t_project_id = phase_data.project_id.id
            task_dict = {'project_id': t_project_id,
                         'phase_id': phase_data.id,
                         'stage_id': t_task_type_id,
                         'name': '/',
                         'category_id': t_type_audit_category_id,
                         }

            t_unit_list = []
            for user_data in phase_data.user_ids:

                # controlli campi obbligatori
                if not user_data.unit_id:
                    raise except_orm(_('Attenzione'),
                                     _("Il campo Unità è obbligatorio in ogni riga!"))
                if not user_data.user_id:
                    raise except_orm(_('Attenzione'),
                                     _("Il campo Ispettore è obbligatorio in ogni riga!"))
                if not user_data.role_id:
                    raise except_orm(_('Attenzione'),
                                     _("Il campo Ruolo è obbligatorio!"))
                if not user_data.task_audit_type_id:
                    raise except_orm(_('Attenzione'),
                                     _("Il campo Tipo Attività è obbligatorio!"))

                # controlli per dipendenti PA
                if user_data.user_id and user_data.user_id.is_employee_pa:
                    if not user_data.auth_id:
                        raise except_orm(_('Attenzione'),
                                         _("Il campo Autorizzazione è obbligatorio in ogni riga, nel caso l'ispettore sia un dipendente PA!"))
                    if user_data.auth_id.auth_type == 'S':
                        if user_data.auth_id.task_ids:
                            raise except_orm(_('Attenzione'),
                                             _("L'autorizzazione per l'ispettore %s è già stata utilizzata!") % (user_data.user_id.name))
                    if user_data.auth_id.auth_type == 'D':
                        if user_data.auth_id.days_remaining < user_data.num_days:
                            raise except_orm(_('Attenzione'),
                                             _("L'autorizzazione per l'ispettore %s supera il limite dei giorni disponibili!") % (user_data.user_id.name))

                # caricamento struttura dati (unit, user, role, auth, tipo, date_start, date_end)
                tuple_unit = user_data.unit_id.id
                tuple_user = user_data.user_id.id
                tuple_role = user_data.role_id.id
                tuple_auth = user_data.user_id.is_employee_pa and user_data.auth_id.id or None
                tuple_type = user_data.task_audit_type_id.id
                tuple_date_start = user_data.date_start
                tuple_date_end = user_data.date_end
                t_unit_list.append((tuple_unit, tuple_user, tuple_role, tuple_auth, tuple_type, tuple_date_start, tuple_date_end))

            for t_unit_id, t_user_id, t_role_id, t_auth_id, t_type_id, t_date_start, t_date_end in t_unit_list:

                t_project_unit_ids = []
                for unit_data in phase_data.project_id.project_unit_ids:
                    if unit_data.id not in t_project_unit_ids:
                        t_project_unit_ids.append(unit_data.id)
                        break

                msg = _("Assicurarsi che tutte le Date di Inizio e Fine siano impostate!")
                if not t_date_start:
                    raise except_orm(_('Attenzione'), msg)

                if not t_date_end:
                    raise except_orm(_('Attenzione'), msg)

                if not t_project_unit_ids:
                    raise except_orm(_('Attenzione'),
                                     _("Non esiste alcuna Unità %d associata al progetto %d!") % (t_unit_id, t_project_id))

                task_dict.update({'unit_id': t_unit_id,
                                  'date_start': t_date_start + " 07:00:00",
                                  'date_end': t_date_end + " 17:00:00",
                                  'user_id': t_user_id,
                                  })
                res = self.env['project.task'].create(task_dict)

                t_flag_first = False
                t_description_team = '(Team: '

                t_partner_data = self.env['res.users'].browse(t_user_id).partner_id

                if t_auth_id:
                    res.write({'auth_ids': [(4, t_auth_id)]})

                self.env['accreditation.task.team'].create({'user_id': t_user_id,
                                                            'role_id': t_role_id,
                                                            'task_id': res.id,
                                                            })
                self.env['project.task.work'].create({'project_id': phase_data.project_id.id,
                                                      'task_id': res.id,
                                                      'unit_id': t_unit_id,
                                                      'user_id': t_user_id,
                                                      'type_id': t_type_id,
                                                      })

                roles_data = self.env['accreditation.roles'].browse(t_role_id)
                t_roles_descr = roles_data.description or ''
                t_partner_title = t_partner_data.title and t_partner_data.title.name or ''
                t_partner_name = t_partner_data.name or ''
                if t_flag_first:
                    t_description_team += ', '
                t_description_team += t_roles_descr + ' ' + t_partner_title + ' ' + t_partner_name
                t_flag_first = True

                t_description_team += ')'
                t_name = phase_data.type_audit_type_id.name
                if user_data.date_start and user_data.date_end:
                    t_date_start = datetime.strftime(datetime.strptime(tuple_date_start, DF), "%d/%m/%Y")
                    t_date_end = datetime.strftime(datetime.strptime(tuple_date_end, DF), "%d/%m/%Y")
                    t_name += ' (dal ' + t_date_start + ' al ' + t_date_end + ')'

                #res.description = t_name + ' ' + t_description_team
                res.description = 'AUDIT ' + t_name + ' ' + phase_data.project_id.name
                res.name = res.description or '/'

                # Esegue azioni
                for work in res.work_ids:
                    work.do_action()
            # Conferma Audit
            phase_data.set_confirmed()
        return True

    @api.multi
    def do_set_date(self):
        t_phase_id = None
        for phase_data in self:
            t_phase_id = phase_data.id

        result = self.env['ir.model.data'].get_object_reference('project_accredia', 'wizard_set_date_view')

        ctx = dict(self._context)
        ctx.update({'default_phase_id': t_phase_id,
                    })
        view_id = result and result[1] or False

        return {'name': _("Imposta date"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.set.date',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'context': ctx,
                'target': 'new',
                }

    @api.multi
    def write(self, vals):
        res = super(ProjectPhase, self).write(vals)

        for phase_data in self:
            for user_data in phase_data.user_ids:

                # controlli di compatibilità
                if phase_data.project_id and phase_data.project_id.partner_id and user_data.user_id:
                    for function_data in phase_data.project_id.partner_id.persons_ids:
                        if function_data.partner_id and function_data.partner_id.id == user_data.user_id.partner_id.id:
                            raise except_orm(_('Attenzione'),
                                             _("L'ispettore %s non è compatibile con l'ente %s!") % (user_data.partner_id.name, phase_data.project_id.partner_id.name))

        return res

    @api.multi
    def _get_standard_id(self):
        for item in self:
            item.filter_standard_id = None
            if item.project_id and item.project_id.standard_id:
                project = item.project_id
                if project.accreditation_project_type_new \
                  or project.accreditation_project_type_extension \
                  or project.accreditation_project_type_renew:
                    item.filter_standard_id = project.standard_id


    @api.multi
    def _get_filter_standard_id(self):
        #Questa funzione serve per reperire (senza salvare) il valore della norma relativa alla pratica
        project_id = self._context.get('active_id')
        project_obj = self.env['project.project'].browse(project_id)
        standard_id = project_obj.standard_id.id
        return standard_id


    type_audit_visit = fields.Many2one('accreditation.task.work.type', 'Tipo Attività Visita', states={'confirmed':[('readonly',True)], 'done':[('readonly',True)], 'cancelled':[('readonly',True)]})
    type_audit_doc_review = fields.Many2one('accreditation.task.work.type', 'Tipo Attività Esame Documentale', states={'confirmed':[('readonly',True)], 'done':[('readonly',True)], 'cancelled':[('readonly',True)]})
    type_audit_type_id = fields.Many2one('project.task.type', 'Stadio Attività', states={'confirmed':[('readonly',True)], 'done':[('readonly',True)], 'cancelled':[('readonly',True)]})
    type_audit_category_id = fields.Many2one('project.task.category', 'Categoria Attività', states={'confirmed':[('readonly',True)], 'done':[('readonly',True)], 'cancelled':[('readonly',True)]})

    include_not_available = fields.Boolean('Includi Non Disponibili')

    action_type_id = fields.Many2one('accreditation.task.work.type', 'Tipo Azione')

    filter_standard_id = fields.Many2one(compute='_get_standard_id',
                                         comodel_name='accreditation.standard',
                                         string='Filtro Norma',
                                         default=_get_filter_standard_id)
    enable_filter_standard_id = fields.Boolean(
        related='project_id.analytic_account_id.department_id.enable_filter_standard_id',
        string='Abilita Filtro Norma')

    audit_task_type = fields.Selection(
        [('foreseen', 'Previste'), ('planned', 'Pianificate')],
        string='Tipo Attività',
        default='planned')
