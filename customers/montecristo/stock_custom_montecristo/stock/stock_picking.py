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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _get_move_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()

    def _get_total_qty(self, cr, uid, ids, field_name, arg, context=None):
        r = {}
        for id in ids:
            tot = 0.0
            picking = self.browse(cr, uid, id)
            for line in picking.move_lines: 
                tot += line.product_uom_qty
            r[id] = tot
        return r

    _columns = {
        'default_location_dest_id': fields.related('picking_type_id', 'default_location_dest_id', type='many2one', relation='stock.location', string='Destination Location', readonly=True),                
        'total_qty': fields.function(_get_total_qty, copy=False, type="float", digits_compute=dp.get_precision('Product Unit of Measure'), string='Quantità Totale',
            store={
                   'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines','state'], 10),
                   'stock.move': (_get_move_picking, ['product_uom_qty','picking_id'], 10),
            }),    
    }

    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        if not context:
            context = {}

        pick_data = self.browse(cr,uid,picking[0],context=context)
        sd_list = []
        keys = {}
        sd_str = ''


        for move in pick_data.move_lines:
            
            key = (move.location_id.id, move.location_dest_id.id, move.picking_type_id.id or move.picking_id.picking_type_id.id)
            if key not in keys:
                keys[key] = []
            keys[key].append(move.id)
            
            if move.reservation_product_ids:
                for res in move.reservation_product_ids:
                    if res.reservation_id.state == 'draft':
                        sd_list.append(res.product_id.name+ ' - '+res.reservation_id.color.description + ' (' + res.reservation_id.color.name + ')')
        
        if sd_list:                         #Se ci sono righe che si riferiscono ad almeno un S&D ancora aperto
            sd_list = list(set(sd_list))
            for el in sd_list:
                sd_str = sd_str + '\n' + el + ';'        
            raise osv.except_osv(_('User Error!'), _('You cannot transfer selected picking because its movements still are being processed in some document. In particular, the products still in process are:%s') % sd_str)            
        else:                  
            if len(keys) > 1:
                base = False
                new_pickings = picking
                mov_obj = self.pool.get('stock.move')
                for key in keys:
                    if not base and key[2] == pick_data.picking_type_id.id:
                        base = True
                        continue
                    new_pick = self.copy(cr,uid,pick_data.id,{'picking_type_id':key[2], 'move_lines': [], 'pack_operation_ids': [],})
                    mov_obj.write(cr,uid,keys[key],{'picking_id':new_pick},context=context)
                    new_pickings.append(new_pick)
                
                mod_obj = self.pool.get('ir.model.data')
                result = mod_obj.get_object_reference(cr, uid,
                                                      'stock',
                                                      'vpicktree')
                view_id = result and result[1] or False
                
                ctx = {}
                if 'lang' in context and context['lang']:
                    ctx['lang'] = context['lang']
                if 'tz' in context and context['tz']:
                    ctx['tz'] = context['tz']
                if 'uid' in context and context['uid']:
                    ctx['uid'] = context['uid']
                ctx['new_pickings'] = new_pickings
                
                return {'domain': "[('id','in', ["+','.join(map(str,new_pickings))+"])]",
                        'name': _("Picking"),
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'stock.picking',
                        'type': 'ir.actions.act_window',
                        'context': ctx,
                        'views': [(view_id,'tree'),(False,'form')],
                        }
            else:
                res = super(stock_picking,self).do_enter_transfer_details(cr, uid, picking, context=context)
                return res
                
    def onchange_ddt_references(self, cr, uid, ids, partner_id, supplier_ddt_number, supplier_ddt_date, picking_type_id, context=None):
    
        if not supplier_ddt_number or not supplier_ddt_date or not partner_id or not picking_type_id:
            return {}
        
        if picking_type_id and self.pool.get('stock.picking.type').browse(cr, uid, picking_type_id,context=context).code != 'incoming':
            return {}

        
        res_ids = self.search(cr, uid, [('supplier_ddt_number','=',supplier_ddt_number),('supplier_ddt_date','=',supplier_ddt_date),('partner_id','=',partner_id),('id','not in',ids)])
        if res_ids and len(res_ids) > 0:

            warning = {
                       'title': _('Warning!'),
                       'message': _('Esiste già un picking riferito allo stesso fornitore, con lo stesso DDT e la stessa data DDT.' )
                       }
            return {'value': {},
                    'warning': warning
                     }            

        return {}  

    def action_align_picking(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'     
        mov_obj = self.pool.get('stock.move')
        ops_obj = self.pool.get('stock.pack.operation')  
        picking_obj = self.browse(cr,uid,ids,context=context)[0]
        if picking_obj.state != 'done':
            for move in picking_obj.move_lines:
                mov_obj.do_unreserve(cr, uid, move.id,context=context)              
                mov_obj.write(cr, uid, move.id, {'location_dest_id': picking_obj.picking_type_id.default_location_dest_id.id, 'location_id': picking_obj.picking_type_id.default_location_src_id.id, 'picking_type_id':picking_obj.picking_type_id.id}, context=context)
            if picking_obj.pack_operation_ids:
                ops_obj.unlink(cr, uid, picking_obj.pack_operation_ids.ids, context=context)
        return