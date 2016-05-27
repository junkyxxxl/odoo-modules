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
    'name': 'Mattioli - Product Customization module',
    'version': '0.1',
    'category': '',
    'description': """
Personalizzazioni per Mattioli
==============================
Il modulo estende l'anagrafica prodotto con attributi specifici per il tipo di business
del cliente Mattioli. In particolare, permette di gestire:

- Spessore;
- Essenza;
- Stagionatura;
- Classifica (o Qualità);
- Tipologia;

Riporta infine tutte queste informazioni lungo tutto il percorso d'acquisto
(preventivo; ordine d'acquisto; ordine di consegna; pacchi).

       """,
    'author': 'ISA srl',
    'depends': ['purchase',
                'product',
                'stock',
                'sale_stock',
                'stock_account',
                'mattioli_package_manager',
                'account',
                ],
    'data': ['security/ir.model.access.csv',
             'res/res_essence_view.xml',
             'res/res_wood_quality_view.xml',
             'res/res_wood_type_view.xml',
             'res/res_seasoning_view.xml',
             'res/res_finiture_view.xml',
             'product/product_view.xml',
             'product/product_sequence.xml',
             'product/product_uom.xml',
             'purchase/purchase_view.xml',
             'sale/sale_order.xml',
             'stock/stock_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
