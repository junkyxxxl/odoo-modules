# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 ISA s.r.l. (<http://www.isa.it>).
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
    'name': 'Primapaint Report QWeb',
    'version': '0.1',
    'category': 'Reporting',
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    'depends': ['product',
                'family_commission_primapaint',
                'stock',
                'sale_stock',
                ],
    'data': [
             'security/ir.model.access.csv',
             'views/report_onhand_products.xml',
             'views/report_pricelist.xml',
             'views/onhand_report_view.xml',
             'data/report_paperformat.xml',
             'wizard/wizard_print_pricelist_view.xml',
             'report.xml',
             ],
    'demo': [],
    'installable': True,
}
