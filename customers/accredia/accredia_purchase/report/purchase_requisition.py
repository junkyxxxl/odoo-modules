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


class purchase_requisition(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(purchase_requisition, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_requisition_line': self._get_requisition_line,
            'count_lines': self._count_lines,
            'get_uom': self._get_uom,
            })
        self.context = context

    def _get_uom(self, uom_id):
        context = {'lang': 'it_IT',}
        return self.pool.get('product.uom').browse(self.cr, self.uid, uom_id, context).name

    def _get_requisition_line(self, requisition_id, limit_page, offset_page):
        requisition_obj = pooler.get_pool(self.cr.dbname).get('purchase.requisition')
        requisition_data = requisition_obj.browse(self.cr, self.uid, requisition_id)
        requisition_lines = []
        if requisition_data and requisition_data.line_ids:
            hrs_list = []
            hrs = pooler.get_pool(self.cr.dbname).get('purchase.requisition.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('requisition_id', '=', requisition_id), ],
                                  limit=limit_page,
                                  offset=offset_page)

            requisition_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return requisition_lines

    def _count_lines(self, requisition_id):
        num_lines = 0
        requisition_obj = pooler.get_pool(self.cr.dbname).get('purchase.requisition')
        requisition_data = requisition_obj.browse(self.cr, self.uid, requisition_id)
        if requisition_data and requisition_data.line_ids:
            for _ in requisition_data.line_ids:
                num_lines = num_lines + 1
        return num_lines

HeaderFooterTextWebKitParser('report.purchase_requisition_accredia',
                             'purchase.requisition',
                             os.path.dirname(os.path.realpath(__file__)) + '/purchase_requisition.mako',
                             parser=purchase_requisition)
