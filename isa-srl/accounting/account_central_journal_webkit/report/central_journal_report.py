# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ISA s.r.l. (<http://www.isa.it>).
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

import time
from datetime import datetime
from openerp.report import report_sxw
import os

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser

class central_journal_report(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.filters = []
        super(central_journal_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_print_info': self._get_print_info,
            'set_print_info': self._set_print_info,
            'set_wizard_params': self._set_wizard_params,
            'get_move_lines': self._get_move_lines,
        })

    def _set_wizard_params(self, form_values):
        if form_values['date_move_line_from'] :
            date_move_line_from = form_values['date_move_line_from']
            t_filter = ("date", ">=", date_move_line_from)
            self.filters.append(t_filter)
        if form_values['date_move_line_to'] :
            date_move_line_to = form_values['date_move_line_to']
            t_filter = ("date", "<=", date_move_line_to)
            self.filters.append(t_filter)
        return True

    def _get_print_info(self, fiscalyear_id):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid,
                                               [('id', '=', fiscalyear_id), ])
        fiscalyear_data = fiscalyear_obj.browse(self.cr, self.uid,
                                                fiscalyear_ids)[0]
        print_info = {
            'start_row': fiscalyear_data.progressive_line_number,
            'start_page': fiscalyear_data.progressive_page_number,
            'start_debit': fiscalyear_data.progressive_debit,
            'start_credit': fiscalyear_data.progressive_credit,
            'year_name': fiscalyear_data.name,
        }
        return print_info

    def _set_print_info(self, fiscalyear_id, end_date_print, end_row,
                        end_page, end_debit, end_credit):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid,
                                               [('id', '=', fiscalyear_id), ])
        # fiscalyear_data = fiscalyear_obj.browse(self.cr, self.uid,
        #                                         fiscalyear_ids)[0]
        print_info = {
            'date_last_print': end_date_print,
            'progressive_line_number': end_row,
            'progressive_page_number': end_page,
            'progressive_debit': end_debit,
            'progressive_credit': end_credit,
        }
        res = fiscalyear_obj.write(self.cr, self.uid,
                                   fiscalyear_ids, print_info)
        return res

    def _get_move_lines(self, date_from, date_to):

        try:
            date_from = datetime.strptime(date_from, '%d-%m-%Y').strftime('%Y-%m-%d')
            date_to   = datetime.strptime(date_to,   '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            None

        t_filter = ''
        if date_from:
            t_filter = t_filter + " AND l.date >= '" + date_from + "' "
        if date_to:
            t_filter = t_filter + " AND l.date <= '" + date_to + "' "

        query_move_lines = """
                SELECT l.id AS id,
                            m.date AS mdate,
                            m.document_date AS mdocument_date,
                            m.document_number AS mdocument_number,
                            m.name AS mname,
                            l.ref AS lref,
                            l.name AS lname,
                            l.debit AS ldebit,
                            l.credit AS lcredit,
                            a.id AS account_id,
                            a.code AS account_code,
                            a.name AS account_name
                FROM account_move_line l
                    JOIN account_move m on (l.move_id=m.id)
                    JOIN account_account a on (l.account_id = a.id)
                    JOIN account_journal j on (l.journal_id=j.id)
                WHERE (j.exclude_from_central_journal is null
                       OR j.exclude_from_central_journal = FALSE)
                      """ + t_filter + """
                ORDER BY l.date, l.move_id asc
                 """

        self.cr.execute(query_move_lines)
        res = self.cr.dictfetchall()

        return res

HeaderFooterTextWebKitParser('report.central_journal_report',
                             'account.move.line',
                             os.path.dirname(os.path.realpath(__file__)) + \
                                '/central_journal_report.mako',
                             parser=central_journal_report)
