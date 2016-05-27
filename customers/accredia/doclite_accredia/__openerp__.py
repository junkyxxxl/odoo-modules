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
    'name': 'Accredia - Doclite Integration',
    'version': '0.1',
    'category': '',
    'author': 'ISA srl',
    'depends': ['base',
                'l10n_it_base',
                'hr_accredia',
                'doclite',
                'document',
                ],
    'data': ['security/ir.model.access.csv',
             'views/document_model_view.xml',
             'views/document_category_view.xml',
             'views/server_view.xml',
             'views/res_users_view.xml',
             'views/hr_department_view.xml',
             'views/doclite_accredia.xml',
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
