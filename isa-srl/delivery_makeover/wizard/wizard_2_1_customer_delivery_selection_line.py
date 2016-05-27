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
from datetime import datetime
from openerp.tools.translate import _


class wizard_customer_delivery_selection_line(orm.TransientModel):
    _name = 'wizard.customer.delivery.selection.line'
    _description = 'Wizard Customer Delivery Selection Line'
    
    def _get_expired(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        t_today = str(datetime.now())[:10]
        sale_order_line_obj = self.pool.get('sale.order.line')
        for line in self.browse(cr, uid, ids, context):
            t_base_filter = [('delivery_selection_state', '!=', 'R'), 
                             ('state', '=', 'confirmed'),
                             ('delivery_date', '<', t_today),
                             ('order_id.partner_id', '=', line.customer_id.id)]
            sale_order_line_ids = sale_order_line_obj.search(cr, uid, t_base_filter)
            res[line.id] = len(sale_order_line_ids)
        return res
    
    def _get_expiring_today(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        t_today = str(datetime.now())[:10]
        sale_order_line_obj = self.pool.get('sale.order.line')
        for line in self.browse(cr, uid, ids, context):
            t_base_filter = [('delivery_selection_state', '!=', 'R'),
                             ('state', '=', 'confirmed'),
                             ('delivery_date', '=', t_today),
                             ('order_id.partner_id', '=', line.customer_id.id)]
            sale_order_line_ids = sale_order_line_obj.search(cr, uid, t_base_filter)
            res[line.id] = len(sale_order_line_ids)
        return res
    
    def _get_not_expired(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        t_today = str(datetime.now())[:10]
        sale_order_line_obj = self.pool.get('sale.order.line')
        for line in self.browse(cr, uid, ids, context):
            t_base_filter = [('delivery_selection_state', '!=', 'R'),
                             ('state', '=', 'confirmed'),
                             ('delivery_date', '>', t_today),
                             ('order_id.partner_id', '=', line.customer_id.id)]
            sale_order_line_ids = sale_order_line_obj.search(cr, uid, t_base_filter)
            res[line.id] = len(sale_order_line_ids)
        return res

    _columns = {
        'customer_id': fields.many2one('res.partner',
                                       'Customer',
                                       select=1),
        'selection_id': fields.many2one('wizard.customer.delivery.selection',
                                        'Selection'),
        'city': fields.text('City & Province'),
        'expired': fields.function(_get_expired,
                                   readonly=True,
                                   type="integer",
                                   string="Expired"),
        'expiring_today': fields.function(_get_expiring_today,
                                   readonly=True,
                                   type="integer",
                                   string="Expiring"),
        'not_expired': fields.function(_get_not_expired,
                                   readonly=True,
                                   type="integer",
                                   string="Not Expired"),
        }
       
    def select_customer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        line_id = context.get('line_id', None)
        wizard_obj = self.pool.get('wizard.customer.delivery.makeover')
        
        data = self.browse(cr, uid, line_id, context=context)
        t_delivery_date = data.selection_id.delivery_date or None
        t_customer_id = data.customer_id.id
        t_uom_selection = data.selection_id.uom_selection
            
        context.update({
            'default_customer_id': t_customer_id,
            'default_delivery_date': t_delivery_date,
            'default_uom_selection': t_uom_selection,
        })
        
        
        res_id = wizard_obj.set_order_lines(cr, uid, context)

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

