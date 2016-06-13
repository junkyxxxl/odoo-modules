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

from openerp import fields, models, api
from openerp import SUPERUSER_ID

class StockMovePurchase(models.Model):
    _inherit = "stock.move"

    def _get_master_data(self, cr, uid, move, company, context=None):
        if context.get('inv_type') == 'in_invoice' and move.purchase_line_id:
            purchase_order = move.purchase_line_id.order_id
            return purchase_order.partner_id, SUPERUSER_ID, purchase_order.currency_id.id
        elif context.get('inv_type') == 'in_refund' and move.origin_returned_move_id.purchase_line_id:
            purchase_order = move.origin_returned_move_id.purchase_line_id.order_id
            return purchase_order.partner_id, purchase_order.SUPERUSER_ID, purchase_order.currency_id.id
        elif context.get('inv_type') in ('in_invoice', 'in_refund') and move.picking_id:
            # In case of an extra move, it is better to use the data from the original moves
            for purchase_move in move.picking_id.move_lines:
                if purchase_move.purchase_line_id:
                    purchase_order = purchase_move.purchase_line_id.order_id
                    return purchase_order.partner_id, SUPERUSER_ID, purchase_order.currency_id.id        
        #QUESTO AVVIENE SOLO SE NON E' VERIFICATO NESSUNO DEI PRECEDENTI CASI. E' PREFERIBILE RISPETTO ALLA CLAUSOLA ELSE, POICHE' IL PROGRAMMA POTREBBE ENTRARE NEL SECONDO BRANCH ELIF E MAI ARRIVARE AL return
        return super(StockMovePurchase,self)._get_master_data(cr, uid, move, company, context=context)