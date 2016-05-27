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

{
    'name': 'Montecristo - Sale Customization module',
    'version': '0.1',
    'category': '',
    'description': """
Personalizzazioni per Montecristo
==============================
Il modulo estende le viste dei preventivi/ordini di vendita consentendo all'utente di gestire la data presunta di incasso
""",
    'author': 'ISA srl',
    'depends': [
                'sale',
                'sale_stock',
                'sale_journal',
                'product_custom_montecristo',
                'report_qweb_montecristo',
                'sale_salesagent_commissions',
                'grid_custom_montecristo',
                'account',
                'account_makeover',
                'sale_makeover',
                'l10n_it_ddt',
                'l10n_it_ddt_makeover',
                ],
    'data': ['sale_view.xml',
             'account/invoice_view.xml',
             'account/payment_term_view.xml',
             'partner/partner_view.xml',
             'security/ir.model.access.csv',
             'report/sale_report_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
