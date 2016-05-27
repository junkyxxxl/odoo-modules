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
    'name': 'Account Invoice Cancel Management',
    'version': '0.1',
    'category': 'Generic Modules/Accounting',
    'author': 'ISA srl',
    'depends': ['account',
                'account_cancel',
                'account_makeover',
                ],
    'data': ['security/management_group.xml',
             'security/ir.model.access.csv',
             'views/account_invoice_cancel_customer_view.xml',
             'views/account_invoice_view.xml',
             'views/account_journal_view.xml',
             'menu_items.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'certificate': '',
}
