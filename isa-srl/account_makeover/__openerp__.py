# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 ISA s.r.l. (<http://www.isa.it>).
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
    'name': 'Account Makeover',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    'depends': ['base',
                'account',
                'base_fiscalcode',
                'l10n_it',
                'email_template',
                'account_vat_registries_report',
                'account_invoice_entry_date',
                'stock_account',
                'sale',
                ],
    'data': ['security/ir.model.access.csv',
             'data/account_payment_term.xml',
             'data/account_withholding_tax.xml',
             'data/account.fiscal.position.template.csv',
             'views/payment_term_line_view.xml',
             'views/product_view.xml',
             'views/account_journal_view.xml',
             'views/account_invoice_view.xml',
             'views/account_invoice_maturity_preview_lines_view.xml',
             'views/account_withholding_tax_isa_view.xml',
             'views/account_move_view.xml',
             'views/account_account_view.xml',
             'views/res_partner_view.xml',
             'views/res_company_view.xml',
             'views/report_overdue.xml',
             'wizard/wizard_search_manual_reconciliation.xml',
             ],
    'conflicts': ['l10n_it_withholding_tax',
                  'l10n_it_vat_registries',
                  ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'certificate': ''
}
