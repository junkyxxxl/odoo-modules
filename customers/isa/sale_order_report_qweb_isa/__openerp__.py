# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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
    'name': 'Sale Order Report - Qweb',
    'version': '0.1',
    'sequence': 14,
    'summary': 'Print Sale Order Report',
    'description': """
Print your sales reports
========================
With this module you can personalize the sale order report.

    """,
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'depends': ['sale', 'report', 'base_fiscalcode'],
    'category': 'Sale',
    'data': [
             'sale_report.xml',
             'views/report_saleorder.xml',
             'wizard/sale_report.xml',
            ],
    'demo': [],
    'installable': True,
}
