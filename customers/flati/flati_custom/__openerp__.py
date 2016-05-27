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
    'name': 'FLATI - Customization module',
    'version': '0.1',
    'category': '',
    'description': """
            Personalizzazioni per Cliente Flati s.r.l.

            ATTENZIONE:
                I moduli 'account_report_journal_account'e 'account_report_journal_items'
                necessitano dei template customizzati per cliente che si trovano
                nella sotto-cartella 'report'.
       """,
    'author': 'ISA srl',
    'depends': ['account_makeover',
                'account_voucher',
                'account_voucher_makeover',
                'account_ricevute_bancarie',
                'account_due_list',
                'account_invoice_template',
                'account_cancel',
                'account_payment',
                'account_move_template',
                'account_invoice_intracee',
                'account_flati',
                'project',
                'project_flati',
                'account_analytic_default',
                'account_due_list_ext_isa',
                'account_due_date_report_webkit',
                'account_invoice_cancel_management',
                'account_journal_items_webkit',
                'base_fiscalcode',
                'l10n_it',
                'report_webkit',
                'account_financial_report_webkit',
                'account_financial_report_webkit_xls',
                'account_statement_report_webkit',
                'account_vat_registries_report_webkit',
                'account_exporter_statements_webkit',
                'account_report_journal_account_flati',
                'account_report_layout_flati',
                'report_aeroo',
                'report_aeroo_ooo',

                # 7.0
                # 'l10n_it_partially_deductible_vat',
                # 'account_invoice_tax_by_column',

                # 8.0
                'disable_openerp_online',
                'web_export_view',
                'account_exporter_statements',
                ],
    'data': ['security/flati_group.xml',
             'menu_items.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
