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
    'name': 'Omniapart - Sale customization module',
    'version': '0.1',
    'category': '',
    'description': """
Personalizzazioni per Omniapart
===============================
Il modulo modifica il modulo Sale per la gestione degli acconti sui preventivi e gli ordini di vendita
       """,
    'author': 'ISA srl',
    'depends': ['account',
                'sale',
                'report',
                'vat_per_cash',
                'account_makeover',
                ],
    'data': ['sale_view.xml',
             'sale_make_invoice_advance.xml',
             'account_invoice_view.xml',
             'sale_workflow.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
