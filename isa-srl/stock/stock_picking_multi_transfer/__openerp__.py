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
    'name': 'Stock Picking Multi Transfer',
    'version': '0.1',
    'category': 'Warehouse',
    'description': """
Permette di trasferire linee dello stesso picking su stock differenti, da origini differenti
Elimina i domini sugli sotck sorgente e destinazione del wizard di tresferimento picking
""",
    'author': 'ISA srl',
    'depends': ['stock',
                ],
    'data': [
                'wizard/stock_transfer_details.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'certificate': '',
}
