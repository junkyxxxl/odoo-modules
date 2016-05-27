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


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi 
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        exporter_id = self._context.get('exporter_id', None)
        doc_date = self._context.get('registration_date', None)

        res = super(AccountInvoiceLine, self).product_id_change(product, uom_id, qty, name, type, partner_id, fposition_id, price_unit, currency_id, company_id=company_id)
        if exporter_id:
            exp_data = self.env['account.exporter.statements'].browse(exporter_id)
            if exp_data.letter_status == 'A':
                if exp_data.letter_type != 'P':
                    res['value'].update({'invoice_line_tax_id': [exp_data.vat_code_id.id]})
                elif doc_date > exp_data.period_start and doc_date < exp_data.period_end:
                    res['value'].update({'invoice_line_tax_id': [exp_data.vat_code_id.id]})
        return res
