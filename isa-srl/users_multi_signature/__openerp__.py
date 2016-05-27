# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ISA srl (<http://www.isa.it>)
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
    'name': 'Users Multi-Signature',
    'version': '0.1',
    'category': '',
    'description': """
Il modulo introduce la possibilità di associare più firme ad un utente, ciascuna firma legata ad una company; tali firme vengono automaticamente alternate come firma principale ogni volta che l'utente cambia azienda.
       """,
    'author': 'ISA srl',
    'depends': ['base',],
    'data': [
             'views/res_users_view.xml',
             'security/ir.model.access.csv'
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
