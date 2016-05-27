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
    'name': 'Montecristo - Stock Customization module',
    'version': '0.1',
    'category': 'Warehouse Management',
    'description': """
Personalizzazioni per Montecristo
       """,
    'author': 'ISA srl',
    'depends': ['product',
                'stock',
                'product_variant_grid',
                'sale',
                'sale_stock',
                'l10n_it_ddt',
                'l10n_it_ddt_makeover',
                'product_custom_montecristo',
                'sale_makeover',
                'stock_picking_transfer_enhanced',
                ],
    'data': ['security/ir.model.access.csv',
             'sale/sale_view.xml',
             'stock/stock_view.xml',
             'stock/stock_sequence.xml',
             'stock/stock_workflow.xml',
             'product/product_view.xml',
             'partner/res_partner_view.xml',
             'wizard/stock_transfer_details_view.xml',
             'wizard/wizard_order_assign_number_view.xml',
             'wizard/wizard_massive_transfer_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
