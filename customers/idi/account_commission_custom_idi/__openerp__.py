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
    'name': 'Account Commission Custom IDI',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """

Questo modulo introduce personalizzazioni per il cliente IDI alla gestione di 
agenti e provvigioni.
""",
    'author': 'ISA srl',
    'depends': [
                'sale',
                'delivery_makeover',
                'account_commission',
                'marketing',
                'crm',
                ],
    'data': [            
             'views/sale_order_view.xml', 
             'views/account_menuitem.xml',
             ],
    'installable': True,
    'auto_install': False,
    'certificate': '',
}
