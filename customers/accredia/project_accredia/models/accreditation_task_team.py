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


class AccreditationTaskTeam(models.Model):

    _name = "accreditation.task.team"

    task_id = fields.Many2one('project.task', 'Task', required=True)
    user_id = fields.Many2one('res.users', 'Ispettore', required=True)
    partner_id = fields.Many2one(related='user_id.partner_id',
                                 comodel_name='res.partner',
                                 string='Persona Fisica',
                                 store=True,
                                 readonly=True)
    role_id = fields.Many2one('accreditation.roles', 'Role', required=True)

    task_leader = fields.Boolean('Responsible')
    doc_review_days = fields.Float('Giornate Esame Documentale')
    inspection_days = fields.Float('Giornate Visite Ispettive')
    is_employee = fields.Boolean('Is Employee')

    @api.onchange('user_id')
    def onchange_team_person_id(self):
        self.is_employee = False
        if self.user_id:
            employee_data = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
            if employee_data:
                self.is_employee = True

    @api.model
    def create(self, vals):
        if 'user_id' in vals and vals['user_id']:
            employee_data = self.env['hr.employee'].search([('user_id', '=', vals['user_id'])], limit=1)
            if employee_data:
                vals['is_employee'] = True
        return super(AccreditationTaskTeam, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'user_id' in vals and vals['user_id']:
            vals['is_employee'] = False
            employee_data = self.env['hr.employee'].search([('user_id', '=', vals['user_id'])], limit=1)
            if employee_data:
                vals['is_employee'] = True
        return super(AccreditationTaskTeam, self).write(vals)
