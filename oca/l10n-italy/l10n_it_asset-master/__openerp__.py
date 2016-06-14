# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2014 Apulia Software S.r.l. (<info@apuliasoftware.it>)
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Italian localization Asset",
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
        This module adds functionality to calculate and print the amortization 
        on the assets of Italian companies.
        """,
    'author': 'Apulia Software S.r.l.',
    'website': 'www.apuliasoftware.it',
    'license': 'AGPL-3',
    "depends" : [
        'account',
        'account_asset',
        ],
    "init_xml" : [],
    "update_xml" : [
        'account_asset.xml',
        'wizard/calculate_amortization.xml',
        'wizard/wizard_asset_compute.xml',
        ],
    "active": False,
    "installable": True,
}
