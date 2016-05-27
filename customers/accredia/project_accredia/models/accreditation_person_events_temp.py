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


class AccreditationPersonEventsTemp(models.Model):

    _name = "accreditation.person.events.temp"

    @api.onchange('select_from_persons')
    def onchange_select_from_persons(self):
        if self.select_from_persons:
            self.select_from_entities = None

    @api.onchange('select_from_entities')
    def onchange_select_from_entities(self):
        if self.select_from_entities:
            self.select_from_persons = None

    @api.multi
    def do_load_entities(self):

        for data in self:
            t_person_event_list = []

            for person_event_data in data.project_id.person_events_ids:
                if person_event_data.partner_id and person_event_data.partner_id.id not in t_person_event_list:
                    t_person_event_list.append(person_event_data.partner_id.id)
            for partner_data in data.partner_ids:
                for main_unit_data in partner_data.main_units_ids:
                    for t_persons_unit_data in main_unit_data.persons_ids:
                        t_name = t_persons_unit_data.type_id and t_persons_unit_data.type_id.name or ''
                        if t_name == 'Collegamento Accredia':
                            t_person_id = t_persons_unit_data.partner_id and t_persons_unit_data.partner_id.id or None
                            if t_person_id and t_person_id not in t_person_event_list:
                                dict_data = {'project_id': data.project_id.id,
                                             'partner_id': t_person_id,
                                             'role_id': None,
                                             'unit_id': t_persons_unit_data.unit_id and t_persons_unit_data.unit_id.id or None,
                                             }
                                self.env['accreditation.person.events'].create(dict_data)
                                t_person_event_list.append(t_person_id)
        return True

    @api.multi
    def do_load_persons(self):

        for data in self:
            t_person_event_list = []

            for person_event_data in data.project_id.person_events_ids:
                if person_event_data.partner_id and person_event_data.partner_id.id not in t_person_event_list:
                    t_person_event_list.append(person_event_data.partner_id.id)

            t_department_id = data.department_id and data.department_id.id or None
            t_role_id = data.role_id and data.role_id.id or None

            t_query = '''
                select
                    distinct(res_partner.id)
                from
                    res_partner
                    join accreditation_person_roles
                         on accreditation_person_roles.partner_id = res_partner.id
                    '''

            if t_department_id:
                t_query += '''
                    join res_users
                         on res_users.partner_id = res_partner.id
                    join hr_department_res_users_rel
                         on hr_department_res_users_rel.user_id = res_users.id
                    '''
            if t_department_id or t_role_id:

                t_query += '''
                where
                '''
            if t_role_id:
                t_query += '''
                    accreditation_person_roles.role_id = %d
                ''' % (t_role_id)
            if t_department_id and t_role_id:
                t_query += '''
                  and
                '''
            if t_department_id:
                t_query += '''
                    hr_department_res_users_rel.department_id = %d

                ''' % (t_department_id)
            self._cr.execute(t_query)
            person_ids = self._cr.fetchall()

            for (t_person_id,) in person_ids:
                if t_person_id not in t_person_event_list:
                    dict_data = {'project_id': data.project_id.id,
                                 'partner_id': t_person_id,
                                 'role_id': None,
                                 }
                    self.env['accreditation.person.events'].create(dict_data)
                    t_person_event_list.append(t_person_id)
        return True

    project_id = fields.Many2one('project.project', 'Pratica')
    select_from_persons = fields.Boolean('Seleziona da Persone Fisiche')
    select_from_entities = fields.Boolean('Seleziona da Enti')
    role_id = fields.Many2one('accreditation.roles', 'Ruolo')
    department_id = fields.Many2one('hr.department', 'Dipartimento')
    partner_ids = fields.Many2many(comodel_name='res.partner',
                                   column1='person_events_id',
                                   column2='partner_id',
                                   domain=[('is_entity', '=', True)],
                                   string='Enti')

    @api.model
    def create(self, vals):
        # ad eccezione del campo "FATTURABILE" può essere scelto un solo ruolo.
        t_count = 0

        if 'select_from_persons' in vals and vals['select_from_persons']:
            t_count = t_count + 1

        if 'select_from_entities' in vals and vals['select_from_entities']:
            t_count = t_count + 1

        if t_count > 1:
            raise except_orm(_('Errore'),
                             _("Non è possibile impostare più di un Tipo di Selezione!"))

        return super(AccreditationPersonEventsTemp, self).create(vals)

    @api.multi
    def write(self, vals):

        for data in self:
            # ad eccezione del campo "FATTURABILE" può essere scelto un solo ruolo.

            t_count = 0

            if 'select_from_persons' in vals and vals['select_from_persons']:
                t_count = t_count + 1
            elif 'select_from_persons' not in vals:
                if data.select_from_persons:
                    t_count = t_count + 1

            if 'select_from_entities' in vals and vals['select_from_entities']:
                t_count = t_count + 1
            elif 'select_from_entities' not in vals:
                if data.select_from_entities:
                    t_count = t_count + 1

            if t_count > 1:
                raise except_orm(_('Errore'),
                                 _("Non è possibile impostare più di un tipo di selezione!"))

        return super(AccreditationPersonEventsTemp, self).write(vals)

    @api.multi
    @api.depends('project_id', 'project_id.name')
    def name_get(self):
        res = []
        for ap in self:
            t_project_name = ap.project_id and ap.project_id.name or ''
            descr = ("%s") % (t_project_name)
            res.append((ap.id, descr))
        return res
