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

from openerp import fields, models, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class AccreditationRequest(models.Model):

    _name = "accreditation.request"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _track = {
        'state': {
            'project_accredia.acc_request_new': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['G', 'E'],
        },
    }

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id and self.state == 'G':
            self.state = 'E'

    @api.one
    def action_E(self):
        self.state = 'E'

    @api.one
    def action_R(self):
        self.state = 'R'


    @api.onchange('department_id')
    def onchange_department_id(self):
        res = {}
        res.setdefault('domain', {})

        standard_domain = [('standard_type', '=', 'NA')]
        res['domain']['standard_id'] = repr(standard_domain)

        if self.department_id:

            if self.department_id.department_nick == 'DC' or self.department_id.name == 'Dipartimento Certificazione':
                res['domain']['standard_id'] = repr([('standard_scope', '=', 'ODC'),
                                                     ('standard_type', '=', 'NA')
                                                     ])
                res['domain']['user_id'] = repr([('department_ids', '=', self.department_id.id),
                                                 ('is_technical_officer', '=', True),
                                                 ])
            elif self.department_id.name:
                res['domain']['standard_id'] = repr([('standard_scope', '=', 'LAB'),
                                                     ('standard_type', '=', 'NA')
                                                     ])
                res['domain']['user_id'] = repr([('department_ids', '=', self.department_id.id),
                                                 ('is_technical_officer', '=', True),
                                                 ])
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.unit_id = None
        if self.partner_id:
            for main_unit_data in self.partner_id.main_units_ids:
                self.unit_id = main_unit_data
                break

    @api.model
    def _default_department_id(self):
        t_user_data = self.env['res.users'].browse(self._uid)
        if len(t_user_data.department_ids) == 1:
            return t_user_data.department_ids
        return None


    @api.multi
    @api.depends('request_type', 'partner_id', 'cab_code')
    def _compute_name(self):
      for record in self:
        if record.cab_code:
            record.name = '%s - %s - %s' % (record.request_type.name, record.partner_id.name, record.cab_code)
        else:
            record.name = '%s - %s' % (record.request_type.name, record.partner_id.name)

    name = fields.Char('Descrizione', required=True, compute='_compute_name', store=True)
    request_type = fields.Many2one('accreditation.project.type',
                                   domain=['|',
                                           ('is_new', '=', True),
                                           '|',
                                           ('is_extension', '=', True),
                                           ('is_renew', '=', True),
                                           ],
                                   string='Request Type')

    partner_id = fields.Many2one('res.partner', 'Openerp Partner', required=True)
    first_time = fields.Boolean('First Time')
    department_id = fields.Many2one('hr.department', 'Department', default=_default_department_id)

    state = fields.Selection([('G', 'Ricevuta'),
                              ('E', 'In exam'),
                              ('A', 'Accepted'),
                              ('R', 'Rejected'),
                              ],
                             default='G',
                             string="State")
    project_id = fields.Many2one('project.project', 'Project')

    date = fields.Date('Data della domanda')
    date_received = fields.Date('Received Date', default=fields.Date.context_today)
    date_approved = fields.Date('Approved Date')
    date_denial = fields.Date('Denial Date')
    lines_ids = fields.One2many('accreditation.request.lines', 'request_id', 'Accreditations Request lines')

    standard_id = fields.Many2one('accreditation.standard', 'Norma di accreditamento',
                                  domain=[('standard_type', '=', 'NA')])
    user_id = fields.Many2one('res.users', 'Funzionario Tecnico')

    note = fields.Text('Note')

    cab_code = fields.Char('Progressivo Codice CAB', size=64)
    unit_id = fields.Many2one('accreditation.units', 'Unità Principale')
    task_id = fields.Many2one('project.task', 'Rif. Attività Collegata')

    # Acronimo Unità
    unit_acronym = fields.Char('Acronimo Unità', size=50)

    @api.model
    def create(self, vals):

        t_error = _('Error')
        t_message_denial = _('La Data Riufiuto è obbligatoria quando la domanda viene posta nello stato Rifiutata!')

        if 'state' in vals and vals['state']:
            t_state = vals['state']
            if t_state == 'A':
                raise except_orm(_('Error'),
                                 _('Non puoi creare una richiesta già Accettata!'))

            if t_state == 'R':
                # date_denial obbligatorio
                if 'date_denial' in vals and not vals['date_denial']:
                    raise except_orm(t_error, t_message_denial)

        if 'user_id' in vals and vals['user_id']:
            user_data = self.env['res.users'].browse(vals['user_id'])
            t_partner_id = user_data.partner_id.id
            vals['message_follower_ids'] = [(4, t_partner_id)]

        return super(AccreditationRequest, self).create(vals)

    @api.multi
    def write(self, vals):
        t_error = _('Error')
        t_message_approved = _('La Data Approvazione è obbligatoria quando la domanda viene posta nello stato Accettata!')
        t_message_denial = _('La Data Riufiuto è obbligatoria quando la domanda viene posta nello stato Rifiutata!')

        for request in self:
            if request.project_id:
                raise except_orm(_('Error'),
                                 _('Non puoi modificare la richiesta perchè la Pratica è già stata creata!'))
            if 'state' in vals and vals['state']:
                t_state = vals['state']
                if t_state == 'A':
                    # date_approved obbligatorio
                    if 'date_approved' in vals and not vals['date_approved']:
                        raise except_orm(t_error, t_message_approved)
                    elif 'date_approved' not in vals:
                        t_date_approved = request.date_approved
                        if not t_date_approved:
                            vals['date_approved'] = fields.Date.context_today(self)

                if t_state == 'R':
                    # date_denial obbligatorio
                    if 'date_denial' in vals and not vals['date_denial']:
                        raise except_orm(t_error, t_message_denial)
                    elif 'date_denial' not in vals:
                        t_date_denial = request.date_denial
                        if not t_date_denial:
                            raise except_orm(t_error, t_message_denial)
            if 'state' not in vals:
                if 'date_approved' in vals and not vals['date_approved']:
                        t_state = request.state
                        if t_state == 'A':
                            raise except_orm(t_error, t_message_approved)
                if 'date_denial' in vals and not vals['date_denial']:
                        t_state = request.state
                        if t_state == 'R':
                            raise except_orm(t_error, t_message_approved)

            if 'user_id' in vals and vals['user_id']:
                user_data = self.env['res.users'].browse(vals['user_id'])
                t_partner_id = user_data.partner_id.id
                vals['message_follower_ids'] = [(4, t_partner_id)]

        return super(AccreditationRequest, self).write(vals)

    @api.multi
    @api.depends('request_type.name', 'partner_id.name', 'date_approved')
    def name_get(self):
        res = []
        for ar in self:
            descr = ar.request_type.name and ar.request_type.name + ' - ' or ''
            descr += ar.partner_id.name or ''
            descr += ar.date_approved and (' (' + ar.date_approved + ')') or ''
            res.append((ar.id, descr))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        req_ids = self.search(args +
                              ['|',
                               ('partner_id.name', operator, name),
                               ('request_type.name', operator, name)],
                              limit=limit)
        return req_ids.name_get()
