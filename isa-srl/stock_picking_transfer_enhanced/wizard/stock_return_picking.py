# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv
from openerp.tools.translate import _

class stock_return_picking(osv.osv_memory):
    _inherit = 'stock.return.picking'

    def _create_returns(self, cr, uid, ids, context=None):
        new_picking, pick_type_id = super(stock_return_picking, self)._create_returns(cr, uid, ids, context=context)
        
        parent_pick_id = None
        
        return_move_ids = self.read(cr, uid, ids[0], context=context)['product_return_moves']
        if return_move_ids:
            ret_id = self.pool.get('stock.return.picking.line').browse(cr, uid, return_move_ids[0], context=context)
            parent_pick_id = ret_id.move_id.picking_id.id
        
        if parent_pick_id:
            self.pool.get('stock.picking').write(cr, uid, new_picking, {'origin_picking_id': parent_pick_id}, context=context)
        
        return new_picking, pick_type_id



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
