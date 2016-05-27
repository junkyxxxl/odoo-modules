# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
    'name': 'Montecristo SalesAgent Commission - Provvigioni Agenti',
    'version': '0.2',
    'category': 'Finance',
    'description': """
Estende il modulo salesagent_commissions per il calcolo delle provvigioni ai subagenti.
Si definisce subagente un agente che effettua una vendita al cliente di un altro agente (l'agente base
di un cliente è definito nell'anagrafica clienti). In tal caso, la provvigione da pagare al subagente è 
ridotta di una certa percentuale (impostabile a livello di agente, cliente o prodotto, allo stesso modo
delle percentuali di provvigione definite nel modulo base).

L'agente base riceve l'altra parte della provvigione.

        """,
    'author': ["ISA srl"],
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    "active": False,
    "installable": True,
    "depends": ['base',
                'product',
                'sale',
                'sale_stock',
                'account',
                'salesagent_commissions',
                'sale_salesagent_commissions',
                'l10n_it_ddt',
                'l10n_it_ddt_makeover',
                'delivery',
                'account_invoice_intracee',
                'sale_custom_montecristo',
                'sale_crm',
                'sale_journal',
                'portal_sale',
                'account_discount',
                'free_invoice_line',
                'mrp',
                'sale_makeover',
                ],
    "data": ['security/ir.model.access.csv',
             'data/mail_notification_data.xml',
             'sale/sale_view.xml',
             'partner/partner_view.xml',
             'product/category_view.xml',
             'product/product_view.xml',
             'account/invoice_line_view.xml',
             'account/account_discount_view.xml',
             'account/account_invoice_view.xml',
             'account/account_payment_term_view.xml',
             'security/partner_security.xml',
             'wizard/wizard_commissions_payment_view.xml',
             'wizard/wizard_payment_cancellation_view.xml',
             'wizard/wizard_invoice_commissions_payment_view.xml',
             'wizard/wizard_invoice_payment_cancellation_view.xml',
             'wizard/wizard_sale_confirm.xml',
             ],
}
