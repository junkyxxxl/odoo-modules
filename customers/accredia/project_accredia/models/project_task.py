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

from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp import fields, models, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class ProjectTask(models.Model):

    _inherit = "project.task"

    def onchange_project(self, cr, uid, ids, project_id=False, context=None):
        if context is None:
            context = {}
        res = super(ProjectTask, self).onchange_project(cr, uid, ids, project_id, context)

        if not res:
            res['value'] = {}

        res['value']['accreditation_project_type_new'] = False
        res['value']['accreditation_project_type_extension'] = False
        res['value']['accreditation_project_type_renew'] = False

        if project_id:
            project_obj = self.pool.get('project.project')
            project_data = project_obj.browse(cr, uid, project_id)
            if project_data.accreditation_project_type:
                type_data = project_data.accreditation_project_type
                res['value']['accreditation_project_type_new'] = type_data.is_new
                res['value']['accreditation_project_type_extension'] = type_data.is_extension
                res['value']['accreditation_project_type_renew'] = type_data.is_renew

        return res

    def onchange_planned(self, cr, uid, ids, planned=0.0, effective=0.0):
        remaining = 0.0
        if isinstance(planned, float) and isinstance(effective, float):
            remaining = planned - effective
        return {'value': {'remaining_hours': remaining}}

    @api.one
    def get_responsible(self):
        self.fnct_responsible = None
        for team_data in self.task_team_ids:
            if team_data.task_leader:
                self.fnct_responsible = team_data.user_id and team_data.user_id.partner_id or None
                break

    @api.one
    def _get_display_red_date(self):
        self.display_red_date = False
        if not self.color or self.color != 4:
            if not self.date_end and self.date_deadline:
                current_date = fields.Date.context_today(self)
                if self.date_deadline < current_date:
                    self.display_red_date = True

    @api.one
    def _get_calendar_color(self):
        self.calendar_color = 1
        if self.color and self.color == 4:
            self.calendar_color = 4

    @api.multi
    def action_duplicate_group(self):
        task_obj = self.pool.get('project.task')
        if len(self) != 1:
            raise except_orm(_("Attenzione!"),
                             _("Per questa funzione è possibile selezionare solamente una Attività per volta."))

        t_copy_group_id = self.copy_group_id and self.copy_group_id.id or None

        tasks_dict = {}
        tasks_parent_dict = {}
        tasks_child_dict = {}
        new_parent_dict = {}
        new_child_dict = {}
        tasks_list = []
        copy_list = []
        for tasks_data in self.project_id.tasks:
            if tasks_data.copy_group_id and tasks_data.copy_group_id.id == t_copy_group_id and not tasks_data.is_group_duplicated:
                if tasks_data.id not in tasks_dict:
                    tasks_dict.update({tasks_data.id: None})
                    tasks_parent_dict.update({tasks_data.id: []})
                    tasks_child_dict.update({tasks_data.id: []})
                    tasks_list.append(tasks_data)
                    for parent_data in tasks_data.parent_ids:
                        tasks_parent_dict[tasks_data.id].append(parent_data.id)
                    for child_data in tasks_data.child_ids:
                        tasks_child_dict[tasks_data.id].append(child_data.id)

        for t_tocopy_data in tasks_list:
            t_tocopy_data.write({'is_group_duplicated': True})
            # creazione attività
            t_task_team_ids = []
            for t_team_data in t_tocopy_data.task_team_ids:
                t_task_team_ids.append(t_team_data.id)
            copy_id = self.create({
                'name': t_tocopy_data.name,
                'project_id': t_tocopy_data.project_id and t_tocopy_data.project_id.id or None,
                'partner_id': t_tocopy_data.partner_id and t_tocopy_data.partner_id.id or None,
                'copy_group_id': t_tocopy_data.copy_group_id and t_tocopy_data.copy_group_id.id or None,
                'is_copy_group_last': t_tocopy_data.is_copy_group_last,
                'product_id': t_tocopy_data.product_id and t_tocopy_data.product_id.id or None,
                'journal_id': t_tocopy_data.journal_id and t_tocopy_data.journal_id.id or None,
                'uom_id': t_tocopy_data.uom_id and t_tocopy_data.uom_id.id or None,
                'codice_cig': t_tocopy_data.codice_cig,
                'delay_deadline': t_tocopy_data.delay_deadline,
                'days_advance_from_deadline': t_tocopy_data.days_advance_from_deadline,
                'category_id': t_tocopy_data.category_id and t_tocopy_data.category_id.id or None,
                'stage_id': t_tocopy_data.stage_id and t_tocopy_data.stage_id.id or None,
                'phase_id': t_tocopy_data.phase_id and t_tocopy_data.phase_id.id or None,
                'unit_id': t_tocopy_data.unit_id and t_tocopy_data.unit_id.id or None,
                'task_team_ids': [(6, 0, t_task_team_ids)],
                'stage_id': self._default_task_stage_id(),
                })
            copy_list.append(copy_id.id)
            tasks_dict[t_tocopy_data.id] = copy_id.id

            # copia lavorazioni
            for work_data in t_tocopy_data.work_ids:
                self.env['project.task.work'].create({
                    'name': work_data.name,
                    'project_id': work_data.project_id and work_data.project_id.id or None,
                    'task_id': copy_id.id,
                    'user_id': work_data.user_id and work_data.user_id.id or None,
                    'company_id': work_data.company_id and work_data.company_id.id or None,
                    'description': work_data.description,
                    'type_id': work_data.type_id and work_data.type_id.id or None,
                    'not_billing': work_data.not_billing,
                    'audit_visit_accompaniment': work_data.audit_visit_accompaniment,
                    'customer_order_reference': work_data.customer_order_reference,
                    'audit_visit_doc_review': work_data.audit_visit_doc_review,
                    'unit_id': work_data.unit_id and work_data.unit_id.id or None,
                    'person_id': work_data.person_id and work_data.person_id.id or None,
                    'last_protocol': work_data.last_protocol,
                    })

        # calcolo parent e child
        for t_tocopy_data in tasks_list:
            t_new_id = tasks_dict[t_tocopy_data.id]
            if t_new_id not in new_parent_dict:
                new_parent_dict.update({t_new_id: []})
            for t_parent_id in tasks_parent_dict[t_tocopy_data.id]:
                if t_parent_id in tasks_dict:
                    new_parent_dict[t_new_id].append(tasks_dict[t_parent_id])
                else:
                    new_parent_dict[t_new_id].append(t_parent_id)
            if t_new_id not in new_child_dict:
                new_child_dict.update({t_new_id: []})
            for t_child_id in tasks_child_dict[t_tocopy_data.id]:
                if t_child_id in tasks_dict:
                    new_child_dict[t_new_id].append(tasks_dict[t_child_id])
                else:
                    new_child_dict[t_new_id].append(t_child_id)

        # scrittura parent
        for t_new_id in new_parent_dict:
            t_new_data = self.browse(t_new_id)
            t_parent_list = []
            for parent_data in t_new_data.parent_ids:
                t_parent_list.append(parent_data.id)
            for t_parent_id in new_parent_dict[t_new_id]:
                if t_parent_id not in t_parent_list:
                    t_parent_list.append(t_parent_id)
                    task_obj.write(self._cr, self._uid, t_new_id, {'parent_ids': [(4, t_parent_id)]})

        # scrittura child
        for t_new_id in new_child_dict:
            t_new_data = self.browse(t_new_id)
            t_child_list = []
            for child_data in t_new_data.child_ids:
                t_child_list.append(child_data.id)
            for t_child_id in new_child_dict[t_new_id]:
                if t_child_id not in t_child_list:
                    t_child_list.append(t_child_id)
                    task_obj.write(self._cr, self._uid, t_new_id, {'child_ids': [(4, t_child_id)]})

        if copy_list:
            result = self.env['ir.model.data'].get_object_reference('project_accredia',
                                                                    'view_project_task_accredia_ext_form')
            view_id = result and result[1] or False

            return {'domain': "[('id','in', ["+','.join(map(str, copy_list))+"])]",
                    'name': _("Attività Copiate"),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'project.task',
                    'type': 'ir.actions.act_window',
                    'views': [(False, 'tree'), (view_id, 'form')],
                    }

        return True

    @api.multi
    def case_close(self):
        for task in self:
            for parent in task.parent_ids:
                if parent.fnct_state in ['pending', 'draft']:
                    reopen = True
                    for child in parent.child_ids:
                        if child.id != task.id and child.fnct_state not in ('done', 'cancelled'):
                            reopen = False
                    if reopen:
                        parent.do_reopen()

            t_date_end = task.date_end or fields.Datetime.now()
            t_req_supervision_days = task.req_supervision_days

            for child in task.child_ids:
                if t_req_supervision_days:
                    delay = timedelta(days=t_req_supervision_days)
                    t_date = datetime.strptime(task.date_deadline, DF).date()
                    child.date_deadline = str(t_date - delay)
                elif child.days_advance_from_deadline and task.date_deadline:
                    delay = timedelta(days=child.days_advance_from_deadline)
                    t_date = datetime.strptime(task.date_deadline, DF).date()
                    child.date_deadline = str(t_date - delay)
                elif child.delay_deadline:
                    delay = timedelta(days=child.delay_deadline)
                    t_date = datetime.strptime(t_date_end, DTF).date()
                    child.date_deadline = str(t_date + delay)
            if task.phase_id:
                # (conferma preventivi fornitori: effettuata in accredia_purchase)

                # approva tempi e materiali
                to_invoice = None
                try:
                    to_invoice = self.env['ir.model.data'].get_object_reference(
                        'hr_timesheet_invoice', 'timesheet_invoice_factor1')
                except ValueError:
                    pass

                if to_invoice:
                    for t_line in task.analytic_line_ids:
                        # TODO da fare anche se t_line.to_invoice è impostato?
                        for work in task.work_ids:
                            to_invoice_close = work.type_id.to_invoice_close
                            if to_invoice_close:
                                t_line.to_invoice = to_invoice_close

                        if not t_line.to_invoice:
                            t_line.to_invoice = to_invoice[1]

            # close task
            task.color = 4
            task.remaining_hours = 0.0
            task.date_end = t_date_end
        return True

    @api.one
    def do_reopen(self):
        self.color = None
        self.date_end = None
        return True

    @api.multi
    def add_parent_task(self):

        t_task_id = None
        t_project_id = None
        for task_data in self:
            t_task_id = task_data.id
            t_project_id = task_data.project_id and task_data.project_id.id or None

        result = self.env['ir.model.data'].get_object_reference('project_accredia', 'wizard_task_create_parent_form')

        ctx = dict(self._context)
        ctx.update({'default_task_id': t_task_id,
                    'default_project_id': t_project_id,
                    })
        view_id = result and result[1] or False

        return {'name': _("Aggiungi Attivita Genitore"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.task.create.parent',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'context': ctx,
                'target': 'new',
                }

    @api.multi
    def add_child_task(self):
        t_task_id = None
        t_project_id = None
        for task_data in self:
            t_task_id = task_data.id
            t_project_id = task_data.project_id and task_data.project_id.id or None

        result = self.env['ir.model.data'].get_object_reference('project_accredia', 'wizard_task_create_child_form')

        ctx = dict(self._context)
        ctx.update({'default_parent_id': t_task_id,
                    'default_project_id': t_project_id,
                    })
        view_id = result and result[1] or False

        return {'name': _("Aggiungi Attivita Delegata"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.task.create.child',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'context': ctx,
                'target': 'new',
                }

    @api.one
    def _get_fnct_project_state(self):
        self.fnct_project_state = None
        if self.project_id:
            self.fnct_project_state = self.project_id.state



    @api.one
    def _get_fnct_state(self):
        self.fnct_state = None
        if self.color and self.color == 4:
            self.fnct_state = 'Done'
        elif self.stage_id.name:
            self.fnct_state = self.stage_id.name

    @api.multi
    def _get_dom_analytic_line_ids(self):
        for task in self:
            task.dom_analytic_line_ids = []
            for line in task.analytic_line_ids:
                if line not in task.dom_analytic_line_ids:
                    if not line.to_invoice:
                        task.dom_analytic_line_ids += line
                    else:
                        if line.to_invoice.to_be_confirmed:
                            task.dom_analytic_line_ids += line
                        elif line.to_invoice.customer_name == '100%':
                            task.dom_analytic_line_ids += line
    @api.multi
    def _default_task_stage_id(self):
        type_obj = self.env['project.task.type']
        task_type_ids = type_obj.search([('audit', '=', True)],limit=1)
        if task_type_ids:
            return task_type_ids.id

        return None

    unit_id = fields.Many2one('accreditation.units', 'Unit')
    task_team_ids = fields.One2many('accreditation.task.team', 'task_id', 'Task Team')
    fnct_responsible = fields.Many2one(compute='get_responsible',
                                       comodel_name='res.partner',
                                       string="Responsible")
    display_red_date = fields.Boolean(compute='_get_display_red_date', string="Hidden")
    fnct_state = fields.Char(compute='_get_fnct_state', string='Get State', store=False)
    calendar_color = fields.Integer(compute='_get_calendar_color', string='Calendar Color')
    # Timesheet
    product_id = fields.Many2one(
        'product.product', 'Product',
        help="Specifies employee's designation as a product with type 'service'.")
    journal_id = fields.Many2one('account.analytic.journal', 'Analytic Journal')
    uom_id = fields.Many2one(related='product_id.uom_id',
                             comodel_name='product.uom',
                             string='Unit of Measure',
                             store=True)
    # Attività nelle pratiche
    num_non_conformita = fields.Integer('Non Conformità', help='Numero di Non Conformità')
    num_osservazioni = fields.Integer('Osservazioni', help='Numero di Osservazioni')
    num_commenti = fields.Integer('Commenti', help='Numero di Commenti')
    project_partner_id = fields.Many2one(related='project_id.partner_id',
                                         comodel_name='res.partner',
                                         string='Ente', store=False, readonly=False)
    analytic_line_ids = fields.One2many('account.analytic.line', 'task_id', 'Attività da Fatturare')

    codice_cig = fields.Char('Codice CIG', size=64)

    dom_analytic_line_ids = fields.One2many(compute='_get_dom_analytic_line_ids',
                                            comodel_name='account.analytic.line',
                                            string="Domain Attività da Fatturare",
                                            store=False)
    delay_deadline = fields.Integer('Giorni Ritardo')
    days_advance_from_deadline = fields.Integer('Giorni Anticipo da Scadenza')

    auth_ids = fields.Many2many(comodel_name='accreditation.persons.auth',
                                relation="accreditation_persons_auth_task_rel",
                                column1='task_id',
                                column2='auth_id',
                                string='Autorizzazioni')
    category_id = fields.Many2one('project.task.category', 'Categoria', ondelete="cascade")

    accreditation_project_type_new = fields.Boolean(related='project_id.accreditation_project_type.is_new',
                                                    string='Hidden')
    accreditation_project_type_extension = fields.Boolean(related='project_id.accreditation_project_type.is_extension',
                                                          string='Hidden')
    accreditation_project_type_renew = fields.Boolean(related='project_id.accreditation_project_type.is_renew',
                                                      string='Hidden')

    analytic_account_id = fields.Many2one(related='project_id.analytic_account_id',
                                          comodel_name='account.analytic.account',
                                          string='Conto Analitico')

    fnct_project_state = fields.Char(compute='_get_fnct_project_state',
                                     string='Get Project State',
                                     store=False)


    copy_group_id = fields.Many2one('accreditation.project.task.grouping', 'Raggruppamento')
    is_copy_group_last = fields.Boolean('Ultima Attività')
    is_group_duplicated = fields.Boolean('Gruppo già duplicato', default=False)

    req_supervision_days = fields.Integer('Giorni per Sorveglianza')

    _defaults = {'stage_id': _default_task_stage_id,
                 }

    def _get_default_stage_id(self, cr, uid, context=None):
        """ Overrides default stage_id """
        # TODO da rivedere?
        return None

    @api.one
    def copy(self, default=None):
        default = dict(default or {})

        # Se sto duplicando un template devo settare l'utente corrente
        if self.project_id and self.project_id.state == 'template':
            default.update({'user_id': self._uid})
        result = super(ProjectTask, self).copy(default)

        if self.project_id and self.project_id.state == 'template':
            t_default = {'hours': 0.0,
                         'date': None,
                         'project_id': result.project_id.id,
                         'task_id': result.id,
                         'user_id': self._uid,
                         }
            for work in self.work_ids:
                self.pool['project.task.work'].copy(self._cr, self._uid, work.id, default=t_default, context=self._context)

        return result

    @api.multi
    @api.depends('name,' 'project_id.name')
    def name_get(self):
        res = []

        t_obj_type = self._context.get('t_obj', None)

        for rp in self:
            descr = ("%d - %s") % (rp.id, rp.name)
            if rp.project_id and t_obj_type and t_obj_type == 'mission':
                #descr = ("%d - %s - %s") % (rp.id, rp.name, rp.project_id.name)
                descr = ("%d - %s") % (rp.id, rp.name)
            res.append((rp.id, descr))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        try:
            args = args + [('id', '=', int(name))]
        except ValueError:
            args = args + [('name', operator, name)]

        t_user_id = self._context.get('t_user_id', False)

        if t_user_id:
            args += [('task_team_ids.user_id', '=', t_user_id)]

        return super(ProjectTask, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

    def _check_child_task(self, cr, uid, ids, context=None):
        # controllo disabilitato
        return True

    @api.model
    def create(self, vals):
        t_delay_deadline = None
        t_days_advance_from_deadline = None
        if 'delay_deadline' in vals and vals['delay_deadline']:
            t_delay_deadline = vals['delay_deadline']
        if'days_advance_from_deadline' in vals and vals['days_advance_from_deadline']:
            t_days_advance_from_deadline = vals['days_advance_from_deadline']
        if t_delay_deadline and t_days_advance_from_deadline:
            raise except_orm(_("Attenzione!"),
                             _("Non è possibile impostare contemporaneamente sia i Giorni Ritardo che i Giorni anticipo da scadenza."))
        return super(ProjectTask, self).create(vals)

    @api.multi
    def write(self, vals):
        force_stage_id = self._context.get('force_stage_id', False )
        for task_data in self:
            if not force_stage_id:
                if 'stage_id' in vals and vals['stage_id']:
                    if task_data.project_id and task_data.project_id.state and task_data.project_id.state != 'template':
                        del vals['stage_id']
            t_delay_deadline = task_data.delay_deadline
            t_days_advance_from_deadline = task_data.days_advance_from_deadline
            if 'delay_deadline' in vals:
                t_delay_deadline = vals['delay_deadline']
            if'days_advance_from_deadline' in vals:
                t_days_advance_from_deadline = vals['days_advance_from_deadline']
            if t_delay_deadline and t_days_advance_from_deadline:
                raise except_orm(_("Attenzione!"),
                                 _("Non è possibile impostare contemporaneamente sia i Giorni Ritardo che i Giorni anticipo da scadenza."))
        return super(ProjectTask, self).write(vals)


