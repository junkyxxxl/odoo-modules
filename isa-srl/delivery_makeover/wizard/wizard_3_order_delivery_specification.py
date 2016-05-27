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


class wizard_order_delivery_specification(orm.TransientModel):
    _name = 'wizard.order.delivery.specification'
    _description = 'Wizard Order Delivery Specification'

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
        'customer_id': fields.many2one('res.partner',
                                   'customer'),
        'delivery_date': fields.date('Delivery Date'),
        'uom_selection': fields.selection([('C', 'Colli'),
                                                  ('K', 'Kg'),
                                                  ('P', 'Uom del Prodotto')],
                                                 'Quantity for'),
        'confirmed_ids': fields.one2many(
                              'wizard.order.delivery.specification.line',
                              'order_delivery_id',
                              domain=[('delivery_selection_state', '=', 'C')],
                              string="Confirmed",
                              readonly=True),
        'selected_ids': fields.one2many(
                              'wizard.order.delivery.specification.line',
                              'order_delivery_id',
                              domain=[('delivery_selection_state', '=', 'S')],
                              string="Selected",
                              readonly=True),
        'actual_page': fields.integer('Actual Page'),
        'total_pages': fields.integer('Total Pages'),
        'pages_resume': fields.function(_resume_page,
                                  string='Page',
                                  type='text'),
        'is_last_page': fields.function(_is_last_page,
                                  string='Is Last Page',
                                  type='boolean'),
        'company_id':fields.many2one('res.company','Company'),
    }
    
    _defaults = {
                 'actual_page': 1
                 }
    
    def action_move_all_forward(self, cr, uid, ids, context=None):
        res = None
        t_spec = self.browse(cr, uid, ids[0])
        line_obj = self.pool.get('wizard.order.delivery.specification.line')
        for line in t_spec.confirmed_ids:
            context.update({
                            'line_id': line.id
                            })
            res = line_obj.move_draft_forward(cr, uid, ids, context=context)
        return res
    
    def action_move_all_backward(self, cr, uid, ids, context=None):
        res = None
        t_spec = self.browse(cr, uid, ids[0])
        line_obj = self.pool.get('wizard.order.delivery.specification.line')
        for line in t_spec.selected_ids:
            context.update({
                            'line_id': line.id
                            })
            res = line_obj.move_draft_backward(cr, uid, ids, context=context)
        return res
    
    def create_stock_picking(self, cr, uid, ids, context=None):
        t_lines = []
        sale_lines = []
        t_wizard = self.browse(cr, uid, ids[0])
        stock_picking_obj = self.pool.get('stock.picking')
        stock_picking_type_obj = self.pool.get('stock.picking.type')
        terms_obj = self.pool.get('stock.picking.delivery.terms')
        location_obj = self.pool.get('stock.location')
        sale_order_line_obj = self.pool.get('sale.order.line')
        selected_lines_obj = self.pool.get('wizard.order.delivery.specification.line')
        # TODO
        cause_ids = stock_picking_type_obj.search(cr, uid, [('code', '=', 'outgoing')])
        if not cause_ids:
            raise orm.except_orm(_('Error!'),
                                 _('Non esiste alcuna causale di Uscita.'))
        cause_id = cause_ids[0]
        
        terms_ids = terms_obj.search(cr, uid, [('name', '=', 'Consegna al luogo di destinazione')])
        if not terms_ids:
            raise orm.except_orm(_('Error!'),
                                 _('Non esiste Condizione di consegna.'))
        terms_id = terms_ids[0]
        
        loc_ids = location_obj.search(cr, uid, [('name', '=', 'Stock')])
        if not loc_ids:
            raise orm.except_orm(_('Error!'),
                                 _('Non esiste luogo di stoccaggio.'))
        loc_id = loc_ids[0]
        
        loc_dest_ids = location_obj.search(cr, uid, [('name', '=', 'Customers')])
        if not loc_dest_ids:
            raise orm.except_orm(_('Error!'),
                                  _('Non esiste luogo di stoccaggio clienti.'))
        loc_dest_id = loc_dest_ids[0]
        
        new_picking = {
                       'partner_id': t_wizard.customer_id.id,
                       'picking_type_id': cause_id,
                       'company_id': t_wizard.company_id.id,
                       'move_type': 'one',
                       }
        res_id = stock_picking_obj.create(cr, uid, new_picking)
        selected_lines_ids = selected_lines_obj.search(cr, uid, [('delivery_selection_state', '=', 'S'),
                                                                  ('order_delivery_id', '=', ids[0])],
                                                                  order='product_id')
        if not selected_lines_ids:
            raise orm.except_orm(_('Error!'), _('Selezionare almeno una riga se presente'))

        first_line = selected_lines_obj.browse(cr, uid, selected_lines_ids[0])
        last_line = selected_lines_obj.browse(cr, uid, selected_lines_ids[0])
        t_quantity = 0.0
        t_product = first_line.product_id.id
        t_date_string = None
        if last_line.delivery_date:
            t_date_string = last_line.delivery_date[:10] + ' 00:00:00'

        for line in selected_lines_obj.browse(cr, uid, selected_lines_ids):
            t_lp = line.product_id.id
            if(t_lp != t_product):
                t_date_string = last_line.delivery_date[:10] + ' 00:00:00'
                t_lines.append((0, 0, {
                                    'product_id': t_product,
                                    'product_uom_qty': t_quantity,
                                    'product_uom': last_line.order_line_id.product_uom.id,
                                    'name': last_line.description,
                                    'date_expected': t_date_string,
                                    'picking_id': int(res_id),
                                    'date': t_date_string,
                                    'location_id': loc_id,
                                    'location_dest_id': loc_dest_id
                                     }))
                t_quantity = 0.0

            t_quantity += line.product_uom_qty
            t_product = line.product_id.id
            last_line = line
            sale_lines.append(line.order_line_id.id)
        t_lines.append((0, 0, {
                                'product_id': t_product,
                                'product_uom_qty': t_quantity,
                                'product_uom': last_line.order_line_id.product_uom.id,
                                'name': last_line.description,
                                'date_expected': t_date_string,
                                'picking_id': int(res_id),
                                'date': t_date_string,
                                'location_id': loc_id,
                                'location_dest_id': loc_dest_id
                                }))

        sale_order_line_obj.write(cr, uid, sale_lines, {
                                                        'delivery_selection_state': 'R'
                                                        })
    
        stock_picking_obj.write(cr, uid, [res_id], {'move_lines': t_lines, })
        
        result = self.create_post_order(cr, uid, ids, res_id, context)
        return result
    
    def create_post_order(self, cr, uid, ids, stock_id, context):
        post_obj = self.pool.get('wizard.post.order.creation')
        res_id = post_obj.create(cr, uid, {
                                           'stock_picking_out_id': stock_id
                                           })
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'post_order_creation_view')
        view_id = result and result[1] or False

        return {
              'name': _("Wizard Customer Post Order Delivery Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.post.order.creation',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
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
        
    def move_page(self, cr, uid, ids, context=None):
        wizard_line_obj = self.pool.get('wizard.order.delivery.specification.line')
        data = self.browse(cr, uid, ids[0], context=context)
        t_delivery_date = data.delivery_date
        t_customer_id = data.customer_id.id
        t_uom_selection = data.uom_selection
        t_total_pages = data.total_pages
        
        t_skip = context.get('t_skip', None)
        if(data.actual_page==1 and t_skip==-1):
            raise orm.except_orm(_('Error!'), _('Non puoi andare indietro!'))
            
        if(data.actual_page >= t_total_pages and t_skip == 1):
            raise orm.except_orm(_('Error!'), _("Hai raggiunto l'ultima pagina!"))

        t_page = data.actual_page + t_skip
        
        context.update({
            'default_customer_id': t_customer_id,
            'default_delivery_date': t_delivery_date,
            'default_uom_selection': t_uom_selection,
            'default_actual_page': t_page,
            'default_total_pages': t_total_pages
        })

        res_id = wizard_line_obj._set_order_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'delivery_makeover',
                                              'wizard_order_delivery_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Wizard Delivery Order Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.order.delivery.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }

            
        
