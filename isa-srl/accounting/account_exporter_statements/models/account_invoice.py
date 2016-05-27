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
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    exporter_id = fields.Many2one('account.exporter.statements', 'Exporter Statements')

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):

        result = super(AccountInvoice,self).onchange_partner_id(type, partner_id,
                                                                 date_invoice=date_invoice,
                                                                 payment_term=payment_term,
                                                                 partner_bank_id=partner_bank_id,
                                                                 company_id=company_id)

        if 'value' in result:
            ext_obj = self.env['account.exporter.statements']
            exps = ext_obj.search([('partner_id', '=', partner_id),
                                   ('letter_status', '=', 'A')],
                                  limit=1)
            if exps:
                result['value']['exporter_id'] = exps.id

        return result

    @api.multi
    def onchange_exporter_id(self, exporter_id, doc_date, line_ids):
        res = {}
        if exporter_id:
            exp_data = self.env['account.exporter.statements'].browse(exporter_id)
            if exp_data.letter_status == 'A':
                if exp_data.letter_type != 'P':
                    tax_id = [exp_data.vat_code_id.id]
                elif doc_date > exp_data.period_start and doc_date < exp_data.period_end:
                    tax_id = [exp_data.vat_code_id.id]
            new_lines = [] 
            for line in line_ids:
                if isinstance(line, tuple):
                    if line[0] == 0:
                        temp = line[2]
                        temp.update({'invoice_line_tax_id': [(6, 0, tax_id)]})
                        new_lines.append((0,0,temp))
                    elif line[0] == 6:
                        new_lines.append(line)
                        for id in line[2]:
                            self.pool.get('account.invoice.line').write(self._cr,self._uid,id,{'invoice_line_tax_id':[(6,0,tax_id)]})
                elif isinstance(line, dict):
                    None

            comment = 'Lettera d\'intento n. ' + exp_data.letter_number + ' - Del ' + datetime.strptime(exp_data.letter_date,"%Y-%m-%d").strftime('%d/%m/%Y')
            return {'value':{'invoice_line':new_lines, 'comment':comment}}
        return {}
