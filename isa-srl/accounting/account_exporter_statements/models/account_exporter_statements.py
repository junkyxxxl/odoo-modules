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
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class AccountExporterStatements(models.Model):
    _name = "account.exporter.statements"
    _description = "Lettera d'intento"

    letter_number = fields.Char('Letter Number', size=20)
    partner_id = fields.Many2one('res.partner', 'Partner')
    letter_date = fields.Date('Letter Date')
    letter_type = fields.Selection([('S', 'Single Operation'),
                                    ('P', 'Period'),
                                    ('T', 'Till Import')],
                                    'Letter Type')
    vat_code_id = fields.Many2one('account.tax', 'VAT Exemption Code')
    period_start = fields.Date('Period Start')
    period_end = fields.Date('Period End')
    max_amount = fields.Float('Max Amount')
    letter_status = fields.Selection([('A', 'Active'),
                                      ('E', 'Expired'),
                                      ('R', 'Revocated')],
                                     'Letter Status')
    name = fields.Char('Description', size=80)

    @api.multi
    @api.depends('letter_number')
    def name_get(self):
        res = []
        for record in self:
            item_desc = ("%s") % (record.letter_number)
            res.append((record.id, item_desc))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        args = args[:]
        records = self.search([('letter_number', operator, name)] + args,
                              limit=limit)
        return records.name_get()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            res = self.search([('partner_id', '=', self.partner_id.id),
                               ('letter_status', '=', 'A')],
                              limit=1)
            if res:
                raise except_orm(_('Error!'), _('This Partner already has an active exporter statements'))
