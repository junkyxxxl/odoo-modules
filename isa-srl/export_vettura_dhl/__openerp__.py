# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2015 ISA srl (<http://www.isa.it>)
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
    'name': 'Export DDT/Fatture Accompagnatorie dhl',
    'version': '0.1',
    'category': '',
    'description': """
Export DDT/Fatture Accompagnatorie Dhl
===================
""",
    'author': 'ISA srl',
    'depends': ['base',
				'web',
				'product',
                'stock',
                'product_family',
                'l10n_it_ddt',
                ],
    'data': ['data/classifier1_dhl.xml',
             'data/product.template.csv',
             'views/export_dhl.xml',
             'views/stock_ddt_dhl.xml',
             'views/export_ddt_view.xml',
             'views/invoice_dhl.xml',
             ],
    'qweb': ['static/src/xml/export_ddt_template.xml',
            ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False
}
