# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Apulia Software (<info@apuliasoftware.it>)
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


from openerp import models, fields, api


class WizardPrintReportVatPerCash(models.TransientModel):

    _name = "wizard.print.report.vat_per_cash"

    period_ids = fields.Many2many('account.period')
    journal_ids = fields.Many2many('account.journal')

    @api.multi
    def print_report(self):
        wizard = self[0]
        data = {
            'journal_ids': [j.id for j in (wizard.journal_ids or [])],
            'period_ids': [p.id for p in (wizard.period_ids or [])]
            }
        report = 'vat_per_cash.registro_iva_sospensione'
        return self.env['report'].get_action(self, report, data=data)