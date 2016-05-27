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
    'name': 'Sales Management - ISA',
    'version': '0.1',
    'category': 'Sales Management',
    'sequence': 14,
    'summary': 'Quotations, Sales Orders, Invoicing',
    'description': """
Il modulo modifica la funzionalità dei preventivi, in particolare:
modifica e corregge il report dei preventivi, evitando di mostrare
lo sconto se è pari a zero;
consente di specificare le ragioni di un annullamento di un preventivo,
specificando se si tratta di un preventivo sostituito, scaduto o non accettato;
aggiunge i filtri sullo stato annullato, sostituito, scaduto o non accettato.

    """,
    'author': 'ISA srl',
    'website': 'http://www.openerp.com',
    'depends': ['sale',
                'report',
                'account_invoice_entry_date',
                ],
    'data': ['views/sale_view.xml',
             'views/sale_order_line_view.xml',
             'report/sale_order_report.xml',
             'wizard/sale_make_invoice_advance.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
