# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015
#    Andrea Cometa <a.cometa@apuliasoftware.it>
#    WEB (<http://www.apuliasoftware.it>).
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
    'name': "ISA Sale Analysis",
    'version': '0.1',
    'category': 'mrp',
    'description': """Custom sale analysis""",
    'author': 'Andrea Cometa <a.cometa@apuliasoftware.it>',
    'website': 'www.apuliasoftware.it',
    'license': 'AGPL-3',
    "depends": [
        'sale',
        'mrp',
        'product',
        'product_custom_montecristo',
        'sale_makeover',
        'purchase'],
    "data": [
        'security/ir.model.access.csv',
        'wizard/production_analysis_view.xml',
        'wizard/purchase_analysis_view.xml',
        'views/sale_analisys_view.xml',
        'reports.xml',
        'report/summary_requirement.xml',
    ],
    "active": False,
    "installable": True
}
