# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 ISA s.r.l. (<http://www.isa.it>).
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


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    default_bank = fields.Boolean('Default')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            item_desc = ("%s [ %s ]") % (record.acc_number, record.bank.name)
            res.append((record.id, item_desc))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        args = args[:]
        records = self.search(['|',
                               ('acc_number', operator, name),
                               ('bank.name', operator, name)] + args,
                              limit=limit)
        return records.name_get()
