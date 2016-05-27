# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ISA srl (<http://www.isa.it>)
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
    'name': 'Mattioli - Chart of Accounts Mattioli',
    'version': '0.1',
    'category': 'Localization/Account Charts',
    'description': """
Mattioli - Chart of Accounts Mattioli
=====================================

""",
    'depends': ['base_vat',
                'account_chart',
                'base_iban',
                'l10n_it_base',
                'l10n_it',
                'account',
                ],
    'data': ['data/account.account.template.csv',
             'data/account.tax.code.template.csv',
             'account_chart.xml',
             'data/account.tax.template.csv',
             'data/account.fiscal.position.template.csv',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
