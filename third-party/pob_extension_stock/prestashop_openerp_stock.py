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

from datetime import date, datetime
from dateutil import relativedelta
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging

_logger = logging.getLogger(__name__)

from openerp import workflow
import prestapi
from prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError
# from openerp.addons.pob import _unescape
def _unescape(text):
	##
	# Replaces all encoded characters by urlib with plain utf8 string.
	#
	# @param text source text.
	# @return The plain text.
	from urllib import unquote_plus
	return unquote_plus(text.encode('utf8'))
################## .............prestashop-openerp stock.............##################
			
# Overriding this class in order to handle Stock Management b/w OpenERP n PrestaShop. 
class stock_move(osv.osv):
	_inherit="stock.move"
	
	def action_done(self, cr, uid, ids, context=None):
		""" Makes the move done and if all moves are done, it will finish the picking.
		@return:
		"""
		context = context or {}
		super(stock_move, self).action_done(cr, uid, ids, context=context)
		todo = [move.id for move in self.browse(cr, uid, ids, context=context) if move.state == "draft"]
		if todo:
			ids = self.action_confirm(cr, uid, todo, context=context)
		if not context.has_key('prestashop'):
			check_out,check_in = [False,False]
			product_qty = 0
			pob_conf = self.pool.get('prestashop.configure').search(cr, uid, [('active','=',True)])
			if pob_conf:
				pob_location = self.pool.get('prestashop.configure').browse(cr, uid, pob_conf[0]).pob_default_stock_location.id
			else:
				pob_location = -1
			for id in ids:
				data=self.browse(cr,uid,id)
				erp_product_id = data.product_id.id
				flag=1 # means there is some origin.
				if data.origin!=False:
					# Check if origin is 'Sale' and channel is 'prestashop',no need to update quantity.			
					sale_id=self.pool.get('sale.order').search(cr,uid,[('name','=',data.origin)])
					if sale_id:
						get_channel=self.pool.get('sale.order').browse(cr,uid,sale_id[0]).channel
						if get_channel=='prestashop':
							flag=0 # no need to update quantity.
				else:
					flag=2 # no origin.

				if flag==1:
					if data.picking_type_id:
						check_pos = self.pool.get('ir.model').search(cr,uid,[('model','=','pos.order')])
						if check_pos:
							pos_order_data=self.pool.get('pos.order').search(cr,uid,[('name','=',data.origin)])
							if pos_order_data:
								lines=self.pool.get('pos.order').browse(cr,uid,pos_order_data[0]).lines
								for line in lines:
									get_line_data=self.pool.get('pos.order.line').search(cr,uid,[('product_id','=',erp_product_id),('id','=',line.id)])
									if get_line_data:
										data.product_qty=self.pool.get('pos.order.line').browse(cr,uid,get_line_data[0]).qty
						if data.picking_type_id.code=='incoming':
							if data.location_dest_id.id == pob_location:
								check_in = True
						if data.picking_type_id.code=='outgoing':
							if data.location_id.id == pob_location:
								check_out = True							
				if flag==2:						
					pob_conf = self.pool.get('prestashop.configure').search(cr, uid, [('active','=',True)])
					if pob_conf:
						pob_location = self.pool.get('prestashop.configure').browse(cr, uid, pob_conf[0]).pob_default_stock_location.id
					else:
						pob_location = -1
					if data.location_dest_id.id == pob_location:
						check_in = True
					elif data.location_id.id == pob_location:
						check_out = True					
				if check_in:									
					product_qty=int(data.product_qty)					
				if check_out:												
					product_qty=int(-data.product_qty)
				if check_in or check_out:
					self.synch_quantity(cr, uid, erp_product_id, product_qty, pob_conf, context)
		return True
	
	# Extra function to update quantity(s) of product to prestashop`s end.
	def synch_quantity(self, cr, uid, erp_product_id, product_qty, config_ids, context=None):				
		response=self.update_quantity(cr,uid,erp_product_id,product_qty,config_ids[0],context)
		if response[0]==1:
			return True
			
	# Function to update quantity of products to prestashop`s end. 	
	def update_quantity(self,cr,uid,erp_product_id,quantity,config_id,context=None):
		check_mapping=self.pool.get('prestashop.product').search(cr,uid,[('erp_product_id','=',erp_product_id)])
		if check_mapping:
			presta_product_id = self.pool.get('prestashop.product').browse(cr,uid,check_mapping[0]).presta_product_id
			presta_product_attribute_id = self.pool.get('prestashop.product').browse(cr,uid,check_mapping[0]).presta_product_attr_id
			
			if config_id:
				obj = self.pool.get('prestashop.configure').browse(cr,uid,config_id)
				url = obj.api_url
				key = obj.api_key
				try:
					prestashop = PrestaShopWebServiceDict(url,key)
				except Exception, e:
					return [0,' Error in connection',check_mapping[0]]
				try:
					stock_search = prestashop.get('stock_availables',options={'filter[id_product]':presta_product_id,'filter[id_product_attribute]':presta_product_attribute_id})
				except Exception,e:
					return [0,' Unable to search given stock id',check_mapping[0]]
				if type(stock_search['stock_availables'])==dict:
					stock_id = stock_search['stock_availables']['stock_available']['attrs']['id']
					try:
						stock_data = prestashop.get('stock_availables', stock_id)
					except Exception,e:
						return [0,' Error in Updating Quantity,can`t get stock_available data.',check_mapping[0]]
					if type(quantity)==str:
						quantity=quantity.split('.')[0]
					if type(quantity)==float:
						quantity=int(quantity)
					stock_data['stock_available']['quantity']=int(stock_data['stock_available']['quantity'])+int(quantity)
					try:
						up = prestashop.edit('stock_availables',stock_id,stock_data)
					except:
						pass
					return [1,'']
				else:
					return [0,' No stock`s entry found in prestashop for given combination (Product id:%s ; Attribute id:%s)'%(str(presta_product_id),str(presta_product_attribute_id)),check_mapping[0]]
		else:
			return [1,'']
					
stock_move()	