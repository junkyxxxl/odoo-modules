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

from openerp import fields, models, api
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools.translate import _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.depends('document_reference_id', 'document_reference_id.ddt_id', 'document_reference_id.ddt_id.name', 'document_reference_id.ddt_id.date')
    def _get_ddt_origin(self):
        for line in self:
            if (line.document_reference_id and line.document_reference_id.ddt_id and line.document_reference_id.ddt_id.name):
                t_ddt_number = line.document_reference_id.ddt_id.name
                t_ddt_date_ref = line.document_reference_id.ddt_id.date
                t_ddt_date = datetime.strptime(t_ddt_date_ref,
                                               DTF).strftime("%d/%m/%Y")
                line.ddt_origin = t_ddt_number + _(" of ") + t_ddt_date

    # recupera il ddt se presente
    ddt_origin = fields.Char(compute=_get_ddt_origin, store=True, string="DDT")
    # contiene il riferimento allo stock picking
    document_reference_id = fields.Many2one('stock.picking', 'Document Reference')
