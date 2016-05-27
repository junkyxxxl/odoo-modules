# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _


class wizard_stock_sheet(orm.TransientModel):
    _name = 'wizard.stock.sheet'
    _description = 'Print Stock Sheet Wizard'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True), 
        'product_id': fields.many2one('product.product',
                                      'Product',
                                      required=True),
        'warehouse_id': fields.many2one('stock.warehouse',
                                      'Warehouse'),
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
    }

    _defaults = { 
        'date_to': fields.date.context_today,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, context=c),        
    }

    def _check_date_range_validity(self, cr, uid, ids):
        form = self.read(cr, uid, ids)[0]
        t_date_from = form["date_from"]
        t_date_to = form["date_to"]

        if t_date_from > t_date_to:
            raise orm.except_orm(_('Error!'), _('Start period should precede then end period.'))

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = {'value': {}}
        warehouse_id = self._get_default_warehouse(cr, uid, company_id, context)
        if warehouse_id:
            res['value'].update({'warehouse_id': warehouse_id})
        else:
            res['value'].update({'warehouse_id': ''})         
        return res
    
    def _get_default_warehouse(self, cr, uid, company_id, context=None):
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id', '=', company_id)], context=context)
        if not warehouse_ids:
            return False
        return warehouse_ids[0]

    
    def _get_wizard_params(self, date_from, date_to, product_id, warehouse_id):
        filters = []
        if date_from :
            f = ("date", ">=", date_from)
            filters.append(f)
        if date_to :
            t = ("date", "<=", date_to)
            filters.append(t)
        if product_id :
            p = ("product_id", "=", product_id)
            filters.append(p)
        if warehouse_id :
            p = ("warehouse_id", "=", warehouse_id)
            filters.append(p)
        return filters
    
    def _get_initial_wizard_filters(self, date_from, product_id):
        filters = []
        if date_from :
            f = ("date", "<", date_from)
            filters.append(f)
        if product_id :
            p = ("product_id", "=", product_id)
            filters.append(p)
        
        return filters
    
    def _get_initial_quantity(self, cr, uid, context=None):
        stock_move_obj = self.pool.get('stock.move')
        stock_picking_obj = self.pool.get('stock.picking')

        start_quantity = 0.0

        t_date_from = context.get('default_date_from', None)
        t_date_from = t_date_from + ' 00:00:00'
        t_product_id = context.get('default_product_id', None)
        initial_filters = self._get_initial_wizard_filters(t_date_from, t_product_id)

        stock_move_ids = stock_move_obj.search(cr, uid, initial_filters)
        t_stock_move = stock_move_obj.browse(cr, uid, stock_move_ids)

        for line in t_stock_move:
            t_picking_id = line.picking_id.id
            t_picking = stock_picking_obj.browse(cr, uid, t_picking_id)
            if(t_picking):
                t_sign = ''
                if t_picking.picking_type_id:
                    t_causes = t_picking.picking_type_id
                    if t_causes:
                        t_sign = t_causes.code
                if(t_sign == 'outgoing'):
                    start_quantity -= float(line.product_qty)
                else:
                    start_quantity += float(line.product_qty)

        return start_quantity

    def _set_sheet_result_lines(self, cr, uid, context=None):
        t_date_from = context.get('default_date_from', None)
        t_date_to = context.get('default_date_to', None)
        t_product_id = context.get('default_product_id', None)
        t_warehouse_id = context.get('default_warehouse_id', None)
        
        initial_quantity = self._get_initial_quantity(cr, uid, context=context)
        final_quantity = initial_quantity
        line_filters = self._get_wizard_params(t_date_from, t_date_to, t_product_id, t_warehouse_id)
        
        stock_move_obj = self.pool.get('stock.move')
        t_stock_move_ids = stock_move_obj.search(cr, uid, line_filters, order='date')
        stock_picking_obj = self.pool.get('stock.picking')
        stock_picking_ddt_obj = self.pool.get('stock.picking.ddt')
        
        new_sheet = {'product_id': t_product_id,
                     'warehouse_id': t_warehouse_id,
                     'date_from': t_date_from,
                     'date_to': t_date_to,
                      }
        result_id = self.pool.get('wizard.stock.sheet.result').create(cr,
                                uid, new_sheet, context=context)
        
        t_lines = [(0, 0, {  'result_id': result_id,
                                 'date': t_date_from,
                                 'move_id': None,
                                 'document_number': '',
                                 'document_origin': _('Initial Quantity'),
                                 'partner_id': None,
                                 'unit_of_measure': '',
                                 'cause': '',
                                 'sign': '',
                                 'quantity': initial_quantity,
                                 'warehouse_id': t_warehouse_id,
                              })]

        for line in stock_move_obj.browse(cr, uid, t_stock_move_ids):

            t_ddt = ''
            t_picking_id = line.picking_id.id 
            t_picking = stock_picking_obj.browse(cr, uid, t_picking_id)
            if t_picking:
                t_ddt = 'stock'
                stock_picking_ddt_ids = stock_picking_ddt_obj.search(cr, uid,
                                                                     [('picking_id', '=', t_picking_id)],
                                                                     limit=1,
                                                                     context=context)
                if stock_picking_ddt_ids:
                    stock_picking_ddt_id = stock_picking_ddt_ids[0]
                    stock_picking_ddt_data = stock_picking_ddt_obj.browse(cr, uid, stock_picking_ddt_id)
                    if stock_picking_ddt_data.ddt_number:
                        t_ddt = stock_picking_ddt_data.ddt_number

                t_sign = ''
                t_causes_description = ''
                if t_picking.picking_type_id:
                    t_causes = t_picking.picking_type_id
                    if t_causes and t_causes.name:
                        t_causes_description = t_causes.name
                    if t_causes and t_causes.code:
                        t_sign = t_causes.code

                t_lines.append((0, 0, {  'result_id': result_id,
                                         'date': line.date,
                                         'move_id': line.id,
                                         'document_number': t_ddt,
                                         'document_origin': line.origin,
                                         'partner_id': t_picking.partner_id.id,
                                         'unit_of_measure': line.product_uom.name,
                                         'cause': t_causes_description,
                                         'sign': t_sign,
                                         'quantity': line.product_qty,
                                         'warehouse_id': t_warehouse_id,
                                         }))
                if(t_sign == 'ingoing'):
                    final_quantity += line.product_qty
                if(t_sign == 'outgoing'):
                    final_quantity -= line.product_qty

        t_lines.append((0, 0, {  'result_id': result_id,
                                         'date': t_date_to,
                                         'move_id': '',
                                         'document_number': '',
                                         'document_origin': _('Final Quantity'),
                                         'partner_id': None,
                                         'unit_of_measure': '',
                                         'cause': '',
                                         'sign': '',
                                         'quantity': final_quantity,
                                         'warehouse_id': t_warehouse_id,
                                         }))

        self.pool.get('wizard.stock.sheet.result').write(cr, uid, [result_id], {'line_ids': t_lines, })

        return result_id

    def view_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        self._check_date_range_validity(cr, uid, ids)

        form = self.read(cr, uid, ids)[0]
        t_date_from = form["date_from"]
        t_date_to = form["date_to"]
        t_product_id = form["product_id"][0]
        t_company_id = form["company_id"][0]
        if(form["warehouse_id"]):
            t_warehouse = form["warehouse_id"][0]
        else: 
            t_warehouse = None

        context.update({
                        'default_product_id': t_product_id,
                        'default_date_from': t_date_from,
                        'default_date_to': t_date_to,
                        'default_warehouse_id': t_warehouse,
                        'default_company_id':t_company_id
                        })

        result_id = self._set_sheet_result_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'stock_sheet_report_webkit',
                                              'view_stock_sheet_result_form')
        view_id = result and result[1] or False

        return {
                'name': _("Stock Sheet"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.stock.sheet.result',
                'type': 'ir.actions.act_window',
                'res_id': result_id,
                'view_id': view_id,
                'target': 'inlineview',
               }
