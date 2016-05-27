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

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.exceptions import Warning


class ProjectProject(models.Model):

    _inherit = "project.project"


    '''
     Serve a rendere readonly il campo numer certificato in base al flag settato a
     livello di utente.
    '''
    @api.one
    def _compute_certificate_readonly(self):
        if self.env.user.edit_number_certificate:
            self.readonly_certificate = False
        else:
            self.readonly_certificate = True

    readonly_certificate = fields.Boolean(compute='_compute_certificate_readonly')


    '''
    @api.multi
    def _get_partner_domain(self):
        #Prendo tutte le pratiche e per ognuna di esse controllo il tipo pratica,
        #e setto il campo relativo alla pratica, appena creato
        for record in self:
           accreditation_project_type_obj = record.accreditation_project_type
           is_committees_meeting = accreditation_project_type_obj.is_committees_meeting
           record.get_partner_domain = is_committees_meeting
    '''

    @api.one
    def _get_extension_ids(self):
        counter = 0
        for _ in self.child_ids:
            counter = counter + 1
        self.extension_ids_counter = str(counter)

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        ctx = self._context.copy()
        ctx.update({'copy': True, })
        default.update({'date_start': None,
                        'date': None,
                        'request_id': None,
                        'user_id': self._uid,
                        })
        return super(ProjectProject, self.with_context(ctx)).copy(default)

    @api.model
    def create(self, vals):

        if 'department_id' not in vals or not vals['department_id']:
            if 'analytic_account_id' not in vals or not vals['analytic_account_id']:
                raise except_orm(_('Attenzione'),
                                 _("Department is not specified for this project!"))
            if 'analytic_account_id' in vals and vals['analytic_account_id']:
                aaa_data = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
                if not aaa_data.department_id:
                    raise except_orm(_('Attenzione'),
                                     _("Department is not specified for this contract!"))
                vals['department_id'] = aaa_data.department_id.id

        t_department = vals['department_id']
        dep_data = self.env['hr.department'].browse(t_department)
        if dep_data and dep_data.project_sequence_id:
            # TODO
            t_seq = dep_data.project_sequence_id._next()
            vals['project_sequence'] = 'Accreditation n. ' + str(t_seq)

        vals['enable_tab_sectors'] = dep_data.enable_tab_sectors
        vals['enable_tab_tests'] = dep_data.enable_tab_tests

        if 'partner_id' not in vals or not vals['partner_id']:
            if 'analytic_account_id' in vals and vals['analytic_account_id']:
                aaa_data = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
                if not aaa_data.partner_id:
                    raise except_orm(_('Attenzione'),
                                     _("Partner is not specified for this contract!"))
                vals['partner_id'] = aaa_data.partner_id.id

        t_partner = vals['partner_id']

        if self._context.get('project_type_id', None):
            vals['accreditation_project_type'] = self._context.get('project_type_id', None)

        if 'accreditation_project_type' in vals and vals['accreditation_project_type']:
            t_project_type_id = vals['accreditation_project_type']

            if t_project_type_id:
                type_data = self.env['accreditation.project.type'].browse(t_project_type_id)
                if type_data.is_new or type_data.is_extension or type_data.is_renew:
                    # TODO da ottimizzare
                    proj_ids = self.env['project.project'].search(
                        [('partner_id', '=', t_partner),
                         ('serial_number_for_entity', '!=', None),
                         ('serial_number_for_entity', '!=', False),
                         ])
                    vals['serial_number_for_entity'] = len(proj_ids) + 1

                if (type_data.accreditation_request_days or type_data.accreditation_request_days == 0) and 'accreditation_due_date' in vals and vals['accreditation_due_date']:

                    t_date = str(datetime.strptime(vals['accreditation_due_date'], DF) - relativedelta(months=4))
                    vals['accreditation_request_due_date'] = t_date

        if 'user_id' in vals and vals['user_id']:
            user_data = self.env['res.users'].browse(vals['user_id'])
            if user_data.partner_id:
                vals['officer_id'] = user_data.partner_id.id

        res = super(ProjectProject, self).create(vals)

        req_id = 'request_id' in vals and vals['request_id'] or None

        accreq_obj = self.env['accreditation.request']
        if req_id and 'standard_id' in vals and vals['standard_id']:
            accreq_data = accreq_obj.browse(req_id)
            if not accreq_data.standard_id:
                accreq_data.write({'standard_id': vals['standard_id'], })
        if req_id and not self._context.get('copy', False) and not self._context.get('analytic_project_copy', False):
            accreq_data = accreq_obj.browse(req_id)
            accreq_data.write({'state': 'A', 'project_id': res.id, })

        t_person_events_list = []
        for t_person_events_data in res.person_events_ids:
            if t_person_events_data.partner_id and t_person_events_data.partner_id.id in t_person_events_list:
                raise except_orm(_('Attenzione'),
                                 _("La persona fisica può essere presente una sola volta nell'elenco dei partecipanti.!"))
            t_person_events_list.append(t_person_events_data.partner_id.id)

        return res

    @api.multi
    def write(self, vals):
        for data in self:

            if data.state == 'template' and not data.user_has_groups('project.group_project_manager'):
                vals_dict = vals.copy()
                if 'tasks' in vals_dict:
                    del vals_dict['tasks']
                if len(vals_dict.keys()) > 0:
                    raise except_orm(_('Attenzione'),
                                     _("Non puoi modificare il template perché non hai i permessi di Manager delle Pratiche!"))

            if data.user_id and data.user_id.id != self._uid and self._uid != SUPERUSER_ID:
                raise except_orm(_('Attenzione'),
                                 _("Non puoi modificare la pratica perché è stata assegnata ad un altro Funzionario!"))

            if data.state != 'template':
                if 'request_id' in vals and not vals['request_id']:
                    raise except_orm(_('Attenzione'),
                                     _("Non puoi rimuovere la richiesta perché è già stata associata a questo progetto!"))

                t_request_id = data.request_id and data.request_id.id or None
                if 'request_id' in vals:
                    t_request_id = vals['request_id']

                project_unit_ids_data = data.project_unit_ids
                if 'project_unit_ids' in vals and vals['project_unit_ids']:
                    t_project_unit_ids = vals['project_unit_ids']
                    t_unit_ids = []

                    for t_unit in t_project_unit_ids:
                        if t_unit[0] == 6:
                            t_unit_ids = t_unit_ids + t_unit[2]
                        if t_unit[0] == 4 or t_unit[0] == 2 and t_unit[1]:
                            t_unit_ids.append(t_unit[1])

                    project_unit_ids_data = self.env['accreditation.units'].browse(t_unit_ids)

                if t_request_id:
                    t_main_unit_list = []
                    for project_unit_data in project_unit_ids_data:
                        if project_unit_data.unit_category_id and project_unit_data.unit_category_id.is_main:
                            t_main_unit_list.append(project_unit_data.id)
                            break
                    if not t_main_unit_list:
                        raise except_orm(_('Attenzione'),
                                         _("Manca l'unità principale nella Tab Unità!"))

            if 'accreditation_due_date' in vals or 'accreditation_project_type' in vals:
                vals['accreditation_request_due_date'] = None
                t_project_type_id = None
                t_due_date = None
                if 'accreditation_project_type' in vals and vals['accreditation_project_type']:
                    t_project_type_id = vals['accreditation_project_type']
                if 'accreditation_due_date' in vals and vals['accreditation_due_date']:
                    t_due_date = vals['accreditation_due_date']
                if not t_project_type_id and 'accreditation_project_type' not in vals:
                    t_project_type_id = data.accreditation_project_type and data.accreditation_project_type.id or None
                if not t_due_date and 'accreditation_due_date' not in vals:
                    t_due_date = data.accreditation_due_date

                if t_project_type_id and t_due_date:
                    type_data = self.env['accreditation.project.type'].browse(t_project_type_id)

                    if type_data.accreditation_request_days or type_data.accreditation_request_days == 0:

                        t_date = str(datetime.strptime(t_due_date, DF) - relativedelta(months=4))
                        vals['accreditation_request_due_date'] = t_date

        if 'user_id' in vals:
            vals['officer_id'] = None
            if vals['user_id']:
                t_user_data = self.env['res.users'].browse(vals['user_id'])
                if t_user_data.partner_id:
                    vals['officer_id'] = t_user_data.partner_id.id

        if data.parent_id:
            if 'department_id' in vals and vals['department_id']:
                parent_department_id = data.parent_id.department_id and data.parent_id.department_id.id or None
                if vals['department_id'] != parent_department_id:
                    raise except_orm(_('Attenzione'),
                                     _("Il dipartimento selezionato differisce da quello della pratica padre!"))

        if 'department_id' in vals:
            t_dep_data = self.env['hr.department'].browse(vals['department_id'])
            vals['enable_tab_sectors'] = t_dep_data.enable_tab_sectors
            vals['enable_tab_tests'] = t_dep_data.enable_tab_tests

        res = super(ProjectProject, self).write(vals)

        accreq_obj = self.pool['accreditation.request']
        for data in self:
            if 'request_id' in vals and vals['request_id']:
                req_id = vals['request_id']

                accreq_obj.write(self._cr, self._uid, req_id, {'state': 'A',
                                                               'project_id': data.id, })

            if 'standard_id' in vals and vals['standard_id']:
                req_id = data.request_id and data.request_id.id or None
                if 'request_id' in vals and vals['request_id']:
                    req_id = vals['request_id']
                if req_id:
                    accreq_data = self.env['accreditation.request'].browse(req_id)
                    if not accreq_data.standard_id:
                        accreq_obj.write(self._cr, self._uid, req_id, {'standard_id': vals['standard_id'], })

            t_person_events_list = []
            for t_person_events_data in data.person_events_ids:
                if t_person_events_data.partner_id and t_person_events_data.partner_id.id in t_person_events_list:
                    raise except_orm(_('Attenzione'),
                                     _("La persona fisica può essere presente una sola volta nell'elenco dei partecipanti!"))
                t_person_events_list.append(t_person_events_data.partner_id.id)

        return res

    def _get_domain(self):
        t_flag_first = False
        t_domain = []

        roles_dict = {'is_technical_officer': False,
                      'is_supervisor': False,
                      'is_inspector': False,
                      'is_inspector_system': False,
                      'is_relator': False,
                      'is_correlator': False,
                      'is_evaluator': False,
                      'is_direction_repr': False,
                      'is_observer': False,
                      'is_technical_expert': False,
                      'is_resp_group_inspection': False,
                      'is_assistant_inspection': False,
                      'is_department_director': False,
                      'is_secretary_management': False,
                      'is_candidate': False,
                      }

        if self.accreditation_project_type:
            for role_data in self.accreditation_project_type.roles_ids:
                if role_data.technical_officer:
                    roles_dict.update({'is_technical_officer': True, })
                if role_data.supervisor:
                    roles_dict.update({'is_supervisor': True, })
                if role_data.inspector:
                    roles_dict.update({'is_inspector': True, })
                if role_data.inspector_system:
                    roles_dict.update({'is_inspector_system': True, })
                if role_data.relator:
                    roles_dict.update({'is_relator': True, })
                if role_data.correlator:
                    roles_dict.update({'is_correlator': True, })
                if role_data.evaluator:
                    roles_dict.update({'is_evaluator': True, })
                if role_data.direction_repr:
                    roles_dict.update({'is_direction_repr': True, })
                if role_data.observer:
                    roles_dict.update({'is_observer': True, })
                if role_data.technical_expert:
                    roles_dict.update({'is_technical_expert': True, })
                if role_data.resp_group_inspection:
                    roles_dict.update({'is_resp_group_inspection': True, })
                if role_data.assistant_inspection:
                    roles_dict.update({'is_assistant_inspection': True, })
                if role_data.department_director:
                    roles_dict.update({'is_department_director': True, })
                if role_data.secretary_management:
                    roles_dict.update({'is_secretary_management': True, })
                if role_data.candidate:
                    roles_dict.update({'is_candidate': True, })

        for role_item in roles_dict:
            if roles_dict[role_item]:
                t_domain.insert(0, (role_item, '=', True))
                if t_flag_first:
                    t_domain.insert(0, '|')

                if not t_flag_first:
                    t_flag_first = True

        if self.department_id:
            t_domain.insert(0, ('department_ids', '=', self.department_id.id))

        return t_domain


    @api.onchange('accreditation_project_type')
    def onchange_project_type(self):
        res = {'domain': {'user_id': [],
                          },
               }
        self.accreditation_project_type_new = False
        self.accreditation_project_type_extension = False
        self.accreditation_project_type_renew = False
        self.accreditation_project_type_committees_meeting = False
        self.accreditation_project_type_courses = False
        self.accreditation_project_type_conferences = False
        self.accreditation_project_type_meetings = False
        self.user_id = None
        self.accreditation_request_due_date = ''

        if self.accreditation_project_type:
            type_data = self.accreditation_project_type
            if type_data.is_new:
                self.accreditation_project_type_new = True
            if type_data.is_extension:
                self.accreditation_project_type_extension = True
            if type_data.is_renew:
                self.accreditation_project_type_renew = True
            if type_data.is_committees_meeting:
                self.accreditation_project_type_committees_meeting = True
            if type_data.is_courses:
                self.accreditation_project_type_courses = True
            if type_data.is_conferences:
                self.accreditation_project_type_conferences = True
            if type_data.is_meetings:
                self.accreditation_project_type_meetings = True
            if type_data.accreditation_request_days and self.accreditation_due_date:
                t_date = str(datetime.strptime(self.accreditation_due_date, DF) - relativedelta(months=4))
                self.accreditation_request_due_date = t_date

        res['domain']['user_id'] = self._get_domain()


        accreditation_project_type_obj = self.accreditation_project_type
        is_committees_meeting = accreditation_project_type_obj.is_committees_meeting
        self.get_partner_domain = is_committees_meeting

        return res


    @api.onchange('accreditation_due_date')
    def onchange_accreditation_due_date(self):
        self.accreditation_request_due_date = ''

        if self.accreditation_project_type:
            type_data = self.accreditation_project_type
            if type_data.accreditation_request_days and self.accreditation_due_date:
                t_date = str(datetime.strptime(self.accreditation_due_date, DF) - relativedelta(months=4))
                self.accreditation_request_due_date = t_date

    @api.onchange('request_id')
    def onchange_request(self):

        request_data = self.request_id
        # self.user_id = request_data.user_id
        self.unit_id = request_data.unit_id
        self.partner_id = request_data.partner_id
        self.note = request_data.note
        self.standard_id = request_data.standard_id
        self.cab_code = request_data.cab_code or None

        t_project_unit_ids = None

        t_cab_code = self.cab_code
        t_unit_acronym = request_data.unit_id and request_data.unit_id.unit_acronym or ''
        t_unit_acronym = t_unit_acronym and t_unit_acronym + ' - ' or t_unit_acronym
        if request_data.unit_acronym:
            t_unit_acronym = request_data.unit_acronym + ' - '
        t_unit_name = request_data.unit_id and request_data.unit_id.name or ''
        t_unit_name = t_unit_name and t_cab_code and ' - ' + t_unit_name or t_unit_name

        if request_data.department_id and not self.department_id:
            self.department_id = request_data.department_id

        for x in request_data.lines_ids:
            if t_project_unit_ids:
                t_project_unit_ids += x.unit_id
            else:
                t_project_unit_ids = x.unit_id

        for main_unit_data in request_data.partner_id.main_units_ids:
            if not self.unit_id:
                self.unit_id = main_unit_data
            if not t_project_unit_ids or main_unit_data not in t_project_unit_ids:
                if t_project_unit_ids:
                    t_project_unit_ids += main_unit_data
                else:
                    t_project_unit_ids = main_unit_data

        self.project_unit_ids = t_project_unit_ids

        if t_unit_acronym and t_cab_code and t_unit_name:
            self.name = t_unit_acronym + t_cab_code + t_unit_name

    @api.onchange('cab_code', 'unit_id')
    def onchange_cab_unit(self):
        if self.cab_code and self.unit_id:
            t_unit_acronym = self.unit_id.unit_acronym or ''
            t_unit_acronym = t_unit_acronym and t_unit_acronym + ' - '
            t_unit_name = self.unit_id.name or ''
            t_unit_name = t_unit_name and self.cab_code and ' - ' + t_unit_name

            if self.request_id and self.request_id.unit_acronym:
                t_unit_acronym = self.request_id.unit_acronym + ' - '

            self.name = self.unit_id.unit_code + ' - ' +  t_unit_acronym + self.cab_code

    @api.onchange('department_id')
    def onchange_department_id(self):

        domain = {'request_id':
                  [('state', '=', 'E'), ('request_type', '=', self.accreditation_project_type.id)]}
        if self.department_id:
            domain = {'request_id':
                      [('state', '=', 'E'), ('request_type', '=', self.accreditation_project_type.id), ('department_id', '=', self.department_id.id)]}

            if self.department_id and self.department_id.name == 'Dipartimento Certificazione':
                domain.update({'standard_id':
                               [('standard_scope', '=', 'ODC')]})
            elif self.department_id and self.department_id.name:
                domain.update({'standard_id':
                               [('standard_scope', '=', 'LAB')]})
            self.enable_tab_sectors = self.department_id.enable_tab_sectors
            self.enable_tab_tests = self.department_id.enable_tab_tests
        else:
            domain.update({'standard_id':
                           []})
            self.enable_tab_sectors = False
            self.enable_tab_tests = False

        if self.request_id and self.department_id:
            if self.request_id.department_id and self.request_id.department_id.id != self.department_id.id:
                self.request_id = None

        domain['user_id'] = self._get_domain()

        return {'domain': domain}

    @api.one
    def _is_last_test_draft(self):
        self.is_last_test_draft = False
        t_max_test_data = None
        for test_data in self.test_ids:
            if not t_max_test_data or (test_data.rev_number and t_max_test_data.rev_number and t_max_test_data.rev_number < test_data.rev_number):
                t_max_test_data = test_data

        if t_max_test_data and t_max_test_data.state == 'draft':
            self.is_last_test_draft = True

    @api.one
    def _enable_tab_sectors(self):
        self.enable_tab_sectors = False
        if self.department_id and self.department_id.enable_tab_sectors:
            self.enable_tab_sectors = True

    @api.one
    def _enable_tab_tests(self):
        self.enable_tab_tests = False
        if self.department_id and self.department_id.enable_tab_tests:
            self.enable_tab_tests = True

    project_sequence = fields.Char('Project Sequence', size=128, help='Sequence of the Project')
    project_number = fields.Integer('Project Number', help='Number of the Project')
    certificate_number = fields.Char('Numero Certificato', size=12,
        help='Tramite la funzione di ricerca avanzata, si possono scegliere tutte le pratiche legate allo stesso certificato di accreditamento.')
    accreditation_due_date = fields.Date('Data Scadenza Accreditamento')
    accreditation_request_due_date = fields.Date('Data scadenza invio domanda accreditamento')
    serial_number_for_entity = fields.Integer('Serial Number Entity', help='Number of the Project')
    last_accreditation_date = fields.Date('Last Accreditation Date')
    last_accreditation_expiry = fields.Date('Last Accreditation Expiry')
    accreditation_project_type = fields.Many2one('accreditation.project.type', 'Tipo Pratica')
    accreditation_project_type_new = fields.Boolean(related='accreditation_project_type.is_new', string='Hidden')
    accreditation_project_type_extension = fields.Boolean(related='accreditation_project_type.is_extension', string='Hidden')
    accreditation_project_type_renew = fields.Boolean(related='accreditation_project_type.is_renew', string='Hidden')
    accreditation_project_type_committees_meeting = fields.Boolean(related='accreditation_project_type.is_committees_meeting', string='Hidden')
    accreditation_project_type_courses = fields.Boolean(related='accreditation_project_type.is_courses', string='Hidden')
    accreditation_project_type_conferences = fields.Boolean(related='accreditation_project_type.is_conferences', string='Hidden')
    accreditation_project_type_meetings = fields.Boolean(related='accreditation_project_type.is_meetings', string='Hidden')
    committees_contact_ids = fields.One2many('accreditation.committees.contact', 'project_id', 'Contatti')
    test_ids = fields.One2many('accreditation.test', 'project_id', 'Prove')
    test_temp_ids = fields.One2many('accreditation.test.temp', 'project_id', 'Prove Temporanee')
    person_events_ids = fields.One2many('accreditation.person.events', 'project_id', 'Invitati/Partecipanti')
    person_events_temp_id = fields.Many2one('accreditation.person.events.temp', 'Wizard Invitati/Partecipanti')
    request_id = fields.Many2one('accreditation.request', 'Accreditation Request')
    project_unit_ids = fields.Many2many(comodel_name='accreditation.units',
                                        relation='project_unit',
                                        column1='project_id',
                                        column2='unit_id',
                                        string='Projects')
    team_ids = fields.One2many('accreditation.team', 'project_id', 'Team')
    standard_id = fields.Many2one('accreditation.standard', 'Norma')
    sector_ids = fields.One2many('accreditation.project.sector', 'project_id', 'Settore')
    note = fields.Text('Note')
    codice_cig = fields.Char('Codice CIG', size=64)
    cab_code = fields.Char('Progressivo Codice CAB', size=64)
    unit_id = fields.Many2one('accreditation.units', 'Unità Principale')
    is_last_test_draft = fields.Boolean(compute='_is_last_test_draft', string='Ultima Revisione Draft')
    enable_tab_sectors = fields.Boolean(compute='_enable_tab_sectors', string='Abilita Tab Settori')
    enable_tab_tests = fields.Boolean(compute='_enable_tab_tests', string='Abilita Tab Prove Accreditate')
    extension_ids_counter = fields.Char(compute='_get_extension_ids', store=False)
    accreditation_date = fields.Date('Accreditation Date')
    accreditation_expiry_date = fields.Date('Accreditation Expiry Date')
    get_partner_domain = fields.Boolean(compute='onchange_project_type', store=False, string='Domain')

    # per doclite
    officer_id = fields.Many2one('res.partner', string='Funzionario')
    rel_department_id = fields.Many2one(related='analytic_account_id.department_id',
                                        comodel_name='hr.department',
                                        readonly=True,
                                        string='Dipartimento')

    _defaults = {'privacy_visibility': 'public',
                 }

    def create_model_da02(self, cr, uid, ids, default={}, context=None):
        if context is None:
            context = {}

        for project_data in self.browse(cr, uid, ids, context):
            t_max_test_data = None
            for test_data in project_data.test_ids:
                if not t_max_test_data or (test_data.rev_number and t_max_test_data.rev_number and t_max_test_data.rev_number < test_data.rev_number):
                    t_max_test_data = test_data

            if t_max_test_data:
                t_max_test_data.create_model_da02()

        return True

    @api.multi
    def do_load_partner(self):
        for data in self:
            if data.partner_id:

                #Controllo se per quell'ente, ci sono effettivamente i componenti
                if not data.partner_id.member_ids:
                   raise Warning("L'ente " + str(data.partner_id.display_name) + " non ha componenti")

                #Devo svuotare prima tutti i componenti relativi all'ente della pratica attuale
                accreditation_committees_ids = self.env['accreditation.committees.contact'].search([('project_id','=', data.id)])
                accreditation_committees_ids.unlink()

                for t_member_data in data.partner_id.member_ids:
                    if (not t_member_data.date_start or data.date_start >= t_member_data.date_start) and (not t_member_data.date_stop or data.date_start <= t_member_data.date_stop):
                        dict_data = {'sequence': t_member_data.sequence,
                                     'register': t_member_data.register,
                                     'partner_person_id': t_member_data.partner_person_id and t_member_data.partner_person_id.id or None,
                                     'partner_entity_id': t_member_data.partner_entity_id and t_member_data.partner_entity_id.id or None,
                                     'role_id': t_member_data.role_id and t_member_data.role_id.id or None,
                                     'project_id': data.id,
                        }
                        self.env['accreditation.committees.contact'].create(dict_data)
        return True

    @api.multi
    def do_select_partner(self):

        if not self:
            return True

        person_events_temp = None
        for data in self:
            if data.person_events_temp_id:
                person_events_temp = data.person_events_temp_id.id
            break

        if not person_events_temp:
            dict_data = {'project_id': self.id, }
            person_events_temp = self.env['accreditation.person.events.temp'].create(dict_data)
            self.person_events_temp_id = person_events_temp

        result = self.env['ir.model.data'].get_object_reference('project_accredia',
                                                                'view_accreditation_person_events_temp_form')

        ctx = self._context.copy()
        ctx.update({'default_project_id': self.id,
                    })

        view_id = result and result[1] or False
        return {'name': _('Add Person Events'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'accreditation.person.events.temp',
                'type': 'ir.actions.act_window',
                'res_id': person_events_temp.id,
                'view_id': view_id,
                'context': ctx,
                'target': 'new',
                }

    @api.multi
    def do_show_extensions(self):

        if not self:
            return True

        t_project_list = []
        t_account_list = []

        for project_data in self:
            for child_data in project_data.child_ids:
                if child_data.id not in t_account_list:
                    t_account_list.append(child_data.id)

        if t_account_list:
            t_project_list = self.env['project.project'].search([('analytic_account_id', 'in', t_account_list)]).ids

        if t_project_list:
            result = self.env['ir.model.data'].get_object_reference('project_accredia',
                                                                    'view_project_accredia_form')
            view_id = result and result[1] or False

            ctx = self._context.copy()
            return {'domain': "[('id','in', ["+','.join(map(str, t_project_list))+"])]",
                    'name': _("Pratiche Collegate"),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'project.project',
                    'type': 'ir.actions.act_window',
                    'context': ctx,
                    'views': [(False, 'tree'), (view_id, 'form')],
                    }
        return True

    @api.multi
    def do_add_extension(self):

        t_department_id = None
        t_parent_id = None
        t_user_id = None
        t_partner_id = None
        t_certificate_number = None
        t_due_date = None
        for project_data in self:
            if project_data.department_id:
                t_department_id = project_data.department_id.id
            if project_data.analytic_account_id:
                t_parent_id = project_data.analytic_account_id.id
            if project_data.user_id:
                t_user_id = project_data.user_id.id
            if project_data.partner_id:
                t_partner_id = project_data.partner_id.id
            if project_data.certificate_number:
                t_certificate_number = project_data.certificate_number
            if project_data.accreditation_due_date:
                t_due_date = project_data.accreditation_due_date

        result = self.env['ir.model.data'].get_object_reference('project_accredia',
                                                                'wizard_project_create_extension_form')

        ctx = self._context.copy()
        ctx.update({'parent_id': t_parent_id,
                    't_user_id': t_user_id,
                    'partner_id': t_partner_id,
                    'certificate_number': t_certificate_number,
                    'default_department_id': t_department_id,
                    'accreditation_due_date': t_due_date,
                    })
        view_id = result and result[1] or False

        return {'name': _("Crea Pratica Collegata"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.project.create.extension',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'context': ctx,
                'target': 'new'
                }
