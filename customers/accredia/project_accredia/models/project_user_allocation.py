# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ISA s.r.l. (<http://www.isa.it>).
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


class ProjectUserAllocation(models.Model):
    _inherit = 'project.user.allocation'

    unit_id = fields.Many2one('accreditation.units', 'Unità')
    is_main = fields.Boolean(related='unit_id.unit_category_id.is_main', string='Unità Principale')
    filter_standard_id = fields.Many2one(related='phase_id.filter_standard_id',
                                         comodel_name='accreditation.standard',
                                         string='Filtro Norma')
    enable_filter_standard_id = fields.Boolean(related='phase_id.enable_filter_standard_id',
                                               string='Abilita Filtro Norma')

    role_id = fields.Many2one('accreditation.roles', 'Ruolo')
    auth_id = fields.Many2one('accreditation.persons.auth', string='Autorizzazione')
    is_employee_pa = fields.Boolean(related='user_id.is_employee_pa',
                                    string="Is Employee PA",
                                    store=False)
    task_audit_type_id = fields.Many2one('accreditation.task.work.type', 'Tipo Attività')


    _defaults = {
                'user_id': None,
                 }


    @api.onchange('user_id')
    def onchange_user_id(self):
        self.is_employee_pa = False
        if self.user_id:
            self.is_employee_pa = self.user_id.is_employee_pa

    @api.model
    def create(self, vals):

        if 'user_id' in vals and vals['user_id']:
            user_data = self.env['res.users'].browse(vals['user_id'])

            if 'role_id' in vals and vals['role_id']:
                t_role_list = []
                for person_role_data in user_data.partner_id.roles_ids:
                    if person_role_data.role_id:
                        t_role_list.append(person_role_data.role_id.id)
                if vals['role_id'] not in t_role_list:
                    role_data = self.env['accreditation.roles'].browse(vals['role_id'])
                    raise except_orm(_('Errore'),
                                     _("Il ruolo %s non è compatibile con l'ispettore %s!") % (role_data.description, user_data.name))

            if 'unit_id' in vals and vals['unit_id']:
                t_person_list = []
                unit_data = self.env['accreditation.units'].browse(vals['unit_id'])
                for person_data in unit_data.location_id.partner_id.persons_ids:
                    if person_data.partner_id:
                        t_person_list.append(person_data.partner_id.id)
                if user_data.partner_id.id in t_person_list:
                    raise except_orm(_('Errore'),
                                     _("L'unità %s non è compatibile con l'ispettore %s!") % (unit_data.name, user_data.name))

            if 'date_start' in vals and vals['date_start'] and 'date_end' in vals and vals['date_end']:

                t_date_start = vals['date_start']
                t_date_end = vals['date_end']

                meeting_ids = self.env['calendar.event'].search([('partner_ids', '=', user_data.partner_id.id),
                                                                 ('show_as', '=', 'busy'),
                                                                 '&', ('start_date', '<=', t_date_end + " 23:59:59"),
                                                                      ('start_date', '>=', t_date_start + " 00:00:00"),
                                                                 ],
                                                                limit=1)

                if meeting_ids:
                    raise except_orm(_('Error'),
                                     _("L'ispettore %s è già impegnato nella data specificata!") % (user_data.name))

                # TODO migliorare il filtro considerando la durata del meeting

        return super(ProjectUserAllocation, self).create(vals)

    @api.multi
    def write(self, vals):

        for data in self:
            t_role_id = data.role_id and data.role_id.id or None
            t_user_id = data.user_id and data.user_id.id or None
            t_unit_id = data.unit_id and data.unit_id.id or None
            if 'role_id' in vals:
                t_role_id = vals['role_id']
            if 'user_id' in vals:
                t_user_id = vals['user_id']
            if 'unit_id' in vals:
                t_unit_id = vals['unit_id']

            if t_role_id and t_user_id:
                t_role_list = []
                user_data = self.env['res.users'].browse(t_user_id)
                for person_role_data in user_data.partner_id.roles_ids:
                    if person_role_data.role_id:
                        t_role_list.append(person_role_data.role_id.id)
                if t_role_id not in t_role_list:
                    role_data = self.env['accreditation.roles'].browse(t_role_id)
                    raise except_orm(_('Errore'),
                                     _("Il ruolo %s non è compatibile con l'ispettore %s!") % (role_data.description, user_data.name))

            if t_unit_id and t_user_id:
                t_person_list = []
                unit_data = self.env['accreditation.units'].browse(t_unit_id)
                for person_data in unit_data.location_id.partner_id.persons_ids:
                    if person_data.partner_id:
                        t_person_list.append(person_data.partner_id.id)
                user_data = self.env['res.users'].browse(t_user_id)
                if user_data.partner_id.id in t_person_list:
                    raise except_orm(_('Errore'),
                                     _("L'unità %s non è compatibile con l'ispettore %s!") % (unit_data.name, user_data.name))

        return super(ProjectUserAllocation, self).write(vals)
