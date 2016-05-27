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

from openerp import fields,models, api


class ResUsers(models.Model):
    _inherit = 'res.users'


    edit_number_certificate = fields.Boolean(string="Modifica numero di certificato", store=True)

    #Creo la funzione per rimuovere i duplicati da una lista
    def remove_duplicates(self,values):
        output = []
        seen = set()
        for value in values:
            if value not in seen:
                output.append(value)
                seen.add(value)
        return output


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        partner_list = []

        # filtra per norme
        if self._context.get('filter_standard_id', False) and self._context.get('enable_filter_standard_id', False):
            standard_id = self._context.get('filter_standard_id', False)
            partner_list = []
            skill_ids = self.env['accreditation.skills'].search([('standard_id', '=', standard_id)])
            for skill_data in skill_ids:
                for partner_data in skill_data.partner_ids:
                    if partner_data.id not in partner_list:
                        partner_list.append(partner_data.id)

        # esclude gli incompatibili
        if self._context.get('t_unit_id', False):
            t_unit_id = self._context.get('t_unit_id', False)
            unit_data = self.env['accreditation.units'].browse(t_unit_id)
            person_list_data = unit_data.location_id and unit_data.location_id.partner_id and unit_data.location_id.partner_id.persons_ids or None
            if person_list_data:
                for person_data in person_list_data:
                    if person_data.partner_id:
                        partner_list.append(person_data.partner_id.id)


        # esclude i non disponibili
        if 'include_not_available' in self._context and not self._context.get('include_not_available', False):

            t_date_start = self._context.get('t_date_start', False)
            if not t_date_start:
                t_date_start = self._context.get('parent_date_start', False)
            t_date_end = self._context.get('t_date_end', False)
            if not t_date_end:
                t_date_end = self._context.get('parent_date_end', False)

            if t_date_start and t_date_end:

                t_query = '''
                    select
                        distinct(res_users.id)
                    from
                        res_partner
                        join res_users
                             on res_users.partner_id = res_partner.id
                        join calendar_event_res_partner_rel
                             on calendar_event_res_partner_rel.res_partner_id = res_partner.id
                        join calendar_event
                             on calendar_event_res_partner_rel.calendar_event_id = calendar_event.id
                    where
                        calendar_event.show_as like 'busy'
                      and
                        (
                         (calendar_event.start_date <= '%s' and calendar_event.start_date >= '%s')
                         or
                         (calendar_event.stop_date >= '%s' and calendar_event.stop_date <= '%s')
                         )

                    ''' % (t_date_end, t_date_start, t_date_start, t_date_end)
                self._cr.execute(t_query)
                user_ids = self._cr.fetchall()
                if user_ids:
                    args = args + [['id', 'not in', user_ids]]

        # filtra per team della pratica in pianificazione attività di audit
        if 't_project_id' in self._context and self._context.get('t_project_id', False):

            t_project_id = self._context.get('t_project_id', False)
            project_data = self.env['project.project'].browse(t_project_id)
            for team_data in project_data.team_ids:
                if team_data.user_id and team_data.user_id.id not in partner_list:
                    partner_list.append(team_data.user_id.partner_id.id)

        #partner_list = self.remove_duplicates(partner_list)
        if partner_list:
            args = args + [['partner_id', 'in', partner_list]]
        return super(ResUsers, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
