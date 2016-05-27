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
    'name': 'EA Sector for NACE',
    'version': '0.1',
    'category': 'Localisation/Italy',
    'author': 'ISA srl',
    'depends': ['l10n_eu_nace',
                ],
    'data': ['security/ir.model.access.csv',
             'data/accreditation.sector.ea.csv',
             'data/accreditation.sector.ea.nace.csv',
             'views/res_partner_view.xml',
             'views/sector_ea_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
