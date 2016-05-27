# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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

from openerp import fields, models


class AccountInvoiceCancelIsa(models.Model):
    _name = 'account.invoice.cancel.isa'
    _description = "Cancelled Customer Invoices"
    _rec_name = "number"

    number = fields.Char('Invoice Number', size=64, readonly=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, readonly=True)
    protocol_number = fields.Char('Protocol Number', size=64, readonly=True)
