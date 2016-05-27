# -*- coding: utf-8 -*-
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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from datetime import datetime


class purchase_order_mattioli(osv.osv):

    _inherit = "purchase.order"

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
        ''' prepare the stock move data from the PO line. This function returns a list of dictionary ready to be used in stock.move's create()'''
        product_uom = self.pool.get('product.uom')
        price_unit = order_line.price_unit
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
        res = []
        t_coeff = order_line.product_id.uos_coeff_deincr or 1.0
        move_template = {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_id.uos_id.id,  # diff
            'date': order.date_order,
            'date_expected': fields.date.date_to_datetime(self, cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': False,
            'state': 'draft',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': order.picking_type_id.id,
            'group_id': group_id,
            'procurement_id': False,
            'origin': order.name,
            'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': order.picking_type_id.warehouse_id.id,
            'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
        }

        diff_quantity = order_line.product_qty
        for procurement in order_line.procurement_ids:
            procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=order_line.product_uom.id)
            tmp = move_template.copy()
            tmp.update({
                'product_uom_qty': min(procurement_qty, diff_quantity),
                'product_uos_qty': min(procurement_qty, diff_quantity) * t_coeff,  # diff
                'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
                'procurement_id': procurement.id,
                'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state=='picking' and '2binvoiced') or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
                'propagate': procurement.rule_id.propagate,
            })
            diff_quantity -= min(procurement_qty, diff_quantity)
            res.append(tmp)
        #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
        #split the future stock move in two because the route followed may be different.
        if diff_quantity > 0:
            move_template['product_uom_qty'] = diff_quantity
            if order_line.uos_qty:
                move_template['product_uos_qty'] = order_line.uos_qty                
            else:
                move_template['product_uos_qty'] = diff_quantity * t_coeff
            res.append(move_template)
        return res

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):

        res = super(purchase_order_mattioli, self)._prepare_inv_line(cr,uid, account_id, order_line, context=context)
        
        if order_line.product_uom and order_line.uos_id and order_line.uos_qty:
            if order_line.uos_id.is_cubic_meter or order_line.uos_id.is_square_meter:
                res['price_unit'] = (order_line.price_unit * order_line.product_qty)/order_line.uos_qty
                res['uos_id'] = order_line.uos_id.id
                res['quantity'] = order_line.uos_qty
        
        return res


class purchase_order_line_mattioli(osv.osv):

    _inherit = "purchase.order.line"
    

    _columns = {
        'uos_id': fields.many2one('product.uom', string='UoS'),
        'price_uos': fields.float('Prezzo Mc/Mq', digits_compute=dp.get_precision('Product Price')), 
        'uos_qty': fields.float(digits_compute= dp.get_precision('Product UoS'), string="Quantità (UoS)"),
    }
    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
        
        res = super(purchase_order_line_mattioli, self).onchange_product_id(cr,uid,ids,pricelist_id,product_id,qty,uom_id,partner_id,date_order,fiscal_position_id,date_planned,name,price_unit,state,context)

        if product_id and 'value' in res and 'product_uom' in res['value'] and 'price_unit' in res['value']:    
            if self.pool.get('product.product').browse(cr,uid,product_id).uos_id and self.pool.get('product.product').browse(cr,uid,product_id).uos_id.id != res['value']['product_uom']:
                coeff = self.pool.get('product.product').browse(cr,uid,product_id).uos_coeff_deincr
                uos_id = self.pool.get('product.product').browse(cr,uid,product_id).uos_id.id
                res['value']['price_uos'] = res['value']['price_unit']
                res['value']['price_unit'] = res['value']['price_unit']*coeff
                res['value']['uos_id'] = uos_id
            else:
                res['value']['price_uos'] = 0.0
        else:
            res['value']['price_uos'] = 0.0
                
        if qty and product_id:
            coeff = self.pool.get('product.product').browse(cr,uid,product_id).uos_coeff_deincr
            res['value'].update({'uos_qty': qty * coeff})
        return res    

    def onchange_uos_qty(self, cr, uid, ids, product, qty_uom, qty_uos,  date_order=False, pricelist_id=None, partner_id=None, context=None):
        res = {}

        if not product or not partner_id:
            return res
        
        product_obj = self.pool.get('product.product').browse(cr,uid,product,context=context)         
        uom_id = product_obj.uom_id.id
        # - determine price_unit and taxes_id
        if pricelist_id:
            product_pricelist = self.pool.get('product.pricelist')
            date_order_str = datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
            price = product_pricelist.price_get(cr, uid, [pricelist_id], product, qty_uom or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order_str})[pricelist_id]
        else:
            price = product.standard_price

        if price and product_obj.uom_id and product_obj.uos_id and product_obj.uom_id != product_obj.uos_id:    
            res['value'] = {'price_unit': price*(qty_uos/qty_uom)}
        return res
    
    def onchange_price_uos(self, cr, uid, ids, product_id, price, qty_uom, qty_uos, context=None):
        res = {}
        product_obj = self.pool.get('product.product').browse(cr,uid,product_id,context=context)         

        if price and product_obj.uom_id and product_obj.uos_id and product_obj.uom_id != product_obj.uos_id:    
            res['value'] = {'price_unit': price*(qty_uos/qty_uom)}
        return res
