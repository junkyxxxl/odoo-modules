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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccreditationInvoicedSchema(models.Model):
    _name = "accreditation.invoiced.schema"
    _description = "Fatturato per Schema"

    name = fields.Char('Name')
    customer_id = fields.Many2one('res.partner', domain=[('customer', '=', True)],
                                  string='Cliente di Riferimento', index=True)
    year = fields.Integer('Anno di Riferimento Fatturato',
                          default=2015)  # TODO
    invoiced_amount = fields.Float('Importo fatturato in Euro')
    schema = fields.Char('Schema')

    @api.model
    def create(self, vals):

        t_name = ''
        if 'customer_id' in vals:
            customer = self.env['res.partner'].browse(vals['customer_id'])
            t_name += customer.name
        if 'year' in vals:
            t_name += ' - ' + str(vals['year'])
        vals.update({'name': t_name, })

        return super(AccreditationInvoicedSchema, self).create(vals)

    @api.multi
    def write(self, vals):

        t_name = ''
        if 'customer_id' in vals:
            customer = self.env['res.partner'].browse(vals['customer_id'])
            t_name += customer.name
        elif self.customer_id:
            t_name += self.customer_id.name
        if 'year' in vals:
            t_name += ' - ' + str(vals['year'])
        elif self.year:
            t_name += ' - ' + str(self.year)
        vals.update({'name': t_name, })

        return super(AccreditationInvoicedSchema, self).write(vals)
