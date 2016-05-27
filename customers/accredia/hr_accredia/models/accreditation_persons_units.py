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
from openerp.tools.translate import _


class AccreditationPersonsUnits(models.Model):

    _name = "accreditation.persons.units"
    _description = "Persons Units"

    partner_id = fields.Many2one('res.partner', 'Persona Fisica', required=True)
    unit_id = fields.Many2one('accreditation.units', 'Unit')
    type_id = fields.Many2one('accreditation.persons.units.type', 'Referent Type', required=True)
    job_ids = fields.Many2many('accreditation.jobs',
                               column1='person_unit_id',
                               column2='job_id',
                               string='Job')
    address = fields.Text(related='unit_id.location_id.address',
                          readonly=True,
                          string='Indirizzo')
    zip = fields.Char(related='unit_id.location_id.zip',
                      readonly=True,
                      string='CAP')
    city = fields.Char(related='unit_id.location_id.city',
                       readonly=True,
                       store=True,
                       string='Città')
    province = fields.Many2one(related='unit_id.location_id.province',
                               readonly=True,
                               store=True,
                               comodel_name='res.province',
                               string='Provincia')
    country_id = fields.Many2one(related='unit_id.location_id.country_id',
                                 readonly=True,
                                 store=True,
                                 comodel_name='res.country',
                                 string='Nazione')
    # periodo
    period_date_from = fields.Date('From Date')
    period_date_to = fields.Date('To Date')

    email = fields.Char('E-Mail', size=240)
    phone = fields.Char('Phone', size=64)
    fax = fields.Char('Fax', size=64)
    mobile = fields.Char('Mobile', size=64)
    to_followup = fields.Boolean('Riferimento Solleciti')

    @api.one
    @api.constrains('period_date_from', 'period_date_to')
    def _check_period(self):
        if self.period_date_to and self.period_date_from:
            if self.period_date_to < self.period_date_from:
                raise Warning(_('Error!\nFrom date must precede end date.'))
