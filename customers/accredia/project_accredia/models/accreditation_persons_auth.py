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
from datetime import datetime


class AccreditationPersonsAuth(models.Model):
    _description = 'Autorizzazioni Dipendenti P.A.'
    _name = 'accreditation.persons.auth'
    _rec_name = 'auth_code'

    @api.one
    def _get_days_remaining(self):
        self.days_remaining = max(self.days - self.days_used, 0.0)

    partner_id = fields.Many2one('res.partner', 'Dipendente P.A.', domain=[('employee_pa', '=', True)])
    task_ids = fields.Many2many(comodel_name='project.task',
                                relation="accreditation_persons_auth_task_rel",
                                column1='auth_id',
                                column2='task_id',
                                string='Attività')
    date_start = fields.Date('Data Inizio', required=True)
    date_stop = fields.Date('Data Fine', required=True)
    auth_code = fields.Char('Codice Autorizzazione', size=64, required=True)
    auth_type = fields.Selection([('S', 'Per Singolo Incarico'),
                                  ('D', 'A Giorni')],
                                 'Tipo Autorizzazione')
    days = fields.Float('Numero di Giorni')
    days_used = fields.Float(compute='_get_days_used', string='Giorni Utilizzati', store=True)
    days_remaining = fields.Float(compute='_get_days_remaining', string='Giorni Rimanenti')


    @api.multi
    @api.depends('task_ids')
    def _get_days_used(self):
        for record in self:
            user_obj = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
            days_used = 0
            if record.auth_type == 'D':
                phases = record.mapped('task_ids').mapped('phase_id')
                for phase in phases:
                    if phase.state == 'done' or phase.state == 'confirmed':
                        # Dalla fase vado a cercare gli item che fanno riferimento al dipendende PA
                        for item in phase.user_ids:
                            if (item.user_id.id == user_obj.id) and (item.task_audit_type_id.days_dipendent_authorization):
                                days_used = days_used + item.num_days
                    record.days_used = days_used
            else:
                record.days_used = 0


    @api.multi
    @api.depends('date_start', 'date_stop', 'auth_code', 'auth_type')
    def name_get(self):
        res = []
        for ap in self:
            descr = ("%s") % (ap.auth_code)
            if ap.date_start:
                descr += (" dal %s") % (ap.date_start)
            if ap.date_stop:
                descr += (" al %s") % (ap.date_stop)
            if ap.auth_type:
                if ap.auth_type == 'S':
                    descr += " (Per Singolo Incarico)"
                if ap.auth_type == 'D':
                    descr += " (A Giorni)"
            res.append((ap.id, descr))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        t_user_id = self._context.get('default_user_id', False)
        if t_user_id:
            user_data = self.env['res.users'].browse(t_user_id)
            t_partner_id = user_data.partner_id.id

            args += [('partner_id', '=', t_partner_id)]

        if name:
            args += [('auth_code', operator, name)]

        return super(AccreditationPersonsAuth, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
