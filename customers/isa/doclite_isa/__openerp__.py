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
    'name': 'ISA - Doclite Integration',
    'version': '0.1',
    'category': '',
    'description': """
Integrazioni Doclite per ISA srl
================================


       """,
    'author': 'ISA srl',
    'depends': ['base',
                'doclite',
                'document',
                ],
    'data': ['security/ir.model.access.csv',
             'views/document_model_view.xml',
             'views/document_category_view.xml',
             'views/doclite_isa.xml',
             'menu_items.xml',
             ],
    'qweb': [
        'static/src/xml/url.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
