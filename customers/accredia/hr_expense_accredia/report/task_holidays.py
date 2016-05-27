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


class task_holidays(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        self.partner_dict = {}
        super(task_holidays, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_hr_holidays_line': self._get_hr_holidays_line,
            'get_hr_holidays': self._get_hr_holidays,
            'get_partner_dict': self._get_get_partner_dict,
            'get_partner': self._get_get_partner,
            'count_lines': self._count_lines,
            })
        self.context = context

    def _get_hr_holidays_line(self, holidays_id):
        hr_holidays_obj = pooler.get_pool(self.cr.dbname).get('hr.holidays')
        hr_holidays_data = hr_holidays_obj.browse(self.cr, self.uid, holidays_id)
        res = hr_holidays_data.line_ids
        return res

    def _get_hr_holidays(self, holidays_id):
        hr_holidays_obj = pooler.get_pool(self.cr.dbname).get('hr.holidays')
        hr_holidays_data = hr_holidays_obj.browse(self.cr, self.uid, holidays_id)
        return hr_holidays_data

    def _get_get_partner_dict(self, obj):
        if obj and obj.holiday_ids:
            for data in obj.holiday_ids:
                if data.partner_id and data.partner_id.id not in self.partner_dict:
                    self.partner_dict[data.partner_id.id] = []
                self.partner_dict[data.partner_id.id].append(data.id)
            return self.partner_dict
        return []

    def _get_get_partner(self, partner_id):
        hrs = pooler.get_pool(self.cr.dbname).get('res.partner')
        hr_data = hrs.browse(self.cr, self.uid, partner_id)
        return hr_data

    def _count_lines(self, obj):
        num_lines = 0
        if obj and obj.holiday_ids:
            for _ in obj.holiday_ids:
                num_lines = num_lines +1
        return num_lines

HeaderFooterTextWebKitParser('report.task_holidays_accredia',
                             'project.task',
                             os.path.dirname(os.path.realpath(__file__)) + '/task_holidays.mako',
                             parser=task_holidays)
