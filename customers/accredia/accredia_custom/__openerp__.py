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
    'name': 'Accredia - Customization module',
    'version': '0.1',
    'category': '',
    'author': 'ISA srl',
    'depends': ['base',
                'l10n_it_base',
                'hr_accredia',
                'project_accredia',
                'account_accredia',
                'accredia_purchase',
                'sale_accredia',
                'project_action_accredia',
                'hr_timesheet_invoice_accredia',
                'hr_expense',
                'analytic_contract_hr_expense',
                'hr_expense_accredia',
                'doclite',
                'doclite_accredia',
                'web_export_view',
                'account_financial_report_webkit',
                'account_financial_report_webkit_xls',
                'account_statement_report_webkit',
                'account_vat_registries_report_webkit',
                'account_invoice_report_accredia',
                'hr_expense_multicurrencies',
                'l10n_it_e_invoice',
                'account_invoice_force_number',
                'l10n_it_pec',
                'event',
                'pentaho_reports',
                'disable_openerp_online',
                ],
    'data': ['data/res.company.csv',
             'delete_items.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
