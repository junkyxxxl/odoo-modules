# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Readytec - Customization module',
    'version': '0.1',
    'category': '',
    'author': 'ISA srl',
    'depends': ['base',
                'hr',
                'purchase',
                'account_makeover',
                'account_voucher_makeover',
                'account_banking_sepa_credit_transfer',
                'account_banking_sepa_direct_debit',
                'account_invoice_intracee',
                'account_ricevute_bancarie',
                'stock_makeover',
                'stock_sheet_report_webkit',
                'stock',
                'sale',
                'sale_order_report_qweb',
                'crm',
                'delivery',
                'delivery_makeover',
#                'l10n_it_ddt_makeover',
                'account_cancel',
                'l10n_it_readytec',
                'account_financial_report_webkit',
#                'account_financial_report_webkit_xls',
                'account_statement_report_webkit',
                'account_vat_registries_report_webkit',
                'account_readytec',
                'account_export_teamsystem_readytec',
                'salesagent_commissions',
                'salesagent_commissions_report_webkit',
                'account_central_journal_webkit',
                'dbfilter_from_header',
                'disable_openerp_online',
                'account_invoice_report_qweb',
                'web_export_view',
                ],
    'data': ['views/sale_view.xml',
             'views/sale_order_line_view.xml',
             'views/purchase_view.xml',
             'views/stock_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
