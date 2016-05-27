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


class AccountCeeNatOfTrans(models.Model):

    _name = "account.cee.nat.of.trans"
    _rec_name = 'description'

    code_number = fields.Integer('Code Number', required=True)
    code_alpha = fields.Char('Code Alpha', size=1, required=True)
    description = fields.Text('Description', required=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            item_desc = (str(record.code_number) or '') + ' - ' + (record.description or '')
            res.append((record.id, item_desc))
        return res
