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

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class sale_worksheet_report_isa(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    _name = 'sale.worksheet.report.isa'

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(sale_worksheet_report_isa,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

HeaderFooterTextWebKitParser('report.worksheet_isa',
                             'sale.order',
                             os.path.dirname(os.path.realpath(__file__)) + '/worksheet.mako',
                             parser=sale_worksheet_report_isa)
