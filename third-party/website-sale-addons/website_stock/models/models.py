# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp import fields
from openerp import models
import openerp
from openerp import SUPERUSER_ID
from openerp import tools, api
from openerp.osv import osv, orm, fields
from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _


class product_product(osv.Model):
	_inherit = 'product.product'

	_columns={
		'wk_order_allow':fields.selection((('allow','Allow Order'),('deny','Deny Orders'),),'When Product is out of Stock'),

		'wk_in_stock_msg': fields.char('Message'),

		'wk_out_of_stock_msg': fields.char('Message'),

		'wk_override_default': fields.boolean('Override Default Message')
	}
	_defaults = {
		'wk_order_allow': 'deny',
		'wk_in_stock_msg': 'In Stock',
		'wk_out_of_stock_msg': 'This product has gone out of Stock!'

	}

class website(orm.Model):
	_inherit = 'website'

	def check_product_type(self, cr, uid, ids, product_id=False, context=None):
		if product_id:
			product_type = self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).type
			if product_type == 'service':
				return 1
			else:
				return 0

	def get_product_qty(self, cr, uid, ids, product_id=False, context=None):
		value = self.check_product_type(cr, uid, ids, product_id, context = context)
		if value == 0:
			if context == None:
				context ={}
			context = dict(context)
			if product_id:
				type_stock = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_stock_type')

				type_warehouse = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_warehouse_type')

				if type_warehouse=='all':
					if type_stock == 'on_hand':
						return self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).qty_available
					elif type_stock == 'forecasted':
						return self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).virtual_available
					else:
						qty = self.pool.get('product.product')._product_available(cr, SUPERUSER_ID, [product_id],None,False,context)
						quantity = qty[product_id]['qty_available'] - qty[product_id]['outgoing_qty']
						return quantity

				elif type_warehouse == 'specific':
					stock_location_id = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_stock_location')
					if stock_location_id:
						context={}
						context.update({'states': ('done',), 'what': ('in', 'out'), 'location': int(stock_location_id)})
						qty = self.pool.get('product.product')._product_available(cr, SUPERUSER_ID, [product_id],None,False,context=context)
						
						if type_stock == 'on_hand':
							quantity = qty[product_id]['qty_available']
							return quantity
						elif type_stock == 'forecasted':
							quantity = qty[product_id]['virtual_available']
							return quantity
						else:
							quantity = qty[product_id]['qty_available'] - qty[product_id]['outgoing_qty']
							return quantity
				else:
					return 0
		else:
			return 10

	def check_if_allowed(self, cr, uid, ids, product_id=False, context=None):
		value = self.check_product_type(cr, uid, ids, product_id, context = context)
		if value == 0:
			if product_id:
				check = self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).wk_order_allow
				if check == 'deny':
					return -1
			return 1
		else:
			return 1

	def check_quantity_display(self, cr, uid, ids, product_id=False, quantity=0 , context=None):
		value = self.check_product_type(cr, uid, ids, product_id, context = context)
		if value == 0:
			if product_id:
				display_qunt = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_display_qty')
				min_qunt_val = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_remaining_qty')
				if min_qunt_val:
					min_qunt = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_minimum_qty')
				if display_qunt:
					return 1
				elif min_qunt_val==True and min_qunt>=quantity:
					return 1
			return -1
		else:
			return -1

	def get_in_of_stock_message(self, cr, uid, ids, product_id=False, quantity=0, context=False):
		if product_id:
			min_qunt_val = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_remaining_qty')
			min_qunt = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_minimum_qty')
			if min_qunt_val==True and min_qunt>=quantity:
				return self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_custom_message')
			else:
				check_override = self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).wk_override_default
				if check_override:
					return self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).wk_in_stock_msg
		return self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_in_stock_msg')

	def get_out_of_stock_message(self, cr, uid, ids, product_id=False, context=False):
		if product_id:
			check_override = self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).wk_override_default
			if check_override:
				return self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).wk_out_of_stock_msg
		return self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'product.product', 'wk_out_of_stock_msg')

	def get_product_uom(self, cr, uid, ids, product_id=False, context=None):
		if product_id:
			return self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id).uom_id.name