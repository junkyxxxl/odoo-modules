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
    'name': 'Warehouse Stock Makeover',
    'version': '0.1',
    'category': 'Warehouse',
    'author': 'ISA srl',
    'description': """
    - Porta la data di creazione del picking sul movimento di magazzino all'atto del trasferimento
    - Introduce la data di ultimo inventario su un prodotto
    ===================
    """,
    'depends': ['stock_account', # necessario per attibute module_stock_invoice_directly
                'product',
                'stock',
                'base_fiscalcode',
                ],
    'data': ['security/stock_makeover_groups.xml',
             'data/stock_incoterms.xml',
             'views/res_config_view.xml',
             'views/product_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'certificate': '',
}
