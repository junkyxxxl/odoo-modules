# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ISA s.r.l. (<http://www.isa.it>).
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
    'name': "BEC s.r.l. - Add Filter for Mass Mailing",
    'summary': "Add Filter for Mass Mailing",
    'version': "1.0",
    'author': "ISA srl",
    'category': 'Marketing',
    'website': 'http://www.isa.it',
    'depends': ['base',
                'web',
                'mass_mailing',
                'cq_bec',
                ],
    'data': ['wizard/res_partner_filtraclienti.xml',
             'views/mass_mailing_view.xml',
             'views.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
