# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, osv

class stock_inventory_line(osv.osv):
    
    _inherit = 'stock.inventory.line'
    
    
    def _resolve_inventory_line(self, cr, uid, inventory_line, context=None):
        context['recompute'] = True
        
        #Richiamo la super relativa al metodo resolve_inventory_line, passandogli al context una variabile settata a True
        move_id = super(stock_inventory_line, self)._resolve_inventory_line(cr,uid, inventory_line, context)
        
        diff = inventory_line.theoretical_qty - inventory_line.product_qty        
        if move_id and diff < 0 and inventory_line.package_id:
            

            
            stock_move_obj = self.pool.get('stock.move')
            stock_quant_obj = self.pool.get('stock.quant')
            move = stock_move_obj.browse(cr, uid, move_id, context=context)
            quants = [x.id for x in move.quant_ids]             

            for quant in quants:

                domain = [('id','!=',quant)]
                domain.append(('package_id','=',inventory_line.package_id.id))            
                if inventory_line.prod_lot_id:
                    domain.append(('lot_id','=',inventory_line.prod_lot_id.id))                
                if inventory_line.location_id:
                    domain.append(('location_id','=',inventory_line.location_id.id))      
                
                match_quant = stock_quant_obj.search(cr, uid, domain, context=context)
                if match_quant:
                    new_in_date = stock_quant_obj.browse(cr,uid,match_quant[0],context=context).in_date
                    stock_quant_obj.write(cr, uid, quant, {'in_date': new_in_date}, context=context)
        
        return move_id