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
from datetime import datetime, date
from openerp.report import report_sxw
from openerp.tools.translate import _
import os

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class asset_register_report(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.filters = []
        super(asset_register_report, self).__init__(cr, uid, name, context)

        self.company = self.pool.get('wizard.account.asset.report').browse(self.cr, self.uid, self.parents['active_id']).company_id
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_print_info': self._get_print_info,
            'set_print_info': self._set_print_info,
            'get_assets': self._get_assets,
            'get_date_year': self._get_date_year,
            'report_name': _('Libro Cespiti'),
        })

    def set_context(self, objects, data, ids, report_type=None):

        header_report_name = ' - '.join((_('Libro Cespiti'), self.company.name, self.company.currency_id.name))
        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)

        t_year = ''
        if data['form'] and 'fiscalyear' in data['form'] and data['form']['fiscalyear']:
            t_year = self._get_print_info(data['form']['fiscalyear'])['year_name']

        self.localcontext.update({
            'fiscal_page_base': data.get('fiscal_page_base'),
            'fiscal_year': t_year,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Pagina'), t_year, _('/'), '[page]'))),
                ('--footer-line',),
            ],
        })
        return super(asset_register_report, self).set_context(objects, data, ids, report_type=report_type)
    
    def _get_date_year(self, date):
        if date:
            return str(date[:4])
        return ''

    def _get_print_info(self, fiscalyear_id):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid,
                                               [('id', '=', fiscalyear_id[0]), ])
        fiscalyear_data = fiscalyear_obj.browse(self.cr, self.uid,
                                                fiscalyear_ids)[0]
        print_info = {
            'year_name': fiscalyear_data.name,
        }
        return print_info

    def _set_print_info(self, fiscalyear_id, end_row,
                        end_page):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid,
                                               [('id', '=', fiscalyear_id), ])
        end_date_print = date.today()
        print_info = {
            'date_last_print_asset_register': end_date_print,
        }
        res = fiscalyear_obj.write(self.cr, self.uid,
                                   fiscalyear_ids, print_info)
        return res

    def _get_assets(self, year):

        query_move_lines = """
                SELECT aac.id AS category_id,
                       aac.name AS category_name,
                       aaa.id AS asset_id,
                       aaa.name AS asset_name,
                       aaa.purchase_value AS purchase_value,
                       aadl.amount AS amount,
                       aadl.depreciated_value AS depreciated_value,
                       aadl.remaining_value AS remaining_value,
                       aadl.depreciation_date AS depreciation_date,
                       aaa.purchase_date AS purchase_date
                FROM account_asset_asset aaa
                     JOIN account_asset_depreciation_line aadl ON (aadl.asset_id = aaa.id)
                     JOIN account_asset_category aac ON (aaa.category_id = aac.id)
                     JOIN account_move_line aml ON (aml.id=aadl.move_id)
                     JOIN account_period ap ON (ap.id=aml.period_id)
                     JOIN account_fiscalyear af ON (af.id=ap.fiscalyear_id)
                WHERE aaa.state NOT LIKE 'draft'
                      AND aadl.move_check = TRUE
                      AND af.date_stop <= '""" + year + """-12-31'
                ORDER BY aaa.category_id, aaa.id, aml.id
                 """

        self.cr.execute(query_move_lines)
        res = self.cr.dictfetchall()

        return res

HeaderFooterTextWebKitParser('report.asset_register_report',
                             'account.asset.asset',
                             os.path.dirname(os.path.realpath(__file__)) + \
                                '/asset_register_report.mako',
                             parser=asset_register_report)
