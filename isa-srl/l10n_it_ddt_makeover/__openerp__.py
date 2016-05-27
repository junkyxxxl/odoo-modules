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
    'name': 'DDT Makeover',
    'version': '0.1',
    'category': 'Localization/Italy',
    'summary': 'Documento di Trasporto - Makeover',
    'description': """
DDT Makeover
============

""",
    'author': 'ISA srl',
    'depends': ['account',
                'account_makeover',
                'l10n_it_ddt',
                'purchase',
                'delivery',
                'stock',
                'stock_account',
                'report',
                'base_fiscalcode',
                'stock_picking_transfer_enhanced',
                ],
    'data': ['views/account_invoice_line_view.xml',
             'views/account_invoice_view.xml',
             'views/stock_move_view.xml',
             'views/delivery_carrier_view.xml',
             'views/stock_picking_view.xml',
             'views/sale_order_view.xml',
             'views/res_partner_view.xml',
             'views/stock_picking_type_view.xml',
             'views/stock_ddt_view.xml',
             'views/report_ddt.xml',
             'views/report_invoice.xml',
             'security/ddt_security.xml',
             'wizard/wizard_1_customer_delivery_makeover_view.xml',
             'wizard/wizard_2_1_customer_delivery_selection_view.xml',
             'wizard/wizard_2_2_uom_values_confirm_view.xml',
             'wizard/wizard_3_order_delivery_specification_view.xml',
             'wizard/wizard_4_post_order_creation_view.xml',
             'wizard/stock_makeover_configuration_view.xml',
             'wizard/ddt_create_invoice_view.xml',

             'report/report.xml',

             'menu_actions.xml',
             ],
    'conflicts': [
        'stock_invoice_directly',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
    'certificate': '',
}
