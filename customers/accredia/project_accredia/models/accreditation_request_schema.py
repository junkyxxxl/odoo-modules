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


class AccreditationRequestSchema(models.Model):

    _name = "accreditation.request.schema"
    _order = "name"

    name = fields.Char('Name', size=64, required=True)
    schema_code = fields.Char('Codice Schema', size=10)
    schema_nick = fields.Char('Sigla Schema', size=64)
    description = fields.Text('Descrizione (in italiano)')
    description_en = fields.Text('Descrizione (in inglese)')
    standard_ids = fields.Many2many(comodel_name='accreditation.standard',
                                    column1='schema_id',
                                    column2='standard_id',
                                    domain=[('standard_type', '=', 'NA')],
                                    string='Norme di Accreditamento')
    standard_extra_ids = fields.Many2many(comodel_name='accreditation.standard',
                                          column1='schema_id',
                                          column2='standard_id',
                                          domain=[('standard_type', '=', 'ANA')],
                                          string='Altre Norme di Accreditamento')
    standard_cert_ids = fields.Many2many(comodel_name='accreditation.standard',
                                         column1='schema_id',
                                         column2='standard_id',
                                         domain=[('standard_type', '=', 'NC')],
                                         string='Norme di Certificazione')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        t_list = []
        if self._context.get('default_standard_id', False):
            t_standard_id = self._context.get('default_standard_id', False)
            t_list.append(0)
            for data in self.env['accreditation.standard'].browse(t_standard_id).schema_ids:
                t_list.append(data.id)

        if t_list:
            args += [('id', 'in', t_list)]

        if name:
            args += ['|',
                     ('name', operator, name),
                     ('schema_nick', operator, name)]

        return super(AccreditationRequestSchema, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
