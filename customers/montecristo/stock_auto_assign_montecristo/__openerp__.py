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
    'name': 'Montecristo - Stock Customization Module Advanced',
    'version': '0.1',
    'category': 'Warehouse Management',
    'description': """
Personalizzazioni per Montecristo - Implementa l'algoritmo di auto-assegnazione su Scalature e Divisioni
       """,
    'author': 'ISA srl',
    'depends': ['product',
                'stock',
                'sale',
                'sale_stock',
                'product_custom_montecristo',
                'stock_custom_montecristo',
                'sale_custom_montecristo',
                ],
    'data': ['stock/stock_view.xml',],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
    'active': False,
    'certificate': '',
}
