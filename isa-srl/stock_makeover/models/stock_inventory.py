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

from openerp.osv import osv
from openerp.tools.translate import _


class StockInventory(osv.osv):
    _inherit = 'stock.inventory'

    def action_done(self, cr, uid, ids, context=None):
        res = super(StockInventory, self).action_done(cr, uid, ids, context=context)
        prod_obj = self.pool.get('product.product')
        
        for inv in self.browse(cr, uid, ids, context=context):
            prod_ids = []
            for inventory_line in inv.line_ids:
                if inventory_line.product_id.id not in prod_ids:
                    prod_ids.append(inventory_line.product_id.id)
            prod_obj.write(cr,uid,prod_ids,{'date_last_inventory':inv.date})
            
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        for inventory in self.browse(cr, uid, ids, context=context):
            if inventory.state == 'done':
                raise osv.except_osv(_('Error'),_('Inventory %s is in state %s. You can only delete documents in state draft, progress or canceled') % (inventory.name, inventory.state))
        super(StockInventory,self).unlink(cr, uid, ids, context=context)
        return True
