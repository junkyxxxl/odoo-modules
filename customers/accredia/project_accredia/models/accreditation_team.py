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


class AccreditationTeam(models.Model):

    _name = "accreditation.team"

    project_id = fields.Many2one('project.project', 'Project', required=True)
    user_id = fields.Many2one('res.users', 'Ispettore', domain=[('partner_id.has_role', '=', True)], required=True)
    partner_id = fields.Many2one(related='user_id.partner_id',
                                 comodel_name='res.partner',
                                 string='Persona Fisica',
                                 store=True,
                                 readonly=True)
    role_id = fields.Many2one('accreditation.roles', 'Role', required=True)
    is_employee = fields.Boolean('Is Employee')

    @api.model
    def create(self, vals):
        if 'user_id' in vals and vals['user_id']:
            employees = self.env['hr.employee'].search([('user_id', '=', vals['user_id'])])
            if employees:
                vals['is_employee'] = True
        return super(AccreditationTeam, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'user_id' in vals and vals['user_id']:
            vals['is_employee'] = False
            employees = self.env['hr.employee'].search([('user_id', '=', vals['user_id'])])
            if employees:
                vals['is_employee'] = True
        return super(AccreditationTeam, self).write(vals)

    @api.onchange('user_id')
    def onchange_team_user_id(self):
        self.is_employee = False
        if self.user_id:
            employees = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)])
            if employees:
                self.is_employee = True
