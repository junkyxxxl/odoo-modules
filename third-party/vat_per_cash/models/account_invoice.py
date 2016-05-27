# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Giuseppe D'Alò (<g.dalo@apuliasoftware.it>)
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.one
    def _compute_amount_matured(self):
        debit = sum(line.debit for line in self.matured_line_ids)
        credit = sum(line.credit for line in self.matured_line_ids)
        self.amount_tax_matured = abs(debit - credit)
        self.amount_tax_remain = self.amount_tax - self.amount_tax_matured
    
    matured_line_ids = fields.One2many('account.move.line',
                                       'vat_x_cash_invoice_id',
                                       copy=False)
    amount_tax_matured = fields.Float(string='Tax Matured',
        digits=dp.get_precision('Account'),
        store=False, readonly=True, compute='_compute_amount_matured')
    amount_tax_remain = fields.Float(string='Tax Remain',
        digits=dp.get_precision('Account'),
        store=False, readonly=True, compute='_compute_amount_matured')

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        res = super(account_invoice, self).onchange_partner_id(
                type, partner_id, date_invoice=False,
                payment_term=False, partner_bank_id=False, company_id=False)
        if not 'value' in res or not 'fiscal_position' in res['value'] or res['value']['fiscal_position']:
            if company_id:
                company = self.env['res.company'].browse(company_id)
            else:
                company = self.env.user.company_id
            res['value']['fiscal_position'] = company.fiscal_position_id.id
        return res

