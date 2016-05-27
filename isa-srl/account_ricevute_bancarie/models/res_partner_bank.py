# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

    @api.depends('acc_number')
    def _get_iban(self):
        for data in self:
            data.iban = ''
            if data.acc_number:
                data.iban = data.acc_number.replace(' ', '')

    codice_sia = fields.Char(string='Codice SIA', size=5, help="Identification Code of the Company in the System Interbank")
    # iban field is Deprecated in v7
    # We use acc_number instead of IBAN since v6.1, but we keep this field
    # to not break community modules.
    iban = fields.Char(compute='_get_iban',
                       string='IBAN',
                       store=False,
                       help="International Bank Account Number")
