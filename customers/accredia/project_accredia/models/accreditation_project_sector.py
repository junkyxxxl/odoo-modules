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


class AccreditationProjectSector(models.Model):

    _name = "accreditation.project.sector"

    @api.onchange('standard_id')
    def onchange_standard(self):
        if self.standard_id:
            self.sector_id = None

    @api.onchange('schema_id')
    def onchange_schema(self):
        if self.schema_id:
            self.standard_extra_id = None
            self.standard_id = None

    project_id = fields.Many2one('project.project', 'Pratica', required=True)
    unit_id = fields.Many2one('accreditation.units', 'Unità')
    sector_id = fields.Many2one('accreditation.sector', 'Settore', required=True)
    standard_extra_id = fields.Many2one('accreditation.standard', 'Altra Norma di Accreditamento')
    standard_id = fields.Many2one('accreditation.standard', 'Norma di Certificazione', required=True)
    schema_id = fields.Many2one('accreditation.request.schema', string='Schema', required=True)
