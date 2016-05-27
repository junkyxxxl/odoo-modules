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
    'name': 'Delivery Makeover',
    'version': '0.1',
    'category': 'Delivery',
    'description': """
Delivery Makeover
=================
Aggiunge il riferimento al picking che la genera sulla riga di fattura.


Creazione Fattura Accompagnatoria
---------------------------------
Dal menu Configurazione-> Magazzino impostare:
Create and open the invoice when the user finish a delivery order

Quando da un Ordine di Consegna si sceglie "Conferma", appare
una popup di conferma per la generazione della fattura accompagnatoria.

""",
    'author': 'ISA srl',
    'depends': ['base',
                'account',
                'account_makeover',
                'stock',
#                'stock_invoice_directly',
                'stock_makeover',
                'stock_account', # per def action_invoice_create()
                'delivery',
                'purchase',
                'sale',
                'sale_stock',
                'sale_journal',
                'l10n_it_base',
                'report_webkit',
                'base_fiscalcode',
                ],
    'data': ['security/ir.model.access.csv',
             'data/stock.picking.goods.appearance.csv',
             'views/res_partner_view.xml',
             'views/stock_picking_goods_appearance_view.xml',
             'views/stock_picking_ddt_view.xml',
             'views/stock_picking_view.xml',
             'views/stock_move_view.xml',
             'views/account_invoice_view.xml',
             'views/account_invoice_line_view.xml',
             'views/sale_order_view.xml',
             'views/delivery_carrier_view.xml',
             'views/stock_picking_type_view.xml',

             # TODO
             # 'views/purchase_order_view.xml',

             'wizard/wizard_1_customer_delivery_makeover_view.xml',
             'wizard/wizard_2_1_customer_delivery_selection_view.xml',
             'wizard/wizard_2_2_uom_values_confirm_view.xml',
             'wizard/wizard_3_order_delivery_specification_view.xml',
             'wizard/wizard_4_post_order_creation_view.xml',
             'wizard/stock_invoice_onshipping_view.xml',
             'wizard/stock_return_picking_view.xml',
             'wizard/stock_makeover_configuration_view.xml',
             'menu_actions.xml',
             ],
    'conflicts': [
        'stock_invoice_directly',
        'l10n_it_ddt',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'certificate': '',
}
