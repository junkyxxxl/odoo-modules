# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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


class StockMoveExporterStatements(models.Model):
    _inherit = "stock.move"

    @api.cr_uid_context
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context):
        res = super(StockMoveExporterStatements, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
 
        if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id:
            sale = move.procurement_id.sale_line_id.order_id
            exp_obj = self.pool.get('account.exporter.statements')
            exp_ids = exp_obj.search(cr, uid, [('partner_id', '=', sale.partner_id.id),
                                      ('letter_status', '=', 'A')],
                                     limit=1, context=context)
            if exp_ids:
                res['invoice_line_tax_id'] = [(6, 0, [exp_obj.browse(cr,uid,exp_ids).vat_code_id.id])]
        return res
