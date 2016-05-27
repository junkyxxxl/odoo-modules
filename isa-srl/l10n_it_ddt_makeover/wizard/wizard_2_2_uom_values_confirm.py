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


class wizard_uom_values_confirm(orm.TransientModel):
    _name = 'wizard.uom.values.confirm'
    _description = 'Wizard Unit of Measure Confirm Values'
    
    _columns = {
                'uom_selection': fields.selection([('C', 'Colli'),
                                                  ('K', 'Kg'),
                                                  ('P', 'Uom del Prodotto')],
                                                 'Quantity for'),
                'delivery_date': fields.date('Delivery Date'),
                }
    
    def confirm_customer_selection(self, cr, uid, ids, context=None):
        
        customer_sel_obj = self.pool.get('wizard.customer.delivery.selection')
        form = self.read(cr, uid, ids)[0]
        t_uom_selection = form["uom_selection"]
        t_wizard = context.get('wizard_id', None)
        customer_sel_obj.write(cr, uid, [t_wizard], {
                                                     'uom_selection': t_uom_selection
                                                     })
         
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'wizard_customer_delivery_selection_view')
        view_id = result and result[1] or False

        return {
              'name': _("Customer Selection"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.customer.delivery.selection',
              'type': 'ir.actions.act_window',
              'res_id': t_wizard,
              'view_id': view_id,
              'target': 'inlineview',
              }
        
    def confirm_order_specification(self, cr, uid, ids, context=None):
        
        order_del_spec_obj = self.pool.get('wizard.order.delivery.specification')
        form = self.read(cr, uid, ids)[0]
        t_uom_selection = form["uom_selection"]
        t_wizard = context.get('wizard_id', None)
        order_del_spec_obj.write(cr, uid, [t_wizard], {
                                                     'uom_selection': t_uom_selection
                                                     })
         
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'wizard_order_delivery_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Customer Selection"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.order.delivery.specification',
              'type': 'ir.actions.act_window',
              'res_id': t_wizard,
              'view_id': view_id,
              'target': 'inlineview',
              }
        
    def confirm(self, cr, uid, ids, context=None):
        
        t_flag = context.get('customer_selection')
        if(t_flag):
            result = self.confirm_customer_selection(cr, uid, ids, context)
        else:
            result = self.confirm_order_specification(cr, uid, ids, context)
    
        return result
    
