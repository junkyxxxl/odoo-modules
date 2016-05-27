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

class wizard_create_picking_from_quants(osv.osv_memory):
    _name = "wizard.create.picking.from.quants"
    _description = "Create Picking From Quants"

    @api.model
    def _get_domain(self):
        if self._ids or self.quant_ids or ('active_ids' in self._context and self._context['active_ids']):
            tmp_ids = self._ids or self.quant_ids.ids or self._context['active_ids']
            res = self.pool.get('stock.quant').browse(self._cr, self._uid, tmp_ids[0], context=self._context).location_id.id
            domain=[('default_location_src_id','=', res)]
            return domain
        return [('id','>',0)]

    _columns = {
        'quant_ids': fields.many2many('stock.quant', string='Quants'),
        'partner_id': fields.many2one('res.partner','Partner'),
        'picking_type_id': fields.many2one('stock.picking.type','Picking Type',domain=_get_domain),
        'company_id': fields.many2one('res.company','Company')
    }

    def _get_partner(self, cr, uid, context = None):
        if not context or 'active_ids' not in context or not context['active_ids']:
            return 
        tmp_loc = self.pool.get('stock.quant').browse(cr,uid,context['active_ids'][0],context=context).location_id
        if tmp_loc and tmp_loc.partner_id:
            return tmp_loc.partner_id.id
    
    def _get_ids(self, cr, uid, context = None):
        if not context or 'active_ids' not in context or not context['active_ids']:
            return 
        quant_obj = self.pool.get('stock.quant')
        def_location = quant_obj.browse(cr, uid, context['active_ids'][0], context=context).location_id
        def_company = quant_obj.browse(cr, uid, context['active_ids'][0], context=context).company_id
        for id in context['active_ids']:
            if quant_obj.browse(cr, uid, id, context=context).location_id != def_location:
                raise osv.except_osv(_('Error!'), _('All the selected quants should have the same location'))                
            if quant_obj.browse(cr, uid, id, context=context).company_id != def_company:
                raise osv.except_osv(_('Error!'), _('All the selected quants should belong to the same company'))                            
        return context['active_ids'] 
    
    _defaults = {
        'partner_id': _get_partner,
        'quant_ids': _get_ids,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, context=c),
    }

    def create_picking(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids)[0]
        quant_obj = self.pool.get('stock.quant')
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        
        # CREA PICKING
        
        pick_vals= {
                    'partner_id':wiz.partner_id.id,
                    'move_type':'one',
                    'invoice_state':'none',
                    'picking_type_id':wiz.picking_type_id.id,
                    'company_id':wiz.company_id.id,
                    'priority':'1',
        }
        
        pick_id = pick_obj.create(cr, uid, pick_vals, context=context)
                
        for quant in wiz.quant_ids:
            # CREA MOVIMENTO
            
            move_vals= {
                        'picking_id': pick_id,
                        'product_id': quant.product_id.id,
                        'product_uom': quant.product_id.uom_id.id,
                        'product_uom_qty': quant.qty,
                        'name': quant.product_id.name,
                        'picking_type_id': wiz.picking_type_id.id,
                        'invoice_state': 'none',
                        'priority': '1',
                        'company_id': wiz.company_id.id,
                        'location_id': wiz.picking_type_id.default_location_src_id.id,
                        'location_dest_id': wiz.picking_type_id.default_location_dest_id.id,
                        'restrict_lot_id': quant.lot_id.id
            }
            
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            quant_obj.quants_reserve(cr, uid, [(quant,quant.qty)], move_obj.browse(cr, uid, move_id, context=context), context=context) 
        pick_obj.action_confirm(cr, uid, pick_id, context=context)

        ctx = {}
        for item in context.items():
            ctx[item[0]] = item[1]
        ctx.update({'active_ids':[pick_id], 'active_model':'stock.picking'})
        created_id = self.pool['stock.transfer_details'].create(cr, uid, {'picking_id': pick_id or False}, context=ctx)
        return self.pool['stock.transfer_details'].do_detailed_transfer(cr,uid,created_id,context=context)        

        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
