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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class stock_move_line_discount(models.Model):

    _inherit = 'stock.move'

    @api.cr_uid_context    
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move_line_discount, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        if res:
            line = None
            if move.procurement_id and move.procurement_id.sale_line_id:
                line = move.procurement_id.sale_line_id
            elif move.purchase_line_id:
                line = move.purchase_line_id
            if res and line:
                res.update({'discount1':line.discount1,
                            'discount2':line.discount2,
                            'discount3':line.discount3,
                            'max_discount': line.max_discount,})
        return res    
        