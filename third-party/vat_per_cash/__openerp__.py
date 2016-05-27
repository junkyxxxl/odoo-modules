# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Giuseppe D'Alò (<g.dalo@apuliasoftware.it>)
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "vat_per_cash",
    'version': '0.1',
    'category': 'account',
    'description': """This module implements the functionality
of the calculation of VAT per cash according to the Italian
legislation under Article 32-bis, decree June 22, 2012, number 83""",
    'author': 'Giuseppe DAlò <g.dalo@apuliasoftware.it>',
    'website': 'www-apuliasoftware.it',
    'license': 'AGPL-3',
    "depends": [
        'account',
        'account_vat_period_end_statement',
        'account_invoice_entry_date',
        'account_voucher',
        'report'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'reports.xml',
        'views/registro_iva_in_sospensione.xml',
        'views/wizard_print_report.xml',
        'views/account_invoice_view.xml',
        ],
    'demo': [],
    'installable': True,
    'active': False,
}
