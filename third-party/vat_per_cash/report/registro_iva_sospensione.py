# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015
#    Francesco OpenCode Apruzzese <f.apruzzese@apuliasoftware.it>
#    (<http://www.apuliasoftware.it>).
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

from openerp import api, models


class RegistroIvaSospensione(models.AbstractModel):

    _name = 'report.vat_per_cash.registro_iva_sospensione'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'vat_per_cash.registro_iva_sospensione')
        move_obj = self.env['account.move']
        invoice_obj = self.env['account.invoice']
        moves = move_obj.search([
            ('journal_id', 'in', data and data['journal_ids'] or self._ids),
            ('period_id', 'in', data and data['period_ids'] or []),
            ])
        invoice = []
        totals = {}
        for move in moves:
            if not move.ref in invoice:
                invoice.append(move.ref)
            if move.ref in totals:
                totals[move.ref] += move.amount
            else:
                totals.update({move.ref: move.amount})
        invoices = invoice_obj.search([('number', 'in', invoice)])
        docargs = {
            'doc_model': report.model,
            'company': False,
            'invoices': invoices,
            'totals': totals,
        }
        return report_obj.render(
            'vat_per_cash.registro_iva_sospensione',
            docargs)