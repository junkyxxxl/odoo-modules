# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 ISA s.r.l. (<http://www.isa.it>).
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
    'name': 'Omniapart Report QWeb',
    'version': '0.1',
    'category': 'Reporting',
    'description': 'Questo modulo introduce personalizzazioni alle stampe del cliente Omniapart',
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    'depends' : ['account_makeover',
                 'sale_omniapart',
                 'report',
                 'purchase',
                 'sale',
                 'account',
                ],
    'data' : [
              'data/report_paperformat.xml',
              'views/report_invoice_qweb.xml',
              'views/report_saleorder.xml',
              'views/report_saleorder_light.xml',
              'views/report_purchaseorder_light.xml',
              'invoice_report.xml',
              'sale_report.xml',
              ],
    'demo' : [],
    'installable': True,
}
