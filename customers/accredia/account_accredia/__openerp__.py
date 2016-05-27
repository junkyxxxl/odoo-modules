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
    'name': 'Accredia - Accounting Module',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'author': 'ISA srl',
    'depends': ['base',
                'account',
                'account_makeover',
                'account_vat_registries_report',
                'account_voucher_makeover',
                'account_chart_accredia',
                'account_banking_accredia',
                'hr',
                'hr_accredia',
                'doclite',
                'account_followup',
                'project_accredia',
                'l10n_it_fatturapa', # per campo protocol_number della fattura
                ],
    'data': ['security/ir.model.access.csv',
             'views/res_partner_bank_view.xml',
             'views/res_partner_view.xml',
             'views/account_invoice_view.xml',
             'views/account_invoice_line_view.xml',
             'views/account_invoice_classification_view.xml',
             'views/account_payment_term_view.xml',
             'views/account_journal_view.xml',
             'views/hr_departments_view.xml',
             'views/account_analytic_line_view.xml',
             'views/accreditation_group_charges_view.xml',
             'views/accreditation_invoiced_schema_view.xml',
             'views/accreditation_small_lab_view.xml',
             'views/res_company_view.xml',
             'wizard/account_followup_date_view.xml',
             'report/account_followup_report.xml',
             'menu_items.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
