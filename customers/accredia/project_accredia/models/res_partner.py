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


class ResPartner(models.Model):

    _inherit = "res.partner"

    skill_ids = fields.Many2many(comodel_name='accreditation.skills',
                                 relation='accreditation_persons_skills_rel',
                                 column1='partner_id',
                                 column2='skill_id',
                                 string='Skill')
    # ogni persona che sia dipendente PA puo avere autorizzazioni
    auth_ids = fields.One2many('accreditation.persons.auth',
                               'partner_id',
                               string='Autorizzazioni')

    person_events_ids = fields.Many2many('accreditation.person.events.temp',
                                         column1='partner_id',
                                         column2='person_events_id',
                                         string='Eventi')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        t_list = []
        if self._context.get('default_task_id', False):
            t_task_id = self._context.get('default_task_id', False)
            t_task_data = self.env['project.task'].browse(t_task_id)
            if t_task_data.fnct_responsible:
                t_list.append(t_task_data.fnct_responsible.id)
            if t_task_data.project_id and t_task_data.project_id.user_id:
                t_list.append(t_task_data.project_id.user_id.partner_id.id)
            for data in t_task_data.task_team_ids:
                if data.user_id:
                    t_list.append(data.user_id.partner_id.id)
            if t_list:
                args = args + [['id', 'in', t_list]]

        t_list = []
        if self._context.get('default_project_id', False):
            t_project_id = self._context.get('default_project_id', False)
            t_project_data = self.env['project.project'].browse(t_project_id)
            if t_project_data.partner_id:
                for function_data in t_project_data.partner_id.persons_ids:
                    if function_data.partner_id:
                        t_list.append(function_data.partner_id.id)

            if t_list:
                args = args + [['id', 'not in', t_list]]

        ctx = dict(self._context or {})

        if self._context.get('view_person', False):
            # se è persona fisica allora cercare anche quelli con active = false
            ctx.update({'active_test': False, })

        return super(ResPartner, self.with_context(ctx)).name_search(
            name=name, args=args, operator=operator, limit=limit)
