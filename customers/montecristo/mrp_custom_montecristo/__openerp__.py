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
    'name': 'Montecristo - MRP Customization module',
    'version': '0.1',
    'category': 'Manufacturing',
    'description': """
Personalizzazioni per Montecristo
       """,
    'author': 'ISA srl',
    'depends': ['product',
                'product_custom_montecristo',
                'product_variant_grid',
                'mrp',
                ],
    'data': [
             'mrp/mrp_view.xml',
             'wizard/wizard_massive_update.xml',
             'security/ir.model.access.csv',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
