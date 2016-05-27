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
    'name': 'Managing lots items',
    'version': '0.1',
    'category': '',
    'description': """
Managing Lots Items
Nasconde i lotti scaduti dalla selezione dei lotti, se configurato,
inoltre non considera i lotti scaduti nell'assegnazione di un picking
(valido solo con il metodo fefo di prelievo sul punto di stoccaggio).
Modifica il criterio FEFO tenendo conto del pacco nella fase di assegnazione
===================
""",
    'author': 'ISA srl',
    'depends': ['product',
                'stock',
                'product_expiry'
                ],
    'data': ['views/lots_items.xml',
             'security/ir.model.access.csv',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'certificate': '',
}
