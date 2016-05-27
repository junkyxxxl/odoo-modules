# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 OpenERP Italian Community (<http://www.openerp-italia.org>). 
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw
import os
from openerp.tools.translate import _
from datetime import datetime

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class account_journal_items_webkit(report_sxw.rml_parse):
    _name = 'account.report.journal.items.isa'

    def __init__(self, cr, uid, name, context):    
        self.cr = cr
        self.uid = uid
        self.context = context
        self.filters = []
        self.partner_filter = ()       
        super(account_journal_items_webkit, self).__init__(cr, uid, name, context)
        
        company = self.pool.get('analytic.journal_report').browse(self.cr, self.uid, self.parents['active_id']).company_id
        header_report_name = ' - '.join((_('SCADENZARIO'), company.name, company.currency_id.name))

        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)    
            
        self.localcontext.update({
            'time': time,
            'get_wizard_params':self._get_wizard_params,
            'get_journal_moves':self._get_journal_moves,
            'get_journal_totals':self.get_journal_totals,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_wizard_params(self, form_values):

        # partner_filter
        if form_values['partner_id'] :
            # partner_id = form_values['partner_id']
            self.partner_filter = (form_values['partner_id'])

        # filters
        if form_values['date_from'] :
            date_storage_from = form_values['date_from']
            t_filter = ("date", ">=", date_storage_from)
            self.filters.append(t_filter)
        if form_values['date_to'] :
            date_storage_to = form_values['date_to']
            t_filter = ("date", "<=", date_storage_to)
            self.filters.append(t_filter)
        if form_values['account_id'] :
            date_storage_account = form_values['account_id']
            t_filter = ("account_id", "=", date_storage_account[0])
            self.filters.append(t_filter)
        if form_values['company_id']:
            storage_company = form_values['company_id']
            t_filter = ("company_id", "=", storage_company[0])
            self.filters.append(t_filter)            

    def _get_journal_moves(self):

        journal_model = self.localcontext['data']['model']
        report_obj = self.pool.get(journal_model)
        line_ids = report_obj.search(self.cr, self.uid, self.filters)
        report_lines = report_obj.browse(self.cr, self.uid, line_ids)
        filter_line = []
        if self.partner_filter :
            for line in report_lines:
                if line['move_id']['partner_id']['id'] == self.partner_filter :
                    filter_line.append(line)
            report_lines = filter_line
        return report_lines
    
    def get_journal_totals(self, positive=True):

        report_lines = self._get_journal_moves()
        plus = 0
        minus = 0
        for line in report_lines:
            if line['amount'] >= 0 :
                plus += line['amount']
            else:
                minus += line['amount']
        if positive :
            value = plus
        else:
            value = minus
        return value

HeaderFooterTextWebKitParser('report.account_journal_items_pdf',
                             'account.analytic.line',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                         '/report_journal_items.mako',
                             parser=account_journal_items_webkit)

