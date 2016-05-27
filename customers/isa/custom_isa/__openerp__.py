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
    'name': 'ISA s.r.l. - Customization module',
    'version': '0.1',
    'category': '',
    'author': 'ISA srl',
    'depends': ['hr_department_isa',
                'base_res_company_isa',
                'hr_overtime',
                'hr_holidays_isa',
                'project_custom_isa',
                'hr_attendance_isa',
                'hr_employee_report',
                'base_isa',
                'sale',
                'sale_isa',
                'l10n_it_base',
                'base_fiscalcode',
                'account_makeover',
                'account_voucher_makeover',
                'account_invoice_cancel_management',
                'account_financial_report_webkit',
                'account_financial_report_webkit_xls',
                'account_statement_report_webkit',
                'account_vat_registries_report_webkit',
                'document_choose_directory',
                'doclite',
                'account_invoice_report_qweb',
                'disable_openerp_online',
                'account_vat_registries_report',
                'project_timesheet_isa',
                'hr_expense_isa',
                'account_analytic_isa',
#                'account_pentaho_print_isa',
#                'sale_order_report_qweb_isa',
                ],
    'data': ['data/res.company.csv',
             ],
    'qweb': ["static/src/xml/base.xml", ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
