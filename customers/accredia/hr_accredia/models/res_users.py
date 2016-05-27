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


class ResUsers(models.Model):
    _inherit = 'res.users'

    department_ids = fields.Many2many(comodel_name='hr.department',
                                      column1='department_id',
                                      column2='user_id',
                                      string='Dipartimenti')
    is_employee_pa = fields.Boolean(related='partner_id.employee_pa',
                                    string='Is Employee PA')

    @api.model
    def create(self, vals):

        vals['individual'] = True

        if 'person_name' in vals and vals['person_name'] and 'person_surname' in vals and vals['person_surname']:
            vals['name'] = vals['person_name'] + ' ' + vals['person_surname']

        return super(ResUsers, self).create(vals)
