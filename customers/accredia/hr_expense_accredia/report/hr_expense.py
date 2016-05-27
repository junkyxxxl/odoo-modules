# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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

import os
from datetime import datetime

from openerp import pooler
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class ParserReportExpense(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):

    def __init__(self, cursor, uid, name, context):
        super(ParserReportExpense, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.filter = None

        self.active_model = context.get('active_model', '')
        self.active_ids = context.get('active_ids', [])
        self.company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id     

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'get_currency': self._get_currency,
            'report_name': _('Nota Spese trasferta'),
        })

    def _get_currency(self, expense_id):
        if expense_id:
            expense_obj = self.pool.get('hr.expense.expense')
            expense_data = expense_obj.browse(self.cr, self.uid, expense_id)
            for expense_line_data in expense_data.line_ids:
                if expense_line_data.currency_id and expense_line_data.currency_id.name and expense_line_data.currency_id.name!='EUR':
                    return expense_line_data.currency_id.name
        return ''

HeaderFooterTextWebKitParser('report.hr_report_print_expense_webkit',
                             'hr.expense.expense',
                             os.path.dirname(os.path.realpath(__file__)) + '/hr_expense.mako',
                             parser=ParserReportExpense)
