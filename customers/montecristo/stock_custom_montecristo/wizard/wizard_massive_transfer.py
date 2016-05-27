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

from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class wizard_massive_transfer(osv.osv_memory):
    _name = "wizard.massive.transfer"
    _description = "Massive Transfer"

    _columns = {
        'picking_ids': fields.many2many('stock.picking', string='BoMs'),
    }

    def _get_ids(self, cr, uid, context = None):
        if not context or 'active_ids' not in context or not context['active_ids']:
            return
        res = []
        pick_obj = self.pool.get('stock.picking')
        for id in context['active_ids']:
            pick_data = pick_obj.browse(cr,uid,id,context=context)
            if pick_data.state in ['partially_available','assigned']:
                res.append(id)
        return res
    
    _defaults = {
        'picking_ids': _get_ids,
    }

    def _do_massive_transfer(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        quant_obj = self.pool.get('stock.quant')
        trans_obj = self.pool.get('stock.transfer_details')
        
        for picking_id in ids:
            picking = pick_obj.browse(cr, uid, picking_id, context=context)
            for move in picking.move_lines:
                if move.partially_available and move.product_uom_qty > move.reserved_availability:
    
                    old_reserved_ids = move.reserved_quant_ids
                    quants = []
                    for quant in old_reserved_ids:
                        quants.append((quant,quant.qty))                
                    
                    reserved_avalaibility = move.reserved_availability
                    move_obj.do_unreserve(cr, uid, move.id,context=context)         
                    new_move = move_obj.copy(cr, uid, move.id, {'product_uom_qty': move.product_uom_qty - reserved_avalaibility}, context=context) 
                    if move.product_uom == move.product_uos:
                        move_obj.write(cr, uid, new_move, {'product_uos_qty': move.product_uos_qty - reserved_avalaibility}, context=context) 
                                        
                    move_obj.action_confirm(cr, uid, new_move, context=context)
                    move_obj.write(cr, uid, move.id, {'product_uom_qty': reserved_avalaibility}, context=context)
                    if move.product_uom == move.product_uos:
                        move_obj.write(cr, uid, move.id, {'product_uos_qty': reserved_avalaibility}, context=context) 
                    
                    quant_obj.quants_reserve(cr, uid, quants, move, context=context)                                         
            
            ctx = {}
            for item in context.items():
                ctx[item[0]] = item[1]
            ctx.update({'active_ids':[picking_id], 'active_model':'stock.picking'})
            
            t_res = pick_obj.do_enter_transfer_details(cr,uid,[picking_id],context=ctx)
            
            if t_res and t_res['res_model'] == 'stock.transfer_details':
                trans_obj.do_detailed_transfer(cr, uid, t_res['res_id'], context=context)
                
            elif t_res and t_res['res_model'] == 'stock.picking':
                self._do_massive_transfer(cr, uid, t_res['context']['new_pickings'], context)                 

        return
        

    def do_massive_transfer(self, cr, uid, ids, context=None):
        if not context:
            context = {}        
            
        wizard = self.browse(cr, uid, ids, context=context)[0]
        picking_ids = wizard.picking_ids.ids

        res = self._do_massive_transfer(cr, uid, picking_ids, context=context)
        return     


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
