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
    'name': 'Patch Odoo - ISA',
    'version': '0.1',
    'category': '',
    'description': """
Fixes to Odoo code provided by ISA.

Questo modulo applica le fix di ISA al modulo base di Odoo.

Contiene la correzione delle traduzioni in italiano
dei moduli base di Odoo.

       """,
    'author': 'ISA srl',
    'depends': [
                'base',
                'web',
                'mail',
                ],
    'data': [
             'security/ir.model.access.csv',
             'data/res.country.code.csv',
             'view/res_partner.xml',
             ],
    'demo': [],
    'test': [],
    'qweb' : [
        "static/src/xml/base.xml",
        "static/src/xml/res_partner.xml",
    ],
    'installable': True,
    'auto_install': True,
    'certificate': ''
}
