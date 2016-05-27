# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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

{
    'name': 'Accredia - Expenses',
    'version': '0.1',
    'category': '',
    'author': 'ISA srl',
    'depends': ['hr_expense',
                'analytic',
                'account_analytic_analysis',
                'hr_holidays',
                'project_accredia',
                'project_long_term_accredia',
                'account',
                'account_makeover',
                'hr_expense_multicurrencies',
                'account_financial_report_webkit',
                'report_webkit',
                'l10n_it_e_invoice',
                'hr_timesheet_invoice',
                ],
    'data': ['security/ir.model.access.csv',
             'views/hr_expense_view.xml',
             'views/hr_expense_line_view.xml',
             'views/hr_holidays_view.xml',
             'views/hr_holidays_line_view.xml',
             'views/res_partner_view.xml',
             'views/analytic_line_view.xml',
             'views/hr_departments_view.xml',
             'views/project_task_view.xml',
             'views/account_invoice_view.xml',
             'views/product_view.xml',
             'views/account_move_line_view.xml',
             'data/hr_holidays_data.xml',
             'data/financial_webkit_header.xml',
             'wizard/hr_expense_final_wizard.xml',
             'wizard/hr_holiday_validate_mass_view.xml',
             'report/report_expense.xml',
             'report/report_holidays.xml',
             'report/report_expense_final.xml',
             'report/report_task_holidays.xml',
             ],
    'auto_install': False,
    'demo': [],
    'test': [],
    'installable': True,
    'certificate': '',
}
