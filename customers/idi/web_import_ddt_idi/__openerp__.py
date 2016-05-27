# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
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
    'name': 'Import DDT',
    'version': '1.0',
    'author': 'Isa Srl',
    'category': 'Web',
    'license': 'AGPL-3',
    'description': """
        Importazione DDT da terzi per idi,
       """,
    'depends': [
        'web',
        'sale',
        'stock',
        'res_partner_idi',
        'account_account_partner',
        'free_invoice_line',
        'account_discount',
        'l10n_it_ddt',
        'sale_stock',
        'sale_order_lot',
        'sale_stock_makeover',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/track_view.xml',
        'views/account_payment.xml',
        'views/stock_warehouse.xml',
        'wizard/import_ddt_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
