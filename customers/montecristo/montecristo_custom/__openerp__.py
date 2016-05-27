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
    'name': 'Montecristo - Customization module',
    'version': '0.1',
    'category': '',
    'description': """
Personalizzazioni per Cliente Montecristo
=========================================
Il modulo ha come dipendenze tutti i moduli di personalizzazione
per il Cliente Montecristo.

       """,
    'author': 'ISA srl',
    'depends': ['l10n_it_base',
                'account_makeover',
                'disable_openerp_online',
                'sale_salesagent_commissions',
                'sale_stock_salesagent_commissions',
                'salesagent_commissions',
                'stock_salesagent_commissions',
                'crm',
                'mrp',
                'montecristo_salesagents_commissions',
                'montecristo_salesagents_commission_report_qweb',
                'product_variant_grid',
                'sale_product_variant_grid',
                'account_product_variant_grid',
                'purchase_product_variant_grid',
                'product_custom_montecristo',
                'account_invoice_report_qweb',
                'sale_custom_montecristo',
                'grid_custom_montecristo',
                'l10n_it_ddt_makeover',
                'report_qweb_montecristo',
                'mrp_custom_montecristo',
                'account_invoice_intracee',
                'account_due_list',
                'account_due_date_report_webkit',
                'account_due_list_ext_isa',
                'account_vat_registries_report_webkit',
                'isa_sale_analisys',
                'web_export_view',
                'account_invoice_cancel_management',
                'account_exporter_statements',
                'account_exporter_statements_webkit',
                'account_reports_grouping',
                'knowledge',
                ],
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
