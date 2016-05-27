# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
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

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    subaccount_auto_generation_customer = fields.Boolean('Customers Subaccount Automatic Generation')
    subaccount_auto_generation_supplier = fields.Boolean('Suppliers Subaccount Automatic Generation')
    account_parent_customer = fields.Many2one('account.account', 'Customers Ledger')
    account_parent_supplier = fields.Many2one('account.account', 'Suppliers Ledger')
    account_code_generation_last = fields.Boolean('Account Code Generation Last')

    sale_journal_default = fields.Many2one('account.journal', 'Sale Journal')
    purchase_journal_default = fields.Many2one('account.journal', 'Purchase Journal')
    sale_refund_journal_default = fields.Many2one('account.journal', 'Sale Refund Journal')
    purchase_refund_journal_default = fields.Many2one('account.journal', 'Purchase Refund Journal')

    _defaults = {'tax_calculation_rounding_method': 'round_globally',
                 }
