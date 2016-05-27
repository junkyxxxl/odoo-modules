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


class order(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_order_line': self._get_order_line,
            'count_lines': self._count_lines,
            'get_uom': self._get_uom,
            })
        self.context = context

    def _get_uom(self, uom_id):
        context = {'lang':'it_IT',}
        return self.pool.get('product.uom').browse(self.cr, self.uid, uom_id, context).name

    def _get_order_line(self, order_id, limit_page, offset_page):
        order_obj = pooler.get_pool(self.cr.dbname).get('purchase.order')
        order_data = order_obj.browse(self.cr, self.uid, order_id)
        order_lines = []
        if order_data and order_data.order_line:
            hrs_list = []
            hrs = pooler.get_pool(self.cr.dbname).get('purchase.order.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('order_id', '=', order_id), ],
                                  limit=limit_page,
                                  offset=offset_page)

            order_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return order_lines

    def _count_lines(self, order_id):
        num_lines = 0
        order_obj = pooler.get_pool(self.cr.dbname).get('purchase.order')
        order_data = order_obj.browse(self.cr, self.uid, order_id)
        if order_data and order_data.order_line:
            for _ in order_data.order_line:
                num_lines = num_lines +1
        return num_lines

HeaderFooterTextWebKitParser('report.purchase_order_accredia',
                             'purchase.order',
                             os.path.dirname(os.path.realpath(__file__)) + '/order.mako',
                             parser=order)
