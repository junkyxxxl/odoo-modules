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

from openerp import fields, models


class AccreditationStandard(models.Model):

    _name = "accreditation.standard"

    name = fields.Char('Name', size=64, required=True)
    description = fields.Text('Description')
    schema_ids = fields.Many2many(comodel_name='accreditation.request.schema',
                                  column1='standard_id',
                                  column2='schema_id',
                                  string='Schemi')
    sector_ids = fields.Many2many(comodel_name='accreditation.sector',
                                  column1='standard_id',
                                  column2='sector_id',
                                  string='Settori')
    standard_scope = fields.Selection([('ODC', 'Organismi di Certificazione'),
                                       ('LAB', 'Laboratori')],
                                      'Campo di applicazione',
                                      help='''
Valori possibili : ODC (Organismi di Certificazione) e LAB (laboratori).
I record ODC sono selezionabili solo per le pratiche del dipartimento DC
e non sono selezionabili nel catalogo delle prove.''')
    standard_type = fields.Selection([('NA', 'Norma di Accreditamento'),
                                      ('ANA', 'Altra Norma di Accreditamento'),
                                      ('NC', 'Norma di Certificazione')],
                                     'Tipo')
    is_voluntary_scheme = fields.Boolean('Regime Volontario')
