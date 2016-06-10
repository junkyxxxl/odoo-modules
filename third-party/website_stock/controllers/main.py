# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import QueryURL
import logging
logger = logging.getLogger(__name__)

class website_sale(website_sale):
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        if int(add_qty) == 0:
            add_qty = '1'
        get_quantity = request.website.get_product_qty(int(product_id))
        allow_order = request.website.check_if_allowed(int(product_id))
        present_qty = 0
        sale_order_obj = request.registry.get('sale.order.line')
        order = request.website.sale_get_order()
        if order:
            order_lines = order.website_order_line
        else:
            order_lines = []
        # logger.info("***********************%r" ,order_lines)
        for line in order_lines:
            line_product = sale_order_obj.browse(cr, SUPERUSER_ID, [line.id], context = context).product_id
            if line_product.id == int(product_id):
                present_qty = sale_order_obj.browse(cr, SUPERUSER_ID, [line.id], context=context).product_uom_qty
                break;
        temp = float(present_qty) + float(add_qty)
        if allow_order == 1:
            return super(website_sale, self).cart_update(product_id, add_qty, set_qty)
            
        elif float(get_quantity) >= temp:
            return super(website_sale, self).cart_update(product_id, add_qty, set_qty)

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        cr, uid, context = request.cr, request.uid, request.context
        sale_order_obj = request.registry.get('sale.order.line')
        present_qty = sale_order_obj.browse(cr, SUPERUSER_ID, [line_id], context=context).product_uom_qty
        get_quantity = request.website.get_product_qty(int(product_id))
        allow_order = request.website.check_if_allowed(int(product_id))

        if allow_order == 1:
            return super(website_sale, self).cart_update_json(product_id, line_id, add_qty, set_qty)

        elif get_quantity >= set_qty:
            return super(website_sale, self).cart_update_json(product_id, line_id, add_qty, set_qty)

        return super(website_sale, self).cart_update_json(product_id, line_id, None, present_qty)

    @http.route(['/shop/cart/update_json/msg'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json_msg(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        cr, uid, context = request.cr, request.uid, request.context

        sale_order_obj = request.registry.get('sale.order.line')
        present_qty = sale_order_obj.browse(cr, SUPERUSER_ID, [line_id], context=context).product_uom_qty
        get_quantity = request.website.get_product_qty(int(product_id))
        allow_order = request.website.check_if_allowed(int(product_id))
        if allow_order == -1:
            if get_quantity < set_qty:
                return "More Quantity Not in Stock"

    @http.route(['/shop/cart/update/msg'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_msg(self, product_id, add_qty=1, set_qty=0, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        result = {'status':'allow'}
        if int(add_qty) == 0:
            add_qty = '1'
        get_quantity = request.website.get_product_qty(int(product_id))
        allow_order = request.website.check_if_allowed(int(product_id))
        present_qty = 0
        sale_order_obj = request.registry.get('sale.order.line')
        order = request.website.sale_get_order()
        if order:
            order_lines = order.website_order_line
        else:
            order_lines = []
        for line in order_lines:
            line_product = sale_order_obj.browse(cr, SUPERUSER_ID, [line.id], context = context).product_id
            if line_product.id == int(product_id):
                present_qty = sale_order_obj.browse(cr, SUPERUSER_ID, [line.id], context=context).product_uom_qty
                break;
        temp = float(present_qty) + float(add_qty)
        if allow_order == -1:
            if float(get_quantity) < temp:
                result['present_qty'] = present_qty
                result['get_quantity'] = get_quantity
                result['remain_qty'] = (get_quantity - present_qty)
                result['status']='deny'
        return result


