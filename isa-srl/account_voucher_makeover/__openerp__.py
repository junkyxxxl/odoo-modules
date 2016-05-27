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
    'name': 'Account Voucher Makeover',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    'depends' : ['account_makeover',
                 'account_voucher',
                 ],
    'data' : ['res/res_company_view.xml',
              'voucher/account_voucher_makeover_view.xml',
              'voucher/account_voucher_view.xml',
              'voucher/account_voucher_pay_invoice.xml',
              'wizard/wizard_1_supplier_payment_view.xml',
              'wizard/wizard_2_payment_specification_line_view.xml',
              'wizard/wizard_2_payment_specification_view.xml',
              'wizard/wizard_3_confirm_payment_view.xml',
              'wizard/wizard_3_confirm_payment_line_view.xml',
              'wizard/wizard_3_1_values_confirm_view.xml',
              'wizard/wizard_3_2_set_partial_amount_view.xml',
              'wizard/wizard_wht_1_payment_view.xml',
              'wizard/wizard_wht_2_payment_specification_view.xml',
              'wizard/wizard_wht_3_confirm_payment_view.xml',
              'wizard/wizard_1_customer_payment_view.xml',
              'wizard/wizard_2_customer_payment_specification_view.xml',
              'wizard/wizard_3_confirm_customer_payment_view.xml',
              'wizard/wizard_3_confirm_customer_payment_line_view.xml',
              'wizard/wizard_3_1_values_customer_confirm_view.xml',
              'wizard/wizard_3_2_customer_set_partial_amount_view.xml',
              'wizard/wizard_4_post_payment_view.xml',
              'change_due_date/wizard_change_due_date_view.xml',
              'change_due_date/wizard_add_new_line_view.xml',
              'change_due_date/account_invoice_view.xml',
              'change_due_date/account_move_view.xml',
              'menu_actions.xml',
              ],
    'conflicts': ['l10n_it_withholding_tax',
                  ],
    'installable': True,
    'auto_install': True,
    'certificate': ''
}
