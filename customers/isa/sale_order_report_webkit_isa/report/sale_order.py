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
from openerp.tools.translate import _
from openerp import pooler
import os

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class sale_order_report_isa(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    _name = 'sale.order.report.custom.isa'

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(sale_order_report_isa,
              self).__init__(cr, uid, name, context=context)

        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        t_phone = company.partner_id.phone or ''
        t_fax = company.partner_id.fax or ''
        t_email = company.partner_id.email or ''
        self.localcontext.update({
            'time': time,
            'get_order': self._get_order,
            'get_order_line': self._get_order_line,
            'count_lines': self._count_lines,
            'additional_args': [
                ('--footer-font-name', 'Helvetica'),
                ('--footer-font-size', '8'),
                ('--footer-left',
                 ' '.join((_('Tel: '), t_phone, _('            Fax: '), t_fax, _('            Email: '), t_email))),
                ('--footer-right',
                 ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })
        self.context = context

    def _get_order(self, ids):
        order_obj = pooler.get_pool(self.cr.dbname).get('sale.order')
        order_data = order_obj.browse(self.cr, self.uid, ids)
        return order_data

    def _get_order_line(self, order_id, limit_page, offset_page):
        order_obj = pooler.get_pool(self.cr.dbname).get('sale.order')
        order_data = order_obj.browse(self.cr, self.uid, order_id)
        order_lines = []
        if order_data and order_data.order_line:
            hrs_list = []
            hrs = pooler.get_pool(self.cr.dbname).get('sale.order.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('order_id', '=', order_id), ],
                                  limit=limit_page,
                                  offset=offset_page)

            order_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return order_lines

    def _count_lines(self, order_id):
        num_lines = 0
        order_obj = pooler.get_pool(self.cr.dbname).get('sale.order')
        order_data = order_obj.browse(self.cr, self.uid, order_id)
        if order_data and order_data.order_line:
            for _ in order_data.order_line:
                num_lines = num_lines +1
        return num_lines

HeaderFooterTextWebKitParser('report.report_sale_order_isa',
                             'sale.order',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                          '/sale_order.mako',
                             parser=sale_order_report_isa)
