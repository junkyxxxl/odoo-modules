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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class purchase_order_shipping_state(osv.osv):
    _name = "purchase.order.shipping.state"
    
    _columns = {
                'order_id':fields.many2one('purchase.order', string="Ordine", required=True, ondelete='cascade'),
                'product_id':fields.many2one('product.product',string='Prodotto',required=True, ondelete='cascade',),
                'ordered_qty': fields.float('Quantità Ordinata', digits_compute=dp.get_precision('Product Unit of Measure')),
                'shipped_qty':fields.float('Quantità Consegnata', digits_compute=dp.get_precision('Product Unit of Measure')),
                'residual_qty':fields.float('Quantità Residua', digits_compute=dp.get_precision('Product Unit of Measure')),                
    }
    
class purchase_order_montecristo(osv.osv):
    _inherit = "purchase.order"   
    
    _columns = {
                'shipping_state_ids': fields.one2many('purchase.order.shipping.state','order_id','Stato Trasferimento Ordine'), 
    }

    def compute_shipped_quantities(self, cr, uid, ids, context=None):
        order_id = self.browse(cr,uid,ids[0])

        line_obj = self.pool.get('purchase.order.shipping.state')
        picking_obj = self.pool.get('stock.picking')
        line_obj.unlink(cr,uid,order_id.shipping_state_ids.ids)
        
        to_create = {}
        
        pick_ids = []
        for po in self.browse(cr, uid, ids, context=context):
            pick_ids += [picking.id for picking in po.picking_ids]          
        
        for po in self.browse(cr, uid, ids, context=context):
            for line in po.order_line:
                if line.product_id:
                    if line.product_id.id not in to_create:
                        to_create[line.product_id.id] = [0,0]
                    to_create[line.product_id.id][0] += line.product_qty
                        
        for item in to_create:
            
            #PRENDO I MOVIMENTI DI USCITA RELATIVI AL PRODOTTO E LEGATI A QUESTO ORDINE
            if pick_ids:
                cr.execute('''
                        SELECT mov.product_uom_qty
                        FROM 
                            stock_move AS mov,
                            stock_picking AS pick,
                            stock_picking_type AS type
                        WHERE 
                            mov.picking_id IN %s AND
                            mov.product_id = %s AND
                            mov.picking_id = pick.id AND
                            pick.picking_type_id = type.id AND
                            type.code = 'outgoing' AND
                            pick.state = 'done'
                ''',(tuple(pick_ids), item))
                
                qry_result = cr.fetchall()
                for line in qry_result:
                    to_create[item][1] -= line[0]
    
                #PRENDO I MOVIMENTI DI INGRESSO RELATIVI AL PRODOTTO E LEGATI A QUESTO ORDINE
    
                cr.execute('''
                        SELECT mov.product_uom_qty
                        FROM 
                            stock_move AS mov,
                            stock_picking AS pick,
                            stock_picking_type AS type
                        WHERE 
                            mov.picking_id IN %s AND
                            mov.product_id = %s AND
                            mov.picking_id = pick.id AND
                            pick.picking_type_id = type.id AND
                            type.code = 'incoming' AND
                            pick.state = 'done'
                ''',(tuple(pick_ids), item))
                
                qry_result = cr.fetchall()
                for line in qry_result:
                    to_create[item][1] += line[0]                
                
            line_obj.create(cr, uid, {'order_id':ids[0], 'product_id':item, 'ordered_qty':to_create[item][0], 'shipped_qty':to_create[item][1], 'residual_qty':to_create[item][0]-to_create[item][1]})
            
        return True    
    