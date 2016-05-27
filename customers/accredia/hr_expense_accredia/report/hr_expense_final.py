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


class ParserReportExpenseFinal(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):

    def __init__(self, cursor, uid, name, context):
        super(ParserReportExpenseFinal, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.filter = None

        self.active_model = context.get('active_model', '')
        self.active_ids = context.get('active_ids', [])
        self.company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id     

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'get_print_info': self._get_print_info,
            'get_expense_lines': self._get_expense_lines,
            'display_target_move': self._get_display_target_move,
            'report_name': _('Riepilogo Nota Spese'),
        })

    def set_context(self, objects, data, ids, report_type=None):

        header_report_name = ' - '.join((_('Riepilogo Nota Spese'), self.company.name, self.company.currency_id.name))
        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)

        t_year = ''
        if 'form' in data and data['form'] and 'fiscalyear' in data['form'] and data['form']['fiscalyear']:
            t_year = self._get_print_info(data['form']['fiscalyear'])['year_name']

        self.localcontext.update({
            'fiscal_year': t_year,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name + ' - Anno ' + t_year),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })
        return super(ParserReportExpenseFinal, self).set_context(objects, data, ids, report_type=report_type)

    def _get_print_info(self, fiscalyear_id):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid,
                                               [('id', '=', fiscalyear_id), ])
        fiscalyear_data = fiscalyear_obj.browse(self.cr, self.uid,
                                                fiscalyear_ids)[0]
        print_info = {
            'year_name': fiscalyear_data.name,
        }
        return print_info

    def _get_expense_lines(self, date_from, date_to):

        query = """
                 SELECT
                     min(l.id) as id,
                     s.employee_id,
                     em.name_related as employee_name,
                     p.expense_type as expense_type,
                     date_trunc('day',s.date) as date,
                     s.currency_id,
                     to_date(to_char(s.date_confirm, 'dd-MM-YYYY'),'dd-MM-YYYY') as date_confirm,
                     to_date(to_char(s.date_valid, 'dd-MM-YYYY'),'dd-MM-YYYY') as date_valid,
                     s.voucher_id,
                     s.department_id,
                     to_char(date_trunc('day',s.create_date), 'YYYY') as year,
                     to_char(date_trunc('day',s.create_date), 'MM') as month,
                     to_char(date_trunc('day',s.create_date), 'YYYY-MM-DD') as day,
                     l.product_id as product_id,
                     l.analytic_account as analytic_account,
                     sum(l.unit_quantity * u.factor) as product_qty,
                     s.company_id as company_id,
                     sum(l.unit_quantity*l.unit_amount) as price_total,
                     (sum(l.unit_quantity*l.unit_amount)/sum(case when l.unit_quantity=0 or u.factor=0 then 1 else l.unit_quantity * u.factor end))::decimal(16,2) as price_average,
                     count(*) as nbr,
                     (select unit_quantity from hr_expense_line where id=l.id and product_id is not null) as no_of_products,
                     (select analytic_account from hr_expense_line where id=l.id and analytic_account is not null) as no_of_account,
                     s.state
                 FROM hr_expense_line l
                     JOIN hr_expense_expense s on (s.id=l.expense_id)
                     LEFT JOIN product_uom u on (u.id=l.uom_id)
                     JOIN hr_employee em on (em.id=s.employee_id)
                     LEFT JOIN product_product p on (p.id=l.product_id)
                 WHERE 1=1
                 """
        if self.active_model != 'hr.expense.expense':
            query += """
                      AND s.state NOT LIKE 'draft'
                      AND s.state NOT LIKE 'cancelled'
                      AND s.state NOT LIKE 'confirm'
                 """
        if date_from and date_to and self.active_model == 'wizard.hr.expense.final':
            query += """
                          AND s.date <= '""" + date_to + """'
                          AND s.date >= '""" + date_from + """'
                     """
        if self.active_model == 'hr.expense.expense' and self.active_ids:
            t_first = False
            string = ''
            for t_id in self.active_ids:
                if t_first:
                    string = string + ','
                if not t_first:
                    string = '('
                    t_first = True
                string = string + str(t_id)
            if string:
                string = string + ')'

            query += """
                          AND l.expense_id in """ + string + """
                     """
        query += """
                 GROUP BY
                     date_trunc('day',s.date),
                     to_char(date_trunc('day',s.create_date), 'YYYY'),
                     to_char(date_trunc('day',s.create_date), 'MM'),
                     to_char(date_trunc('day',s.create_date), 'YYYY-MM-DD'),
                     to_date(to_char(s.date_confirm, 'dd-MM-YYYY'),'dd-MM-YYYY'),
                     to_date(to_char(s.date_valid, 'dd-MM-YYYY'),'dd-MM-YYYY'),
                     l.product_id,
                     l.analytic_account,
                     s.voucher_id,
                     s.currency_id,
                     s.user_valid,
                     s.department_id,
                     l.uom_id,
                     l.id,
                     s.state,
                     s.journal_id,
                     s.company_id,
                     s.employee_id,
                     em.name_related,
                     p.expense_type
                 ORDER BY
                     s.company_id,
                     s.employee_id
                 """

        self.cr.execute(query)
        res = self.cr.dictfetchall()

        return res

HeaderFooterTextWebKitParser('report.account_report_expense_final',
                             'hr.expense.expense',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                         '/hr_expense_final.mako',
                             parser=ParserReportExpenseFinal)
