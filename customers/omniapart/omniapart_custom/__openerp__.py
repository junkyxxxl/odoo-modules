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
    'name': 'Omniapart - Customization module',
    'version': '0.1',
    'category': '',
    'description': """
Personalizzazioni per Omniapart
===============================
Il modulo ha come dipendenze tutti i moduli di personalizzazione
per il Cliente Omniapart.

ATTENZIONE:

Al termine dell'installazione è necessario far partire manualmente la generazione
dei piani dei conti per le 3 aziende Equalitate, Omniapart e SISA
(Configurazione->Azioni->Procedure di configurazione->Configure Accounting Data)

Successivamente è necessario far partire manualmente l'importazione dei dati
relativi ai partner (Configurazione->Azioni->Procedure di configurazione->Configure Partner Data

       """,
    'author': 'ISA srl',
    'depends': ['account',
                'crm_omniapart',
                'account_makeover',
                'l10n_it_base',
                'base_omniapart',
                'res_partner_omniapart',
                'project_omniapart',
                'l10n_it_ea_sector',
                'account_chart_equalitate_omniapart',
                'account_chart_omniapart',
                'account_chart_sisa_omniapart',
                'analytic_user_function',
                'disable_openerp_online',
                'hr_expense',
                'knowledge',
                'account_invoice_report_qweb',
                'account_analytic_analysis',
                'hr_expense_omniapart',
                'account_due_list',
                'account_due_date_report_webkit',
                'account_due_list_ext_isa',
                'account_vat_registries_report_webkit',
                'account_invoice_intracee',
                'product_custom_omniapart',
                'mail_multicompany_omniapart',
                'vat_per_cash',
                'report_qweb_omniapart',
                'sale_omniapart',
                'web_export_view',
                'google_calendar',
                'im_chat',
                'purchase_double_validation',
                'mrp_repair',
                'l10n_it_ddt',
                'l10n_it_ddt_makeover',
                ],
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
