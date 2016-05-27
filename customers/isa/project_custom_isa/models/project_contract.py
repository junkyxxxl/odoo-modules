# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 ISA s.r.l. (<http://www.isa.it>).
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


class project_isa_contract(models.Model):
    _description = 'Contract of Isa project'
    _name = 'project.contract'

    name = fields.Char('Description', size=255, select=True, required=True)
    contract_number = fields.Char(string='Contract Number', size=6, required=True)
    lines = fields.One2many('project.contract.line', 'contract_id')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)

    @api.multi
    @api.depends('name', 'contract_number')
    def name_get(self):
        res = []
        for record in self:
            name = record.name or ''
            contract_number = record.contract_number and (record.contract_number + ' - ') or ''
            item_desc = contract_number + name
            res.append((record.id, item_desc))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []

        recs = self.search(['|',
                            ('contract_number', operator, name),
                            ('name', operator, name)] + args,
                           limit=limit)

        return recs.name_get()
