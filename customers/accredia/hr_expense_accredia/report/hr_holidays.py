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

import time
from openerp.report import report_sxw
from openerp import pooler
import os
from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class hr_holidays(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(hr_holidays, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_hr_holidays_line': self._get_hr_holidays_line,
            'count_lines': self._count_lines,
            })
        self.context = context

    def _get_hr_holidays_line(self, holidays_id, limit_page, offset_page):
        hr_holidays_obj = pooler.get_pool(self.cr.dbname).get('hr.holidays')
        hr_holidays_data = hr_holidays_obj.browse(self.cr, self.uid, holidays_id)
        hr_holidays_lines = []
        if hr_holidays_data and hr_holidays_data.line_ids:
            hrs_list = []
            hrs = pooler.get_pool(self.cr.dbname).get('hr.holidays.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('holidays_id', '=', holidays_id), ],
                                  limit=limit_page,
                                  offset=offset_page)

            hr_holidays_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return hr_holidays_lines

    def _count_lines(self, holidays_id):
        num_lines = 0
        hr_holidays_obj = pooler.get_pool(self.cr.dbname).get('hr.holidays')
        hr_holidays_data = hr_holidays_obj.browse(self.cr, self.uid, holidays_id)
        if hr_holidays_data and hr_holidays_data.line_ids:
            for _ in hr_holidays_data.line_ids:
                num_lines = num_lines +1
        return num_lines

HeaderFooterTextWebKitParser('report.hr_holidays_accredia',
                             'hr.holidays',
                             os.path.dirname(os.path.realpath(__file__)) + '/hr_holidays.mako',
                             parser=hr_holidays)
