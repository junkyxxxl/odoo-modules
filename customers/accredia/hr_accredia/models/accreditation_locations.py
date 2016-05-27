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


class AccreditationLocations(models.Model):

    _name = "accreditation.locations"
    _description = "Sedi"

    partner_id = fields.Many2one('res.partner', domain=[('is_entity', '=', True)], string='Ente')
    name = fields.Char('Nome Sede', size=128)
    address = fields.Text('Address')
    zip = fields.Char('Zip', size=10)
    city = fields.Char('City', size=120)
    province = fields.Many2one('res.province', string='Province')
    region = fields.Many2one('res.region', string='Region')
    country_id = fields.Many2one('res.country', 'Nation')
    phone = fields.Char('Phone', size=50)
    phone2 = fields.Char('2nd Phone', size=50)
    email = fields.Char('Email', size=120)
    fax = fields.Char('Fax', size=50)
    units_ids = fields.One2many('accreditation.units', 'location_id', 'Units')
    active = fields.Boolean('Active', default=True)

    @api.multi
    @api.depends('name', 'address', 'city')
    def name_get(self):
        res = []
        for record in self:
            descr = (record.name or '') + ' - ' + (record.address or '') + '(' + (record.city or '') + ')'
            res.append((record.id, descr))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        args = args + ['|', '|',
                       ('name', operator, name),
                       ('address', operator, name),
                       ('city', operator, name)]

        return super(AccreditationLocations, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
