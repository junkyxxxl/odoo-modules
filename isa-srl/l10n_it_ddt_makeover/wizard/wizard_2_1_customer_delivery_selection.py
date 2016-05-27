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


class wizard_customer_delivery_selection(orm.TransientModel):
    _name = 'wizard.customer.delivery.selection'
    _description = 'Wizard Customer Delivery Selection'

    def _resume_page(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_wizard in self.browse(cr, uid, ids, context):
            t_actual = str(t_wizard.actual_page)
            t_total = str(t_wizard.total_pages)
            res[t_wizard.id] = t_actual + ' di ' + t_total
        return res
    
    def _is_last_page(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_wizard in self.browse(cr, uid, ids, context):
            t_actual = t_wizard.actual_page
            t_total = t_wizard.total_pages
            if t_actual == t_total:
                res[t_wizard.id] = True
            else:
                res[t_wizard.id] = False
        return res
   
    _columns = {
        'delivery_date': fields.date('Delivery Date'),
        'uom_selection': fields.selection([('C', 'Colli'),
                                                  ('K', 'Kg'),
                                                  ('P', 'Uom del Prodotto')],
                                                 'Quantity for'),
        'line_ids': fields.one2many(
                              'wizard.customer.delivery.selection.line',
                              'selection_id',
                              string="Lines",
                              readonly=True),
        'actual_page': fields.integer('Actual Page'),
        'total_pages': fields.integer('Total Pages'),
        'pages_resume': fields.function(_resume_page,
                                  string='Page',
                                  type='text'),
        'is_last_page': fields.function(_is_last_page,
                                  string='Is Last Page',
                                  type='boolean'),
    }
    
    _defaults = {
                 'actual_page': 1
                 }
    def view_new_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'wizard_action_customer_delivery_makeover_view')
        view_id = result and result[1] or False

        return {
              'name': _("Customer Delivery Makeover"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.customer.delivery.makeover',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'target': 'new',
              }
    
    def set_uom_confirm_values(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'wizard_uom_values_confirm_view')
        
        t_cp = self.browse(cr, uid, ids[0])
        context.update({
            'default_delivery_date': t_cp.delivery_date,
        })
        view_id = result and result[1] or False

        return {
              'name': _("Set UoM Confirm Values"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.uom.values.confirm',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'target': 'new',
              }
        
    def _check_customer_order_lines(self, cr, uid, context=None):
        
        res_partner_obj = self.pool.get('res.partner')
        sale_order_line_obj = self.pool.get('sale.order.line')
        sale_order_obj = self.pool.get('sale.order')
        wizard_obj = self.pool.get('wizard.customer.delivery.selection')
        wizard_del_sel_obj = self.pool.get('wizard.customer.delivery.makeover')

        t_lines = []
        order_line_ids = []
        customer_ids = []
        t_limit = 50
        
        t_delivery_date = context.get('default_delivery_date', None)
        t_uom_selection = context.get('default_uom_selection', None)
        t_page = context.get('default_actual_page', None)
        
        
        t_base_filter = [('delivery_selection_state', '!=', 'R'), ('state', '=', 'confirmed'),
                         ('order_id.partner_id.customer', '=', True)]
        if(t_delivery_date):
            f = ('delivery_date', '<=', t_delivery_date)
            t_base_filter.append(f)
        
        sale_order_line_ids = sale_order_line_obj.search(cr, uid, t_base_filter)
        order_line_dict = sale_order_line_obj.read(cr, uid, sale_order_line_ids,
                                                   ['order_id'])
        for t_dict in order_line_dict:
            order_line_ids.append(t_dict['order_id'][0])
            
        customer_dict = sale_order_obj.read(cr, uid, order_line_ids,
                                                   ['partner_id'])
        
        for t_dict in customer_dict:
            customer_ids.append(t_dict['partner_id'][0])
        
        t_total_pages = wizard_del_sel_obj.get_customer_selection_total_pages(cr, uid, customer_ids, t_limit)
        
        if(t_page > t_total_pages or t_total_pages == 1):
            t_page = t_total_pages
            context.update({
                            'default_actual_page': t_page,
                           })
        
        t_offset = t_limit * (t_page - 1)
        
        new_customer_selection = {
                                  'delivery_date': t_delivery_date,
                                  'uom_selection': t_uom_selection,
                                  'total_pages': t_total_pages
                                  }
        res_id = wizard_obj.create(cr, uid, new_customer_selection, context=context)
        
        
        list_customer = res_partner_obj.search(cr, uid, [('id', 'in', customer_ids)],
                                              order='id',
                                              limit=t_limit,
                                              offset=t_offset)
        
        for t_customer_id in list_customer:
            t_customer = res_partner_obj.browse(cr, uid, t_customer_id)
            t_lines.append((0, 0, {
                                    'customer_id': t_customer_id,
                                    'city': str(t_customer.city) + ' [' + str(t_customer.province.name) + ']',
                                    'selection_id': int(res_id)
                                    }))
        
        wizard_obj.write(cr, uid, [res_id], {'line_ids': t_lines, })
        
        return res_id
    
    def move_page(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context=context)
        t_delivery_date = data.delivery_date or None
        t_uom_selection = data.uom_selection or None
        t_total_pages = data.total_pages
        
        t_skip = context.get('t_skip', None)
        if(data.actual_page==1 and t_skip==-1):
            raise orm.except_orm(_('Error!'), _('Non puoi andare indietro!'))
            
        if(data.actual_page >= t_total_pages and t_skip == 1):
            raise orm.except_orm(_('Error!'), _("Hai raggiunto l'ultima pagina!"))

        t_page = data.actual_page + t_skip
        
        context.update({
            'default_delivery_date': t_delivery_date,
            'default_uom_selection': t_uom_selection,
            'default_actual_page': t_page,
            'default_total_pages': t_total_pages
        })

        res_id = self._check_customer_order_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'wizard_customer_delivery_selection_view')
        view_id = result and result[1] or False

        return {
              'name': _("Wizard Customer Selection"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.customer.delivery.selection',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }

