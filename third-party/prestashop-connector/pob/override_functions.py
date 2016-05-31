#!/usr/bin/env python
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
from pob import _unescape
from openerp import workflow
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
import prestapi
from prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError
############## Overide classes #################

class product_template(osv.osv):	
	_inherit = 'product.template'

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if context.has_key('prestashop'):
			if vals.has_key('name'):
				vals['name'] = _unescape(vals['name'])
			if vals.has_key('description'):
				vals['description'] = _unescape(vals['description'])
			if vals.has_key('description_sale'):
				vals['description_sale'] = _unescape(vals['description_sale'])
		template_id = super(product_template, self).create(cr, uid, vals, context=context)
		if context.has_key('prestashop'):
			variant_ids_ids = self.browse(cr,uid,template_id).product_variant_ids
			temp = {'template_id':template_id}
			if len(variant_ids_ids)==1:
				temp['product_id'] = variant_ids_ids[0].id
			else:
				temp['product_id'] = -1
			self.pool.get('prestashop.product.template').create(cr,uid,{'template_name':template_id,'erp_template_id':template_id,'presta_product_id':context['presta_id']})
			self.pool.get('prestashop.product').create(cr,uid,{'product_name':temp['product_id'],'erp_template_id':template_id,'presta_product_id':context['presta_id'],'erp_product_id':temp['product_id']})
			return temp
		return template_id

	def write(self,cr,uid,ids,vals,context=None):
		if context is None:
			context = {}
		map_obj = self.pool.get('prestashop.product.template')
		if context.has_key('prestashop'):
			if vals.has_key('name'):
				vals['name'] = _unescape(vals['name'])
			if vals.has_key('description'):
				vals['description'] = _unescape(vals['description'])
			if vals.has_key('description_sale'):
				vals['description_sale'] = _unescape(vals['description_sale'])
		# else:
		# 	if ids:
		# 		if type(ids) == list:
		# 			erp_id=ids[0]
		# 		else:
		# 			erp_id=ids
		# 		map_ids = map_obj.search(cr, uid, [('erp_template_id', '=',erp_id)])
		# 		if map_ids:
		# 			map_obj.write(cr, uid, map_ids[0], {'need_sync':'yes'})
		return super(product_template,self).write(cr,uid,ids,vals,context=context)
	_columns = {
        'template_mapping_id': fields.one2many('prestashop.product.template', 'template_name', string='PrestaShop Information',readonly="1"),
    }
product_template()	

class product_product(osv.osv):	
	_inherit = 'product.product'

	def check_for_new_price(self, cr, uid,template_id,value_id,price_extra,context=None):
		if context is None:
			context = {}
		product_attribute_price=self.pool.get('product.attribute.price')
		exists = product_attribute_price.search(cr,uid,[('product_tmpl_id','=',template_id),('value_id','=',value_id)])
		if not exists:
			temp ={'product_tmpl_id':template_id,'value_id':value_id,'price_extra':price_extra}
			pal_id = product_attribute_price.create(cr,uid,temp)
			return True
		else:
			pal_id = exists[0]
			product_attribute_price.write(cr,uid,pal_id,{'price_extra':price_extra})
			return True

	def check_for_new_attrs(self, cr, uid,template_id,ps_attributes,context=None):
		if context is None:
			context = {}
		product_template=self.pool.get('product.template')
		product_attribute_line=self.pool.get('product.attribute.line')
		all_values = []
		for attribute_id in ps_attributes:
			exists = product_attribute_line.search(cr,uid,[('product_tmpl_id','=',template_id),('attribute_id','=',int(attribute_id))])
			if not exists:
				temp ={'product_tmpl_id':template_id,'attribute_id':attribute_id}
				pal_id = product_attribute_line.create(cr,uid,temp)
			else:
				pal_id = exists[0]
			product_attribute_line.write(cr,uid,pal_id,{'value_ids':[[4,int(ps_attributes[attribute_id][0])]]})
			all_values.append(int(ps_attributes[attribute_id][0]))

			if ps_attributes[attribute_id][1]>=0.0:
				self.check_for_new_price(cr, uid,template_id,int(ps_attributes[attribute_id][0]),ps_attributes[attribute_id][1])
		return [[6,0,all_values]]

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if context.has_key('prestashop_variant'):
			template_obj = self.pool.get('product.template').browse(cr,uid,vals['product_tmpl_id'])
			vals['name'] = template_obj.name
			vals['description'] = template_obj.description
			vals['description_sale'] = template_obj.description_sale
			vals['type'] = template_obj.type
			vals['categ_id'] = template_obj.categ_id.id
			vals['uom_id'] = template_obj.uom_id.id
			vals['uom_po_id'] = template_obj.uom_po_id.id
			vals['default_code'] = _unescape(vals['default_code'])
			if vals.has_key('ps_attributes'):
				vals['attribute_value_ids']=self.check_for_new_attrs(cr,uid,template_obj.id,vals['ps_attributes'])
		erp_id =  super(product_product, self).create(cr, uid, vals, context=context)
		if context.has_key('prestashop_variant'):
			prestashop_product = self.pool.get('prestashop.product')
			exists = prestashop_product.search(cr,uid,[('erp_template_id','=',vals['product_tmpl_id']),('presta_product_attr_id','=',0)])
			if exists:
				pp_map = prestashop_product.browse(cr,uid,exists[0])
				if pp_map.product_name:
					self.write(cr,uid,pp_map.product_name.id,{'active':False})
				prestashop_product.unlink(cr,uid,exists)
			prestashop_product.create(cr,uid,{'product_name':erp_id,'erp_template_id':template_obj.id,'presta_product_id':context['presta_id'],'erp_product_id':erp_id,'presta_product_attr_id':context['presta_attr_id']})
		return erp_id
	
	def write(self, cr, uid, ids, vals, context=None):
		if context is None:
			context = {}
		map_obj = self.pool.get('prestashop.product')
		if not context.has_key('prestashop'):
			if ids:
				if type(ids) == list:
					erp_id=ids[0]
				else:
					erp_id=ids
				map_ids = map_obj.search(cr, uid, [('erp_product_id', '=',erp_id)])
				if map_ids:
					map_obj.write(cr, uid, map_ids[0], {'need_sync':'yes'})
		elif context.has_key('prestashop_variant'):
			if type(ids) == list:
				erp_id=ids[0]
			else:
				erp_id=ids
			template_obj = self.pool.get('product.product').browse(cr,uid,erp_id).product_tmpl_id
			# template_obj = self.pool.get('product.template').browse(cr,uid,'product_tmpl_id')
			vals['name'] = template_obj.name
			vals['description'] = template_obj.description
			vals['description_sale'] = template_obj.description_sale
			vals['type'] = template_obj.type
			vals['categ_id'] = template_obj.categ_id.id
			vals['uom_id'] = template_obj.uom_id.id
			vals['uom_po_id'] = template_obj.uom_po_id.id
			vals['default_code'] = _unescape(vals['default_code'])
			if vals.has_key('ps_attributes'):
				vals['attribute_value_ids']=self.check_for_new_attrs(cr,uid,template_obj.id,vals['ps_attributes'])
		return super(product_product,self).write(cr,uid,ids,vals,context=context)
	_columns = {
        'product_mapping_id': fields.one2many('prestashop.product', 'product_name', string='PrestaShop Information',readonly="1"),
    }
product_product()

class product_category(osv.osv):	
	_inherit = 'product.category'
	
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if context.has_key('prestashop'):
			if vals.has_key('name'):
				vals['name'] = _unescape(vals['name'])
		return super(product_category, self).create(cr, uid, vals, context=context)
		
	def write(self,cr,uid,ids,vals,context=None):
		if context is None:
			context = {}
		map_obj = self.pool.get('prestashop.category')
		# raise osv.except_osv(_('Error!'),_('context=%s')%(context))		
		if not context.has_key('prestashop'):
			if ids:
				if type(ids) == list:
					erp_id=ids[0]
				else:
					erp_id=ids
				map_ids = map_obj.search(cr, uid, [('erp_category_id', '=',erp_id)])
				if map_ids:
					map_obj.write(cr, uid, map_ids[0], {'need_sync':'yes'})
		else:
			if vals.has_key('name'):
				vals['name'] = _unescape(vals['name'])
		return super(product_category,self).write(cr,uid,ids,vals,context=context)
product_category()

class res_partner(osv.osv):
	_inherit = 'res.partner'
	
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if context.has_key('prestashop'):
			if vals.has_key('name'):
				vals['name'] = _unescape(vals['name'])
			if vals.has_key('street'):
				vals['street'] = _unescape(vals['street'])
			if vals.has_key('street2'):
				vals['street2'] = _unescape(vals['street2'])
			if vals.has_key('city'):
				vals['city'] = _unescape(vals['city'])
		return super(res_partner, self).create(cr, uid, vals, context=context)
	
	def write(self,cr,uid,ids,vals,context=None):
		if context is None:
			context = {}
		map_obj = self.pool.get('prestashop.customer')
		if not context.has_key('prestashop'):
			if ids:
				if type(ids) == list :
					if ids:
						erp_id=ids[0]
				else:
					erp_id=ids
				map_ids = map_obj.search(cr, uid, [('erp_customer_id', '=',erp_id)])
				if map_ids:
					map_obj.write(cr, uid, map_ids[0], {'need_sync':'yes'})
		else:
			if vals.has_key('name'):
				vals['name'] = _unescape(vals['name'])
			if vals.has_key('street'):
				vals['street'] = _unescape(vals['street'])
			if vals.has_key('street2'):
				vals['street2'] = _unescape(vals['street2'])
			if vals.has_key('city'):
				vals['city'] = _unescape(vals['city'])
		return super(res_partner,self).write(cr,uid,ids,vals,context=context)
res_partner()

class delivery_carrier(osv.osv):
	_inherit = 'delivery.carrier'
	
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if context.has_key('prestashop'):
			vals['name'] = _unescape(vals['name'])
			vals['partner_id'] = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
			vals['product_id'] = self.pool.get('force.done')._get_virtual_product_id(cr,uid,{'name':'Shipping'})
		return super(delivery_carrier, self).create(cr, uid, vals, context=context)	

	def write(self, cr, uid, ids, vals, context=None):
		if context is None:
			context = {}
		if context.has_key('prestashop'):
			vals['name'] = _unescape(vals['name'])
			vals['partner_id'] = uid
			vals['product_id'] = self.pool.get('force.done')._get_virtual_product_id(cr,uid,{'name':'Shipping'})
		return super(delivery_carrier, self).write(cr, uid, ids, vals, context=context)	
delivery_carrier()

class product_attribute(osv.osv):	
	_inherit = 'product.attribute'
	
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if context.has_key('prestashop'):
			if vals.has_key('name'):
				vals['name'] = _unescape(vals['name'])
		return super(product_attribute, self).create(cr, uid, vals, context=context)
		
	def write(self,cr,uid,ids,vals,context=None):
		if context is None:
			context = {}						
		if context.has_key('prestashop'):
			if vals.has_key('name'):
				vals['name'] = _unescape(vals['name'])
		return super(product_attribute,self).write(cr,uid,ids,vals,context=context)
product_attribute()

class sale_order(osv.osv):
	_inherit = "sale.order"

	def manual_prestashop_invoice(self,cr,uid,ids,context=None):
		error_message=''
		status='no'
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			error_message='Connection needs one Active Configuration setting.'
			status='no'
		if len(config_id)>1:
			error_message='Sorry, only one Active Configuration setting is allowed.'
			status='no'
		else:
			obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			url=obj.api_url
			key=obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
			except PrestaShopWebServiceError,e:
				error_message='Invalid Information, Error %s'%e
				status='no'
			except IOError, e:
				error_message='Error %s'%e
				status='no'
			except Exception,e:
				error_message="Error,Prestashop Connection in connecting: %s" % e
				status='no'
			if prestashop:
				order_id=self.pool.get('prestashop.order').get_id(cr,uid,'prestashop','order',ids[0])
				if order_id:
					try:
						inv_data = prestashop.get('order_invoices', options={'schema': 'blank'})
					except Exception,e:
						error_message="Error %s, Error in getting Blank XML"%str(e)
						status='no'
					data=prestashop.get('orders',order_id)
					inv_data['order_invoice'].update({
													'id_order' : order_id,
													'total_wrapping_tax_incl': data['order']['total_wrapping_tax_incl'],
													'total_products': data['order']['total_products'],
													'total_wrapping_tax_excl': data['order']['total_wrapping_tax_excl'],
													'total_paid_tax_incl': data['order']['total_paid_tax_incl'],
													'total_products_wt': data['order']['total_products_wt'],
													'total_paid_tax_excl': data['order']['total_paid_tax_excl'],
													'total_shipping_tax_incl': data['order']['total_shipping_tax_incl'],
													'total_shipping_tax_excl': data['order']['total_shipping_tax_excl'],
													 'delivery_number': data['order']['delivery_number'],
													 'number' : '1'
													})
					invoice=prestashop.add('order_invoices', inv_data)
				else:
					return True
		
		
	def manual_invoice(self, cr, uid, ids, context=None):
		if context is None:
			context={}
		mod_obj = self.pool.get('ir.model.data')				
		inv_ids = set()
		inv_ids1 = set()
		for id in ids:
			for record in self.pool.get('sale.order').browse(cr, uid, id).invoice_ids:
				inv_ids.add(record.id)
		#inv_ids would have old invoices if any
		for id in ids:
			workflow.trg_validate(uid, 'sale.order', id, 'manual_invoice', cr)
			for record in self.pool.get('sale.order').browse(cr, uid, id).invoice_ids:
				inv_ids1.add(record.id)
		inv_ids = list(inv_ids1.difference(inv_ids))		
		res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
		res_id = res and res[1] or False,
		#manual_prestashop_invoice method is used to create an invoice on prestashop end...			
		# if not context.has_key('prestashop'):
		# 	config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		# 	if len(config_id)>0:
		# 		self.manual_prestashop_invoice(cr,uid,ids,context)
		return {
			'name': _('Customer Invoices'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [res_id],
			'res_model': 'account.invoice',
			'context': "{'type':'out_invoice'}",
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': inv_ids and inv_ids[0] or False,
		}
	
	def manual_prestashop_invoice_cancel(self,cr,uid,ids,context=None):
		error_message=''
		status='yes'
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			error_message='Connection needs one Active Configuration setting.'
			status='no'
		if len(config_id)>1:
			error_message='Sorry, only one Active Configuration setting is allowed.'
			status='no'
		else:
			obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			url=obj.api_url
			key=obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
			except PrestaShopWebServiceError,e:
				error_message='Invalid Information, Error %s'%e
				status='no'
			except IOError, e:
				error_message='Error %s'%e
				status='no'
			except Exception,e:
				error_message="Error,Prestashop Connection in connecting: %s" % e
				status='no'
			if prestashop:
				order_id=self.pool.get('prestashop.order').get_id(cr,uid,'prestashop','order',ids[0])
				if order_id:
					try:
						order_his_data=prestashop.get('order_histories', options={'schema': 'blank'})
					except Exception,e:
						error_message="Error %s, Error in getting Blank XML"%str(e)
						status='no'
					order_his_data['order_history'].update({
					'id_order' : order_id,
					'id_order_state':6
					})
					state_update=prestashop.add('order_histories?sendemail=1', order_his_data)
				else:
					return True
				
	def action_cancel(self, cr, uid, ids, context=None):		
		if context is None:
			context = {}
		sale_order_line_obj = self.pool.get('sale.order.line')
		for sale in self.browse(cr, uid, ids, context=context):
			for inv in sale.invoice_ids:
				if inv.state not in ('draft', 'cancel'):
					raise osv.except_osv(
                        _('Cannot cancel this sales order!'),
                        _('First cancel all invoices attached to this sales order.'))
			for r in self.read(cr, uid, ids, ['invoice_ids']):
				for inv in r['invoice_ids']:
					workflow.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
			sale_order_line_obj.write(cr, uid, [l.id for l in  sale.order_line],
                    {'state': 'cancel'})
		self.write(cr, uid, ids, {'state': 'cancel'})
		##manual_prestashop_invoice_cancel method is used to cancel an order on prestashop end...
		if not context.has_key('prestashop'):			
			config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
			if len(config_id)>0:
				self.manual_prestashop_invoice_cancel(cr,uid,ids,context)		
		return True	

	_columns = {
	'channel':fields.selection((('openerp','Openerp'),('prestashop','PrestaShop')),'Channel name'),
	}
	_defaults={
		'channel':'openerp',
	}
sale_order()

class account_invoice(osv.osv):
	_inherit="account.invoice"
	
	def manual_prestashop_paid(self,cr,uid,ids,context=None):
		order_name=self.browse(cr,uid,ids[0]).origin				
		sale_id=self.pool.get('sale.order').search(cr,uid,[('name','=',order_name)])
		if sale_id:
			error_message=''
			status='yes'
			config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
			if not config_id:
				error_message='Connection needs one Active Configuration setting.'
				status='no'
			if len(config_id)>1:
				error_message='Sorry, only one Active Configuration setting is allowed.'
				status='no'
			else:
				obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
				url=obj.api_url
				key=obj.api_key
				try:
					prestashop = PrestaShopWebServiceDict(url,key)
				except PrestaShopWebServiceError,e:
					error_message='Invalid Information, Error %s'%e
					status='no'
				except IOError, e:
					error_message='Error %s'%e
					status='no'
				except Exception,e:
					error_message="Error,Prestashop Connection in connecting: %s" % e
					status='no'
				if prestashop:
					order_id=self.pool.get('prestashop.order').get_id(cr,uid,'prestashop','order',sale_id[0])
					if order_id:
						try:
							order_his_data=prestashop.get('order_histories', options={'schema': 'blank'})
						except Exception,e:
							error_message="Error %s, Error in getting Blank XML"%str(e)
							status='no'
						order_his_data['order_history'].update({
						'id_order' : order_id,
						'id_order_state':2
						})
						state_update=prestashop.add('order_histories?sendemail=1', order_his_data)
					else:
						return True
							
account_invoice()

class stock_picking(osv.osv):
	_name = "stock.picking"
	_inherit="stock.picking"

	def manual_prestashop_shipment(self,cr,uid,ids,context=None):
		order_name=self.pool.get('stock.picking').browse(cr,uid,ids[0]).origin				
		sale_id=self.pool.get('sale.order').search(cr,uid,[('name','=',order_name)])
		if sale_id:
			error_message=''
			status='yes'
			config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
			if not config_id:
				error_message='Connection needs one Active Configuration setting.'
				status='no'
			if len(config_id)>1:
				error_message='Sorry, only one Active Configuration setting is allowed.'
				status='no'
			else:
				obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
				url=obj.api_url
				key=obj.api_key
				try:
					prestashop = PrestaShopWebServiceDict(url,key)
				except PrestaShopWebServiceError,e:
					error_message='Invalid Information, Error %s'%e
					status='no'
				except IOError, e:
					error_message='Error %s'%e
					status='no'
				except Exception,e:
					error_message="Error,Prestashop Connection in connecting: %s" % e
					status='no'
				if prestashop:
					order_id=self.pool.get('prestashop.order').get_id(cr,uid,'prestashop','order',sale_id[0])
					if order_id:
						try:
							order_his_data=prestashop.get('order_histories', options={'schema': 'blank'})
						except Exception,e:
							error_message="Error %s, Error in getting Blank XML"%str(e)
							status='no'
						order_his_data['order_history'].update({
						'id_order' : order_id,
						'id_order_state':4
						})
						state_update=prestashop.add('order_histories?sendemail=1', order_his_data)
		return True


	@api.cr_uid_ids_context
	def do_transfer(self, cr, uid, picking_ids, context=None):		
		super(stock_picking, self).do_transfer(cr, uid, picking_ids, context = context)
		if not context.has_key('prestashop'):
			config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
			if len(config_id)>0:
				self.manual_prestashop_shipment(cr, uid, picking_ids, context)
		return True

	def export_tracking_no_to_prestashop(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		get_carrier_data = []
		presta_id = []
		order_carrier_id = False
		error_message = ''
		message = ''
		up_length = 0
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
		if len(config_id)>1:
			raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))		
		else:
			obj = self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			url = obj.api_url
			key = obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
			except Exception,e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
			if prestashop:				
				picking_obj = self.pool.get('stock.picking').browse(cr, uid, ids[0])
				sale_order_id = picking_obj.sale_id.id
				track_ref = picking_obj.carrier_tracking_ref
				if not track_ref:
					track_ref = ''
				if sale_order_id:
					check = self.pool.get('prestashop.order').search(cr, uid, [('erp_id','=',sale_order_id)])
					if check:
						presta_id = self.pool.get('prestashop.order').browse(cr, uid, check[0]).presta_id
					if presta_id:
						try:
							get_carrier_data = prestashop.get('order_carriers',options={'filter[id_order]':presta_id})
						except Exception,e:
							error_message="Error %s, Error in getting Carrier Data"%str(e)
						try:
							if get_carrier_data['order_carriers']:
								order_carrier_id = get_carrier_data['order_carriers']['order_carrier']['attrs']['id']
							if order_carrier_id:
								data = prestashop.get('order_carriers',order_carrier_id)
								data['order_carrier'].update({
									'tracking_number' : track_ref,					
									})
								try:
									return_id = prestashop.edit('order_carriers',order_carrier_id, data)
									up_length = up_length + 1
								except Exception,e:
									error_message = error_message + str(e)

						except Exception,e:
							error_message = error_message + str(e)
			if not error_message:				
				if up_length == 0:
					message = "No Prestashop Order record fetched in selected stock movement record!!!"
				else:
					message = 'Carrier Tracking Reference Number Successfully Updated to Prestashop!!!'
			else:				
				message = "Error in Updating: %s"%(error_message)
			partial_id = self.pool.get('pob.message').create(cr, uid, {'text':message}, context=context)
			return {'name':_("Message"),
					'view_mode': 'form',
					'view_id': False,
					'view_type': 'form',
					'res_model': 'pob.message',
					'res_id': partial_id,
					'type': 'ir.actions.act_window',
					'nodestroy': True,
					'target': 'new',
					'domain': context,								 
				}

stock_picking()

class account_voucher(osv.osv):
	_inherit="account.voucher"
	
	def button_proforma_voucher(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		# raise osv.except_osv(_('Error!'),_('context=%s')%(context))	
		self.signal_workflow(cr, uid, ids, 'proforma_voucher')
		if not context.has_key('prestashop'):
			config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])	
			if len(config_id)>0:						
				self.pool.get('account.invoice').manual_prestashop_paid(cr,uid,[context['invoice_id']],context)

		return {'type': 'ir.actions.act_window_close'}
account_voucher()