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

from openerp import fields, models


class AccreditationPersonRoles(models.Model):

    _name = "accreditation.person.roles"

    partner_id = fields.Many2one('res.partner', 'Persona Fisica', required=True)
    role_id = fields.Many2one('accreditation.roles', 'Role', required=True)
    is_techoff = fields.Boolean(related='role_id.technical_officer',
                                string="Technical Officer",
                                store=False)
    is_supervisor = fields.Boolean(related='role_id.supervisor',
                                   string="Supervisor",
                                   store=False)
    is_inspector = fields.Boolean(related='role_id.inspector',
                                  string="Ispettore",
                                  store=False)
    date_qualification = fields.Date('Data Qualifica')
    date_delibera_del_cda = fields.Date('Data Delibera del CDA')
