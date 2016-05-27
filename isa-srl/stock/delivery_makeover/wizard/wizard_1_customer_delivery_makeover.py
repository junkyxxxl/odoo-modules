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


class wizard_customer_delivery_makeover(orm.TransientModel):
    _name = 'wizard.customer.delivery.makeover'
    _description = 'Wizard Customer Delivery Makeover'

    _columns = {
        'customer_id': fields.many2one('res.partner',
                                   'Customer'),
        'delivery_date': fields.date('Delivery Date'),
        'company_id':fields.many2one('res.company','Company'),
    }

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(
                                                    cr, uid, 'account.account', context=c),
    }
    
    def get_customer_selection_total_pages(self, cr, uid, customer_ids, t_limit):
        res_partner_obj = self.pool.get('res.partner')
        list_customer = res_partner_obj.search(cr, uid, [('id', 'in', customer_ids)],
                                              order='id')
        if(not list_customer):
            t_total_pages = 1
        else:
            t_total_pages = int(len(list_customer) / t_limit)
            if(len(list_customer) % t_limit) > 0:
                t_total_pages += 1
                
        return t_total_pages

    def _check_customer_order_lines(self, cr, uid, context=None):
        
        res_partner_obj = self.pool.get('res.partner')
        sale_order_line_obj = self.pool.get('sale.order.line')
        sale_order_obj = self.pool.get('sale.order')
        wizard_obj = self.pool.get('wizard.customer.delivery.selection')

        t_lines = []
        order_line_ids = []
        customer_ids = []
        t_limit = 50
        t_delivery_date = context.get('default_delivery_date', None)
        t_company_id = context.get('default_company_id', None)
        
        t_base_filter = [('delivery_selection_state', '!=', 'R'), ('state', '=', 'confirmed'),
                         ('order_id.partner_id.customer', '=', True)]
        if(t_delivery_date):
            f = ('delivery_date', '<=', t_delivery_date)
            t_base_filter.append(f)
        if(t_company_id):
            f = ('company_id', '=', t_company_id)
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
        
        t_total_pages = self.get_customer_selection_total_pages(cr, uid, customer_ids, t_limit)
        
        new_customer_selection = {
                                  'delivery_date': t_delivery_date,
                                  'total_pages': t_total_pages
                                  }
        res_id = wizard_obj.create(cr, uid, new_customer_selection, context=context)
        
        list_customer = res_partner_obj.search(cr, uid, [('id', 'in', customer_ids)],
                                              order='id',
                                              limit=t_limit,
                                              offset=0)
        
        for t_customer_id in list_customer:
            t_customer = res_partner_obj.browse(cr, uid, t_customer_id)
            t_lines.append((0, 0, {
                                    'customer_id': t_customer_id,
                                    'city': str(t_customer.city) + ' [' + str(t_customer.province.name) + ']',
                                    'selection_id': int(res_id)
                                    }))
        
        wizard_obj.write(cr, uid, [res_id], {'line_ids': t_lines, })
        
        return res_id
    
    def get_order_lines_total_pages(self, cr, uid, t_filter, t_limit):
        
        sale_order_line_obj = self.pool.get('sale.order.line')
        
        sale_order_line_ids = sale_order_line_obj.search(cr, uid, t_filter,
                                                         order='id')
        if(not sale_order_line_ids):
            t_total_pages = 1
        else:
            t_total_pages = int(len(sale_order_line_ids) / t_limit)
            if(len(sale_order_line_ids) % t_limit) > 0:
                t_total_pages += 1
                
        return t_total_pages
    
    
    def set_order_lines(self, cr, uid, context=None):
        
        wizard_obj = self.pool.get('wizard.order.delivery.specification')
        sale_order_line_obj = self.pool.get('sale.order.line')

        t_lines = []
        t_limit = 50
        
        t_delivery_date = context.get('default_delivery_date', None)
        t_customer_id = context.get('default_customer_id', None)
        t_company_id = context.get('default_company_id', None)
        
        c_filter = [('delivery_selection_state', '!=', 'R'),
                    ('order_id.partner_id', '=', t_customer_id),
                    ('company_id','=',t_company_id),
                    ('state', '=', 'confirmed'),
                    ('delivery_selection_state', '=', 'C')]
        if(t_delivery_date):
            f = ('delivery_date', '<=', t_delivery_date)
            c_filter.append(f)
        
        t_total_pages = self.get_order_lines_total_pages(cr, uid, c_filter, t_limit)
        
        new_order = {
                     'delivery_date': t_delivery_date,
                     'customer_id': t_customer_id,
                     'company_id':t_company_id,
                     'total_pages': t_total_pages
                    }
        
        res_id = wizard_obj.create(cr, uid, new_order, context=context)
        
        sale_order_line_ids = sale_order_line_obj.search(cr, uid, c_filter,
                                                         order='id',
                                                         limit=t_limit,
                                                         offset=0,)
       
        if sale_order_line_ids:
            for line in sale_order_line_obj.browse(cr, uid, sale_order_line_ids):
                t_lines.append((0, 0, {
                                        'customer_id': t_customer_id,
                                        'company_id':t_company_id,
                                        'order_delivery_id': int(res_id),
                                        'order_line_id': line.id,
                                        'delivery_selection_state': line.delivery_selection_state,
                                        'product_id': line.product_id.id
                                        }))
    
        wizard_obj.write(cr, uid, [res_id], {'confirmed_ids': t_lines, })
        
        s_filter = [('delivery_selection_state', '!=', 'R'),
                    ('order_id.partner_id', '=', t_customer_id),
                    ('state', '=', 'confirmed'),
                    ('delivery_selection_state', '=', 'S'),
                    ('company_id','=',t_company_id)]
        
        sale_order_line_selected_ids = sale_order_line_obj.search(cr, uid, s_filter,
                                                         order='id')
        t_lines = []
        if sale_order_line_selected_ids:
            for line in sale_order_line_obj.browse(cr, uid, sale_order_line_selected_ids):
                t_lines.append((0, 0, {
                                        'customer_id': t_customer_id,
                                        'company_id':t_company_id,
                                        'order_delivery_id': int(res_id),
                                        'order_line_id': line.id,
                                        'delivery_selection_state': line.delivery_selection_state,
                                        'product_id': line.product_id.id
                                        }))
        wizard_obj.write(cr, uid, [res_id], {'selected_ids': t_lines, })
        return res_id
    
    
    def view_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = None
        t_customer_id = None   
        form = self.read(cr, uid, ids)[0]
        if(form["customer_id"]):
            t_customer_id = form["customer_id"][0]
        t_delivery_date = form["delivery_date"]
        t_company_id = form["company_id"][0]
        
        context.update({
            'default_delivery_date': t_delivery_date,
            'default_customer_id': t_customer_id,
            'default_company_id':t_company_id,
        })
        
        if(not t_customer_id):
            res = self.customer_selection(cr, uid, context)
        else:
            res = self.customer_order_specification(cr, uid, context)
            
        return res
    
    def customer_selection(self, cr, uid, context):
        res_id = self._check_customer_order_lines(cr, uid, context)

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
              'res_id': res_id,
              'view_id': view_id,
              'target': 'inlineview',
              }

    def customer_order_specification(self, cr, uid, context):
        res_id = self.set_order_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'wizard_order_delivery_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Customer Order Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.order.delivery.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'target': 'inlineview',
              }

