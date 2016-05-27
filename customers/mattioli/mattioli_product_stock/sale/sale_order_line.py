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
from openerp.addons import decimal_precision as dp
from openerp.tools import float_compare
from openerp import _

class sale_order_line_mattioli(osv.osv):

    _inherit = "sale.order.line"
    _columns = {
        'length': fields.float('Lunghezza [cm]'),
        'width': fields.float('Larghezza [cm]'),
        'thickness': fields.float('Spessore [cm]'),
        'price_uos': fields.float('Prezzo Mc/Mq', digits_compute=dp.get_precision('Product Price')),    
    }

    def _compute_uos(self, cr, uid, product,temp_length,temp_width,qty,temp_thickness=0):
        compute = 0
        prod_data = self.pool.get('product.product').browse(cr,uid,product)        

        if temp_thickness and prod_data.increment_thickness:
            if prod_data.increment_uom_thickness == 'cm':
                temp_thickness += prod_data.increment_thickness
            else:
                temp_thickness *= 1+(prod_data.increment_thickness/100)
            
        if prod_data.increment_width:
            if prod_data.increment_uom_width == 'cm':
                temp_width += prod_data.increment_width
            else:
                temp_width *= 1+(prod_data.increment_width/100)
        
        if prod_data.increment_length:
            if prod_data.increment_uom_length == 'cm':
                temp_length += prod_data.increment_length
            else:
                temp_length *= 1+(prod_data.increment_length/100)
        
        if temp_thickness == 0:
            compute = temp_width*temp_length/10000
        else:
            compute = temp_width*temp_length*temp_thickness/1000000
            
        return compute*qty

    def onchange_sizes(self, cr, uid, ids, product_id, qty, length, width, thickness, context=None):
        context = context or {}
        if not product_id:
            return {}
        product_obj = self.pool.get('product.product').browse(cr,uid,product_id,context=context)
        if product_obj.uos_id.is_cubic_meter or product_obj.uos_id.is_square_meter:
            if product_obj.uos_id.is_cubic_meter and not thickness:
                uos_qty= 0.0
            else:
                if product_obj.uos_id.is_square_meter:
                    thickness = 0.0
                uos_qty = self._compute_uos(cr, uid, product_id,length,width,qty,thickness)
            return {'value': {'product_uos_qty': uos_qty}}
        return {}
    
    def onchange_uos_qty(self, cr, uid, ids, product_id, price, qty_uom, qty_uos, date_order=False, pricelist=None, partner_id=None, context=None):
        res = {}
        if not context:
            context = {}
        if 'from_qty' in context and context['from_qty']:
            return res
        if not product_id or not pricelist or not partner_id:
            return res
        
        product_obj = self.pool.get('product.product').browse(cr,uid,product_id,context=context)         
        if not price:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], product_id, qty_uom, partner_id, {'uom': product_obj.uom_id.id,'date': date_order,})[pricelist]                
        if price and product_obj.uom_id and product_obj.uos_id and product_obj.uom_id != product_obj.uos_id:    
            res['value'] = {'price_unit': price*(qty_uos/qty_uom)}
        return res
 
    def onchange_price_uos(self, cr, uid, ids, product_id, price, qty_uom, qty_uos, context=None):
        res = {}
        product_obj = self.pool.get('product.product').browse(cr,uid,product_id,context=context)         

        if price and product_obj.uom_id and product_obj.uos_id and product_obj.uom_id != product_obj.uos_id:    
            res['value'] = {'price_unit': price*(qty_uos/qty_uom)}
        return res
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, price_unit=False, context=None):
        
        res = super(sale_order_line_mattioli,self).product_id_change(cr,uid,ids,pricelist,product,qty,uom,qty_uos,uos,name,partner_id,lang,update_tax,date_order,packaging,fiscal_position, flag,context=context)
        
        if 'value' in res and 'product_uos_qty' in res['value'] and qty and 'price_unit' in res['value']:   
            t_uos = uos or ('product_uos' in res['value'] and res['value']['product_uos']) or False
            t_uom = uom or ('product_uom' in res['value'] and res['value']['product_uom']) or False
            if t_uos and t_uom:
                if t_uos != t_uom:
                    res['value']['price_uos'] = res['value']['price_unit']
                    res['value']['price_unit'] = res['value']['price_unit']*(res['value']['product_uos_qty']/qty)   
            else:
                res['value']['price_uos'] = 0 
                    
        if 'value' in res and res['value'] and product:
            product_obj = self.pool.get('product.product').browse(cr,uid,product,context=context)
            if product_obj.uos_id.is_square_meter or product_obj.uos_id.is_cubic_meter:             
                length = self.pool.get('product.product')._get_size(cr, uid, product,"Lunghezza") or 0.0
                res['value']['length'] = length
                width = self.pool.get('product.product')._get_size(cr, uid, product,"Larghezza") or 0.0
                res['value']['width'] = width
                if product_obj.uos_id.is_cubic_meter:
                    thickness = product_obj.thickness
                    res['value']['thickness'] = product_obj.thickness
                    res['value']['product_uos_qty'] = self._compute_uos(cr, uid, product,length,width,qty,thickness)
                else:
                    res['value']['product_uos_qty'] = self._compute_uos(cr, uid, product,length,width,qty)
        if 'value' in res and 'from_qty' in context and context['from_qty']:
            if 'price_uos' in res['value']:
                del res['value']['price_uos']
            if 'purchase_price' in res['value']:
                del res['value']['purchase_price']
            if 'price_unit' in res['value']:
                del res['value']['price_unit']
        return res
      
    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):
        context = context or {}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        warehouse_obj = self.pool['stock.warehouse']
        warning = {}
        #UoM False due to hack which makes sure uom changes price, ... in product_id_change
        res = self.product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, price_unit=False, context=context)

        if not product:
            res['value'].update({'product_packaging': False})
            return res

        #update of result obtained in super function
        product_obj = product_obj.browse(cr, uid, product, context=context)
        res['value'].update({'product_tmpl_id': product_obj.product_tmpl_id.id, 'delay': (product_obj.sale_delay or 0.0)})

        # Calling product_packaging_change function after updating UoM
        res_packing = self.product_packaging_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, packaging, context=context)
        res['value'].update(res_packing.get('value', {}))
        warning_msgs = res_packing.get('warning') and res_packing['warning']['message'] or ''

        if product_obj.type == 'product':
            #determine if the product is MTO or not (for a further check)
            isMto = False
            if warehouse_id:
                warehouse = warehouse_obj.browse(cr, uid, warehouse_id, context=context)
                for product_route in product_obj.route_ids:
                    if warehouse.mto_pull_id and warehouse.mto_pull_id.route_id and warehouse.mto_pull_id.route_id.id == product_route.id:
                        isMto = True
                        break
            else:
                try:
                    mto_route_id = warehouse_obj._get_mto_route(cr, uid, context=context)
                except:
                    # if route MTO not found in ir_model_data, we treat the product as in MTS
                    mto_route_id = False
                if mto_route_id:
                    for product_route in product_obj.route_ids:
                        if product_route.id == mto_route_id:
                            isMto = True
                            break

            #check if product is available, and if not: raise a warning, but do this only for products that aren't processed in MTO
            if not isMto:
                uom_record = False
                if uom:
                    uom_record = product_uom_obj.browse(cr, uid, uom, context=context)
                    if product_obj.uom_id.category_id.id != uom_record.category_id.id:
                        uom_record = False
                if not uom_record:
                    uom_record = product_obj.uom_id
                compare_qty = float_compare(product_obj.virtual_available, qty, precision_rounding=uom_record.rounding)
                if compare_qty == -1:
                    warn_msg = _('You plan to sell %.2f %s but you only have %.2f %s available !\nThe real stock is %.2f %s. (without reservations)') % \
                        (qty, uom_record.name,
                         max(0,product_obj.virtual_available), uom_record.name,
                         max(0,product_obj.qty_available), uom_record.name)
                    warning_msgs += _("Not enough stock ! : ") + warn_msg + "\n\n"

        #update of warning messages
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        res.update({'warning': warning})
        return res
    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line_mattioli,self)._prepare_order_line_invoice_line(cr,uid,line,account_id,context=context)
        if res:
            if line.product_uom_qty and line.product_uos and (line.product_uos.is_cubic_meter or line.product_uos.is_square_meter):
                res['length'] = line.length
                res['width'] = line.width
                res['thickness'] = line.thickness
                res['uos_coeff'] = line.product_uos_qty/line.product_uom_qty
            return res
        else:
            return {}
