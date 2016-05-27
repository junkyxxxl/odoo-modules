# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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


class AccreditationSector(models.Model):

    _name = "accreditation.sector"
    _order = "name"

    name = fields.Char('Name', size=64, required=True)
    description = fields.Text('Descrizione (in italiano)')
    description_en = fields.Text('Descrizione (in inglese)')
    sector_code = fields.Char('Codice Settore', size=10)
    standard_ids = fields.Many2many(comodel_name='accreditation.standard',
                                    column1='sector_id',
                                    column2='standard_id',
                                    domain=[('standard_type', '=', 'NC')],
                                    string='Norme')
    project_ids = fields.One2many('accreditation.project.sector',
                                  'sector_id',
                                  'Pratica')
    category_id = fields.Many2one('accreditation.sector.category', 'Categoria')

    @api.multi
    @api.depends('name', 'sector_code')
    def name_get(self):
        res = []
        for ap in self:
            descr = ("[%s] %s") % (ap.sector_code, ap.name)
            res.append((ap.id, descr))
        return res
