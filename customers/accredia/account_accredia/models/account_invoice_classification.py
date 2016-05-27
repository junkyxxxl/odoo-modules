# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api


class AccountInvoiceClassification(models.Model):
    _name = 'account.invoice.classification'
    _description = 'Account Invoice Classification'
    _rec_name = 'description'

    code = fields.Char('Code', size=20)
    description = fields.Text('Description')

    @api.multi
    @api.depends('code', 'description')
    def name_get(self):
        res = []
        for record in self:
            descr = ("[%s] %s") % (record.code, record.description)
            res.append((record.id, descr))
        return res
