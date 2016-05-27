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


class HrHolidayLine(models.Model):
    _name = 'hr.holidays.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.info = None
        if self.partner_id and self.product_id:
            for data in self.partner_id.info_product_ids:
                if data.product_id and data.product_id.id == self.product_id.id:
                    self.info = data.info
                    break

    product_id = fields.Many2one('product.product', 'Prodotto')
    partner_id = fields.Many2one('res.partner', 'Persona Fisica')
    name = fields.Char('Descrizione', size=128, required=True)
    info = fields.Char('Info Aggiuntive')
    date_from = fields.Datetime('Da Data/Ora')
    date_to = fields.Datetime('A Data/Ora')
    holidays_id = fields.Many2one('hr.holidays', 'Holidays', ondelete='cascade', select=True)
    place = fields.Char('Luogo')
