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
    'name': "Global Discounts",
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """
Questo modulo implementa la gestione di scontistiche globali ed omaggi negli ordini di vendita e nelle fatture.
""",
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    "depends" : ['account',
                 'sale',
                 'stock',
                 'stock_account',
                ],
    "data" : [
              'security/ir.model.access.csv',
              'views/sale_order_view.xml',
              'views/account_invoice_view.xml',
              'views/account_discount_view.xml',
              'views/account_payment_term_view.xml',
              'views/product_product_view.xml',
              'views/res_partner_view.xml',
              'views/res_company_view.xml',
             ],
    "demo" : [],
    "installable": True
}
