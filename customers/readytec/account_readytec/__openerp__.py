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
    'name': 'Account Readytec',
    'version': '0.1',
    'category': '',
    'author': 'ISA srl',
    'depends': ['account',
                'account_makeover',
                'sale',
                'account_payment_extension',
                'account_financial_report_webkit',
                'account_statement_report_webkit',
                ],
    'data': ['data/account_payment_term.xml',
             'views/account_invoice_view.xml',
             'views/res_company_view.xml',
             'views/sale_view.xml',
             'views/account_tax_code_view.xml',
             'menu_items.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
