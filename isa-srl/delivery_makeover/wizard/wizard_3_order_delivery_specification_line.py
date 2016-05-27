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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class wizard_order_delivery_specification_line(orm.TransientModel):
    _name = 'wizard.order.delivery.specification.line'
    _description = 'Wizard Customer Order Specification Line'
    
    def _get_packages_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        t_pckg = 0
        sale_order_line_obj = self.pool.get('sale.order.line')
        for line in self.browse(cr, uid, ids, context):
            t_pckg = 0
            t_sale_line = sale_order_line_obj.browse(cr, uid, line.order_line_id.id)
            if(t_sale_line.product_packaging and t_sale_line.product_packaging.id and t_sale_line.product_packaging.qty > 0):
                t_quantity = t_sale_line.product_uom_qty
                t_conf_qty = t_sale_line.product_packaging.qty
                t_pckg = int(t_quantity / t_conf_qty)
                if ((t_quantity % t_conf_qty) > 0):
                    t_pckg += 1
            res[line.id] = t_pckg
        return res

    _columns = {
        'customer_id': fields.many2one('res.partner', 'Customer', select=1),
        'delivery_selection_state': fields.selection([
                                                      ('C', 'Confirmed'),
                                                      ('S', 'Selected')], 'Delivery State'),
        'order_delivery_id': fields.many2one('wizard.order.delivery.specification',
                                         'Customer Order Specification',
                                         ondelete="cascade",
                                         required=True),
        'product_id': fields.many2one('product.product', 'Product', select=1),
        'delivery_date': fields.related('order_line_id',
                                        'delivery_date',
                                        type='date',
                                        string='Delivery Date', readonly=1),
        'weight': fields.related('order_line_id',
                                'th_weight',
                                type='float',
                                string='Weight', readonly=1),
        'product_uom': fields.related('order_line_id',
                                      'product_uom',
                                      'name',
                                      type='char',
                                      string='Product UoM'),
        'product_uom_qty': fields.related('order_line_id',
                                        'product_uom_qty',
                                        type='integer',
                                        string='Quantity', readonly=1),
        'description': fields.related('order_line_id',
                                        'name',
                                        type='text',
                                        string='Product Description',
                                        readonly=1),
        'order_number': fields.related('order_line_id',
                                        'order_id',
                                        'name',
                                        type='char',
                                        string='Order Number', readonly=1),
        'order_line_id': fields.many2one('sale.order.line', 'Order Line'),
        'packages_qty': fields.function(_get_packages_qty,
                                   readonly=True,
                                   type="integer",
                                   string="Nr. Colli"),
    }
    
    def _set_order_lines(self, cr, uid, context=None):
        
        wizard_spec_obj = self.pool.get('wizard.order.delivery.specification')
        wizard_del_make_obj = self.pool.get('wizard.customer.delivery.makeover')
        sale_order_line_obj = self.pool.get('sale.order.line')
        
        t_lines = []
        t_limit = 50
        
        t_delivery_date = context.get('default_delivery_date', None)
        t_customer_id = context.get('default_customer_id', None)
        t_page = context.get('default_actual_page', None)
        
        c_filter = [('delivery_selection_state', '!=', 'R'),
                    ('order_id.partner_id', '=', t_customer_id),
                    ('state', '=', 'confirmed'),
                    ('delivery_selection_state', '=', 'C')]
        
        if(t_delivery_date):
            f = ('delivery_date', '<=', t_delivery_date)
            c_filter.append(f)
            
        t_total_pages = wizard_del_make_obj.get_order_lines_total_pages(cr, uid, c_filter, t_limit)
        
        if(t_page > t_total_pages or t_total_pages == 1):
            t_page = t_total_pages
            context.update({
                            'default_actual_page': t_page,
                           })
        
        t_offset = t_limit * (t_page - 1)
        
        new_order = {
                     'delivery_date': t_delivery_date,
                     'customer_id': t_customer_id,
                     'total_pages': t_total_pages
                    }
        
        res_id = wizard_spec_obj.create(cr, uid, new_order, context=context)
        
        sale_order_line_ids = sale_order_line_obj.search(cr, uid, c_filter,
                                                         order='id',
                                                         limit=t_limit,
                                                         offset=t_offset)
       
        if sale_order_line_ids:
            for line in sale_order_line_obj.browse(cr, uid, sale_order_line_ids):
                t_lines.append((0, 0, {
                                        'customer_id': t_customer_id,
                                        'order_delivery_id': int(res_id),
                                        'order_line_id': line.id,
                                        'delivery_selection_state': line.delivery_selection_state,
                                        'product_id': line.product_id.id
                                        }))
    
        wizard_spec_obj.write(cr, uid, [res_id], {'confirmed_ids': t_lines, })
        
        s_filter = [('delivery_selection_state', '!=', 'R'),
                    ('order_id.partner_id', '=', t_customer_id),
                    ('state', '=', 'confirmed'),
                    ('delivery_selection_state', '=', 'S')]
        
        sale_order_line_selected_ids = sale_order_line_obj.search(cr, uid, s_filter,
                                                         order='id')
        t_lines = []
        if sale_order_line_selected_ids:
            for line in sale_order_line_obj.browse(cr, uid, sale_order_line_selected_ids):
                t_lines.append((0, 0, {
                                        'customer_id': t_customer_id,
                                        'order_delivery_id': int(res_id),
                                        'order_line_id': line.id,
                                        'delivery_selection_state': line.delivery_selection_state,
                                        'product_id': line.product_id.id
                                        }))
        wizard_spec_obj.write(cr, uid, [res_id], {'selected_ids': t_lines, })
        return res_id
   
  
    def move_draft(self, fb, cr, uid, ids, context=None):
        if context is None:
            context = {}

        line_id = context.get('line_id', None)
        data = self.browse(cr, uid, line_id, context=context)
        t_delivery_date = data.order_delivery_id.delivery_date
        t_customer_id = data.order_delivery_id.customer_id.id
        t_uom_selection = data.order_delivery_id.uom_selection
        t_page = data.order_delivery_id.actual_page
        t_state = 'C'
        if fb:
            t_state = 'S'
            
        sale_order_line_obj = self.pool.get('sale.order.line')
        t_sale_line_id = data.order_line_id.id
        sale_order_line_obj.write(cr, uid, [t_sale_line_id], {
            'delivery_selection_state': t_state,
        })
      
        context.update({
            'default_customer_id': t_customer_id,
            'default_delivery_date': t_delivery_date,
            'default_uom_selection': t_uom_selection,
            'default_actual_page': t_page,
        })

        res_id = self._set_order_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'wizard_order_delivery_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Wizard Customer Order Delivery Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.order.delivery.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }

    def move_draft_forward(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.move_draft(1, cr, uid, ids, context)

    def move_draft_backward(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.move_draft(0, cr, uid, ids, context)

    
