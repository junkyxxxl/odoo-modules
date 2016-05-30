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
from openerp.tools.translate import _
from pob import _unescape
from openerp import tools
from openerp import SUPERUSER_ID
from openerp import workflow

############## PrestaShop classes #################
class force_done(osv.osv):
	_name="force.done"

	def add_tracking_number(self, cr, uid, data, context=None):
		if context is None:
			context = {}
		order_name=self.pool.get('sale.order').name_get(cr,uid,data['order_id'])
		pick_id = self.pool.get('stock.picking').search(cr, uid,[('origin','=',order_name[0][1])])		
		if pick_id:
			self.pool.get('stock.picking').write(cr, uid,pick_id[0],{'carrier_tracking_ref':data['track_no']})
		return True

	def action_multiple_synchronize_reference(self, cr, uid, ids, context=None):
		if context is None:
			context = {}		
		selected_ids = context.get('active_ids')		
		up_length = 0		
		error_message = ''
		message = ''
		to_be_updated = []	
		presta_id = []
		config_id = self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
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
			except Exception, e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))		
			if prestashop:			 				
				for k in self.pool.get('stock.picking').browse(cr, uid, selected_ids):
					sale_order_id = k.sale_id.id
					track_ref = k.carrier_tracking_ref
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
				if up_length==0:
					message = "No Prestashop Order records fetched in selected stock movement records!!!"
				else:
					message = '%s Carrier Tracking Reference Number Updated to Prestashop!!!'%(up_length)
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

	def create_attribute_value(self,cr,uid,data,context=None):
		if context is None:
			context = {}
		check = self.pool.get('product.attribute.value').search(cr,uid,[('attribute_id','=',data['erp_attribute_id']),('name','=',data['name'])])
		if check:
			erp_id = check[0]
		else:
			temp={}
			temp['name']=_unescape(data['name'])
			temp['attribute_id']=data['erp_attribute_id']
			temp['sequence']=data['sequence']
			erp_id = self.pool.get('product.attribute.value').create(cr,uid,temp)
		self.pool.get('prestashop.product.attribute.value').create(cr,uid,{'name':erp_id,'erp_id':erp_id,'presta_id':data['presta_attribute_value_id'],'erp_attr_id':data['erp_attribute_id'],'presta_attr_id':data['presta_attribute_id']})
		return erp_id

	def export_all_customers(self,cr,uid,cus_data,add_data,presta_user,context=None):
		if context is None:
			context = {}
		cus={}
		add={}
		cus_merge=[]
		add_merge=[]
		cus_synch_merge=[]
		add_synch_merge=[]
	
		for i in range(len(cus_data)):
			cus['name']=_unescape(cus_data[i]['firstname']+' '+cus_data[i]['lastname'])
			cus['email']=cus_data[i]['email']
			cus['is_company']=True
			if int(cus_data[i]['is_synch']):
				if self.pool.get('res.partner').exists(cr,uid,int(cus_data[i]['erp_customer_id'])):
					self.pool.get('res.partner').write(cr,uid,int(cus_data[i]['erp_customer_id']),cus)
					cus_synch_merge.append(cus_data[i]['id_customer'])
					erp_customer_id=cus_data[i]['erp_customer_id']
			else:
				erp_customer_id=self.pool.get('res.partner').create(cr,uid,cus)
				cus_merge.append({'erp_customer_id':erp_customer_id,'prestashop_customer_id':cus_data[i]['id_customer'],'created_by':presta_user})
				self.pool.get('prestashop.customer').create(cr,uid,{'customer_name':erp_customer_id,'erp_customer_id':erp_customer_id,'presta_customer_id':cus_data[i]['id_customer'],'presta_address_id':'-'})
			for data in filter(lambda x: x['id_customer']==cus_data[i]['id_customer'], add_data):
				if data['country'] and data['country_iso']:
					erp_country_id=self._get_country_id(cr,uid,{'name':_unescape(data['country']),'iso':data['country_iso']})
					if data['state'] and data['state_iso']:
						erp_state_id=self._get_state_id(cr,uid,{'name':_unescape(data['state']),'iso':data['state_iso'],'country_id':erp_country_id})
					else:
						erp_state_id=False
				else:
					erp_country_id=False
				add.update({'parent_id':erp_customer_id,
							'name':_unescape(data['firstname']+' '+data['lastname']),
							'email':cus['email'],
							'street':_unescape(data['address1']),
							'street2':_unescape(data['address2']),
							'phone':data['phone'],
							'mobile':data['phone_mobile'],
							'zip':data['postcode'],
							'city':_unescape(data['city']),
							'country_id':erp_country_id,
							'state_id':erp_state_id,
							'customer':False,
							'use_parent_address':False,
							})
				if int(data['is_synch']):
					if self.pool.get('res.partner').exists(cr,uid,int(data['erp_address_id'])):
						self.pool.get('res.partner').write(cr,uid,int(data['erp_address_id']),add)
						add_synch_merge.append(data['id_address'])
				else:
					erp_address_id=self.pool.get('res.partner').create(cr,uid,add)
					add_merge.append({'erp_address_id':erp_address_id,'prestashop_address_id':data['id_address'],'id_customer':cus_data[i]['id_customer'],'created_by':presta_user})
					self.pool.get('prestashop.customer').create(cr,uid,{'customer_name':erp_address_id,'erp_customer_id':erp_address_id,'presta_customer_id':cus_data[i]['id_customer'],'presta_address_id':data['id_address']})
		return [cus_merge,add_merge,cus_synch_merge,add_synch_merge]

	def _get_country_id(self, cr, uid,data):
		erp_country_id=self.pool.get('res.country').search(cr, uid, [('code', '=',data.get('iso'))])
		if not erp_country_id:
			erp_country_id=self.pool.get('res.country').create(cr,uid,{'name':data.get('name'),'code':data.get('iso')})
			return erp_country_id
		return erp_country_id[0]

	def _get_state_id(self, cr, uid,data):
		erp_state_id=self.pool.get('res.country.state').search(cr, uid, [('code', '=',data.get('iso')),('country_id', '=',data.get('country_id'))])
		if not erp_state_id:
			erp_state_id=self.pool.get('res.country.state').create(cr,uid,{'name':data.get('name'),'code':data.get('iso'),'country_id':data.get('country_id')})
			return erp_state_id
		return erp_state_id[0]

	def _get_journal_id(self, cr, uid, context=None):
		if context is None: context = {}
		if context.get('invoice_id', False):
			currency_id = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'], context=context).currency_id.id
			journal_id = self.pool.get('account.journal').search(cr, uid, [('currency', '=', currency_id)], limit=1)
			return journal_id and journal_id[0] or False
		res = self.pool.get('account.journal').search(cr, uid, [('type', '=','bank')], limit=1)
		return res and res[0] or False

	def _get_tax_id(self, cr, uid,journal_id,context=None):
		if context is None: context = {}
		journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
		account_id = journal.default_credit_account_id or journal.default_debit_account_id
		if account_id and account_id.tax_ids:
			tax_id = account_id.tax_ids[0].id
			return tax_id
		return False

	def _get_currency_id(self, cr, uid,journal_id,context=None):
		if context is None: context = {}
		journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
		if journal.currency:
			return journal.currency.id
		return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id

	def update_product_mapping(self,cr,uid,data,context=None):
		if context is None:
			context = {}
		map_ids=self.pool.get('prestashop.product').search(cr,uid,[('presta_product_id','=',int(data['presta_id']))])
		if map_ids:
			for id in map_ids:
				self.pool.get('prestashop.product').write(cr,uid,id,{'base_price':data['base_price']})
			return True
		return False

	def pricelist_currency(self,cr,uid,currency_name,currency_code,context=None):
		currency_id=self.pool.get('res.currency').search(cr,uid,[('name','=',currency_code),('active', '=', '1')])
		if currency_id:
			pricelist = {
						   'name': currency_name,
						   'active': '1',
						   'type': 'sale',
						   'currency_id': currency_id[0],
						}
			pricelist_id=self.pool.get("product.pricelist").create(cr, uid,pricelist)
			pricelist_version = {
						   'pricelist_id': pricelist_id,
						   'name':  'Default'+currency_name,
						   'active':True,
						   
						}
			price_version_id=self.pool.get('product.pricelist.version').create(cr,uid,pricelist_version)
			price_type_id = self.pool.get('product.price.type').search(cr,uid,[('name','=','Public Price')])
			product_pricelist_item={
						'name':'Dafault'+currency_name,
						'price_version_id':price_version_id,
						'base': price_type_id[0],
						}
			product_pricelist_item_id=self.pool.get('product.pricelist.item').create(cr,uid,product_pricelist_item)
			return pricelist_id
		else:
			return -1

	def _get_journal_code(self, cr, uid,string,sep=' '):
		tl = []
		for t in string.split(sep):
			tl.append(t.title()[0])
		code=''.join(tl)
		code=code[0:3]
		is_exist=self.pool.get('account.journal').search(cr, uid, [('code', '=',code)])
		if is_exist:
			for i in range(99):
				is_exist=self.pool.get('account.journal').search(cr, uid, [('code', '=',code+str(i))])
				if not is_exist:
					return code+str(i)[-5:]
		return code
	
	def _get_journal_name(self, cr, uid,string):
		is_exist=self.pool.get('account.journal').search(cr, uid, [('name', '=',string)])
		if is_exist:
			for i in range(99):
				is_exist=self.pool.get('account.journal').search(cr, uid, [('name', '=',string+str(i))])
				if not is_exist:
					return string+str(i)
		return string

	def _get_virtual_product_id(self,cr,uid,data):
		ir_values = self.pool.get('ir.values')
		erp_product_id = False
		if data['name'].startswith('S'):
			erp_product_id = ir_values.get_default(cr, SUPERUSER_ID, 'product.product', 'pob_delivery_product')
		if data['name'].startswith('D'):
			erp_product_id = ir_values.get_default(cr, SUPERUSER_ID, 'product.product', 'pob_discount_product')
		if not erp_product_id:
			temp_dic={'sale_ok':False,'name':data.get('name'),'type':'service','description_sale':'','list_price':0.0,}
			object_name = ''
			if data['name'].startswith('S'):
				object_name = 'pob_delivery_product'
				temp_dic['description']='Service Type product used by POB for Shipping Purposes'
			if data['name'].startswith('D'):
				object_name = 'pob_discount_product'
				temp_dic['description']='Service Type product used by POB for Discount Purposes'
			erp_product_id=self.pool.get('product.product').create(cr,uid,temp_dic)
			ir_values.set_default(cr, SUPERUSER_ID, 'product.product',object_name,erp_product_id)
			cr.commit()
		return erp_product_id

	def create_payment_method(self, cr, uid,data,context=None):
		if context is None: context = {}
		res = self.pool.get('account.journal').search(cr, uid, [('type', '=','bank')], limit=1)[0]
		credit_account_id=self.pool.get('account.journal').browse(cr,uid,res).default_credit_account_id.id
		debit_account_id=self.pool.get('account.journal').browse(cr,uid,res).default_debit_account_id.id
		journal = {
					   'name': self._get_journal_name(cr,uid,data.get('name')),
					   'code': self._get_journal_code(cr,uid,data.get('name')),
					   'type': 'cash',
					   #'company_id': 1,
					   #'user_id':1,
					   'default_credit_account_id':credit_account_id,
					   'default_debit_account_id':debit_account_id,
					  	}
		journal_id=self.pool.get('account.journal').create(cr,uid,journal)
		return journal_id

	def order_shipped(self,cr,uid,order_id,context=None):
		"""Shipped an order by any service like xmlrpc.
		@param order_id: OpenERP Order ID
		@param context: A standard dictionary
		@return: True
		"""
		if context is None:
			context = {}
		# ir_values=self.pool.get('ir.values')	
		data = self.pool.get('sale.order').read(cr,uid,order_id,['state'])
		state = data['state']
		if state == 'draft':
			self.pool.get('sale.order').action_button_confirm(cr, uid, [order_id], context=None)
			
		context['prestashop'] = 'prestashop'
		order_name=self.pool.get('sale.order').name_get(cr,uid,order_id)
		pick_id = self.pool.get('stock.picking').search(cr, uid,[('origin','=',order_name[0][1])])
		if pick_id:
			config_values=self.pool.get('prestashop.configure').search(cr, uid,[('active','=',True)])
			if config_values:
				self.pool.get('prestashop.configure').write(cr, uid,active_id[0],{'active':False})
			# for line in self.pool.get('stock.picking').browse(cr, uid, pick_id[0]).move_lines:
			# 	self.pool.get('stock.move').action_done(cr, uid, [line.id], context)
			self.pool.get('stock.picking').do_transfer(cr, uid, pick_id, context)
			if config_values:
				self.pool.get('prestashop.configure').write(cr, uid,active_id[0],{'active':True})
			workflow.trg_validate(uid, 'sale.order',order_id, 'ship_end', cr)
		return True

	def create_order_invoice(self,cr,uid,order_id,context=None):
		"""Create an order Invoice by any service like xmlrpc.
		@param order_id: OpenERP Order ID
		@param context: A standard dictionary
		@return: OpenERP Invoice ID
		"""
		if context is None:
			context = {}
		context['prestashop']='prestashop'
		active_id=self.pool.get('prestashop.configure').search(cr, uid,[('active','=',True)])
		if active_id:
			self.pool.get('prestashop.configure').write(cr, uid,active_id[0],{'active':False})
		inv_ids = self.pool.get('sale.order').manual_invoice(cr,uid,[order_id],context)
		invoice_id = inv_ids['res_id']
		if context.has_key('invoice_date'):
			self.pool.get('account.invoice').write(cr,uid,invoice_id,{'date_invoice':context.get('invoice_date',False),'date_due':context.get('invoice_date',False)})			
		workflow.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
		if active_id:
			self.pool.get('prestashop.configure').write(cr, uid,active_id[0],{'active':True})
		return invoice_id

	def update_quantity(self,cr,uid,data,context=None):
		""" Changes the Product Quantity by making a Physical Inventory through any service like xmlrpc.
		@param data: Dictionary of product_id and new_quantity
		@param context: A standard dictionary
		@return: True
		"""
		if context is None:
			context = {}
		context['prestashop']='prestashop'
		rec_id = data.get('product_id')
		assert rec_id, _('Active ID is not set in Context')
		if int(data.get('new_quantity')) < 0:
			raise osv.except_osv(_('Warning!'), _('Quantity cannot be negative.'))
		if int(data.get('new_quantity')) == 0:
			return True
		inventory_obj = self.pool.get('stock.inventory')
		inventory_line_obj = self.pool.get('stock.inventory.line')
		prod_obj_pool = self.pool.get('product.product')
		res_original = prod_obj_pool.browse(cr, uid, rec_id, context=context)
		if int(data.get('new_quantity'))==int(res_original.qty_available):
			return True
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if config_id:
			location_id = self.pool.get('prestashop.configure').browse(cr,uid,config_id[0]).pob_default_stock_location.id
		else:
			location_id = self.pool.get('stock.location').search(cr, uid, [('name','=','Stock')])
			location_id = location_id[0]
		if location_id:
			th_qty = res_original.qty_available
			inventory_id = inventory_obj.create(cr, uid, {
			            'name': _('INV: %s') % tools.ustr(res_original.name),
			            'product_id': rec_id,
			            'location_id': location_id
		            }, context=context)
			line_data = {
		        'inventory_id': inventory_id,
		        'product_qty': data.get('new_quantity'),
		        'location_id': location_id,
		        'product_id': rec_id,
		        'product_uom_id': res_original.uom_id.id,
		        'theoretical_qty': th_qty
			}
			inventory_line_obj.create(cr, uid, line_data, context=context)
			inventory_obj.action_done(cr, uid, [inventory_id], context=context)
		else:
			return "Sorry, Default Stock Location not found!!!"
		return True

	def order_paid(self, cr, uid, payment,context=None):
		"""
		@param payment: List of invoice_id, reference, partner_id ,journal_id and amount
		@param context: A standard dictionary
		@return: True
		"""
		if context is None:
			context = {}
		context['prestashop']='prestashop'

		sale_obj = self.pool.get('sale.order')
		voucher_obj = self.pool.get('account.voucher')
		voucher_line_obj = self.pool.get('account.voucher.line')
		partner_id=payment.get('partner_id')
		journal_id=payment.get('journal_id',False)
		order_id=payment.get('order_id',False)
		invoice_id=0
		date =False
		if order_id:
			sale_data = sale_obj.read(cr,uid,order_id,['invoice_exists','invoice_ids','date_order','state'])
			date=sale_data['date_order']
			if not sale_data['invoice_exists']:
				if sale_data['state'] in ['draft','sent']:
					workflow.trg_validate(uid, 'sale.order',order_id, 'order_confirm', cr)
				invoice_id=self.create_order_invoice(cr,uid,order_id,context)
			elif sale_data['invoice_ids']:
				invoice_id = sale_data['invoice_ids'][0]
			else:
				invoice_id = payment.get('invoice_id',0)
		else:
			invoice_id = payment.get('invoice_id',0)
		if invoice_id==0:
			return False
		if not journal_id:
			journal_id=self._get_journal_id(cr,uid,context)
		if isinstance(payment.get('amount'),str):
			amount=float(payment.get('amount'))
		else:
			amount=payment.get('amount')
		if not date:
			date=time.strftime('%Y-%m-%d')
		entry_name=payment.get('reference')
		data = voucher_obj.onchange_partner_id(cr, uid, [], partner_id, journal_id,amount, False, 'receipt', date, context)['value']
		invoice_obj=self.pool.get('account.invoice').browse(cr,uid,invoice_id)
		invoice_name=invoice_obj.number
		for line_cr in data.get('line_cr_ids'):
			if line_cr['name']==invoice_name:
				amount=line_cr['amount_original']
		account_id = data['account_id']
		default_data = voucher_obj.default_get(cr, uid, ['company_id'])

		statement_vals = {
                        'reference': invoice_name+'('+entry_name+')',
                        'journal_id': journal_id,
                        'amount': amount,
                        'date' : date,
                        'partner_id': partner_id,
                        'company_id': default_data.get('company_id',False),
                        'account_id': account_id,
                        'type': 'receipt',
                         }
		if data.get('payment_rate_currency_id'):
			statement_vals['payment_rate_currency_id'] = data['payment_rate_currency_id']
			company_currency_id=self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id
			if company_currency_id<>data['payment_rate_currency_id']:
				statement_vals['is_multi_currency']=True
		if data.get('paid_amount_in_company_currency'):
			statement_vals['paid_amount_in_company_currency'] = data['paid_amount_in_company_currency']
		if data.get('writeoff_amount'):
			statement_vals['writeoff_amount'] =data['writeoff_amount']
		if data.get('pre_line'):
			statement_vals['pre_line'] = data['pre_line']
		if data.get('payment_rate'):
			statement_vals['payment_rate'] = data['payment_rate']
		statement_id = voucher_obj.create(cr, uid, statement_vals, context)
		for line_cr in data.get('line_cr_ids'):
			line_cr.update({'voucher_id':statement_id})
			if line_cr['name']==invoice_name:
				line_cr['amount']=line_cr['amount_original']
				line_cr['reconcile']=True
			line_cr_id=self.pool.get('account.voucher.line').create(cr,uid,line_cr)
		for line_dr in data.get('line_dr_ids'):
			line_dr.update({'voucher_id':statement_id})
			line_dr_id=self.pool.get('account.voucher.line').create(cr,uid,line_dr)

		self.pool.get('account.voucher').button_proforma_voucher(cr, uid, [statement_id], context=context)
		workflow.trg_validate(uid, 'sale.order',order_id, 'invoice_end', cr)
		return True

	def order_cancel(self, cr, uid, order_id, context=None):
		if context is None:
			context = {}
		obj = self.pool.get('sale.order').browse(cr, uid, order_id)
		if obj.shipped == False:
			try:
				search_id = self.pool.get('account.invoice').search(cr, uid,[('origin','=',obj.name)])
				if search_id:
					invoice_obj = self.pool.get('account.invoice').browse(cr, uid, search_id)
					c_id = invoice_obj[0].journal_id.id
					self.pool.get('account.journal').write(cr, uid, c_id,{'update_posted':True})
				paid_id = self.pool.get('account.invoice').search(cr, uid,[('state','=','paid'),('origin','=',obj.name)])
				if paid_id:
					invoice_obj = self.pool.get('account.invoice').browse(cr, uid, paid_id)
					for i in invoice_obj[0].payment_ids:
						num = i.name
					sr_id = self.pool.get('account.voucher').search(cr, uid,[('move_ids.name','=',num)])
					inv_obj = self.pool.get('account.voucher').browse(cr, uid, sr_id)
					j_id = inv_obj[0].journal_id.id
					self.pool.get('account.journal').write(cr, uid, j_id,{'update_posted':True})
					self.pool.get('account.voucher').cancel_voucher(cr, uid, sr_id, context=None)
				self.pool.get('account.invoice').action_cancel(cr, uid, search_id, context)
				s_id = self.pool.get('stock.picking').search(cr, uid,[('origin','=',obj.name)])
				if s_id:
					self.pool.get('stock.picking').action_cancel(cr, uid, s_id, context)
				self.pool.get('sale.order').action_cancel(cr, uid, [order_id], context)
			except Exception,e:
				pass
		else:
			raise osv.except_osv(_('Error!'),_('Cannot Cancel a Shipped Order'))
		return True

	def create_n_confirm_order(self,cr,uid,order_data,line_data,context=None):
		if context is None:
			context = {}
		return_array={}
		if order_data and line_data:
			order_dic={
				'partner_id'			:order_data['partner_id'],
				'partner_invoice_id'	:order_data['partner_invoice_id'],
				'partner_shipping_id'	:order_data['partner_shipping_id'],
				'pricelist_id'			:order_data['pricelist_id'],
				'carrier_id'			:order_data['carrier_id'],
                'order_policy'          :'manual',     
				'origin'				:'PrestaShop'+'('+order_data['presta_order_reference']+')',
				'channel'				:'prestashop',
				}
			# if order_data.has_key('invoice_date'):

				# context['invoice_date']=order_data.get('invoice_date',False)
			if order_data.has_key('date_add'):	
				order_dic['date_order']=order_data.get('date_add',False)
				# order_dic['date_confirm']=order_data.get('date_upd',False)
				order_dic['date_confirm']=order_data.get('date_add',False)
				context['invoice_date']=order_data.get('date_add',False)
			if order_data.get('shop_id'):
				order_dic.update({'shop_id':order_data['shop_id']})
			order_id=self.pool.get('sale.order').create(cr,uid,order_dic)
			if order_id:
				for line in line_data:
					if line.get('type').startswith('S'):
						erp_product_id=self._get_virtual_product_id(cr,uid,{'name':'Shipping'})
					if line.get('type').startswith('V'):
						erp_product_id=self._get_virtual_product_id(cr,uid,{'name':'Discount'})
					if line.get('type').startswith('P'):
						erp_product_id=line['product_id']
					line_dic={
					'order_id'				:order_id,
					'product_id'			:erp_product_id,
					'price_unit'			:line['price_unit'],
					'product_uom_qty'		:line['product_uom_qty'],
					'name'					:_unescape(line['name']),
					'discount'				:line.get('discount',False),
					}
					if line.get('tax_id') and int(line.get('tax_id'))!=-1:
						line_dic['tax_id']=[(6,0,[line.get('tax_id')])]
					else:
						line_dic['tax_id'] = False
					line_id=self.pool.get('sale.order.line').create(cr,uid,line_dic)
					erp_product_id=False
				
				order_erp=self.pool.get('sale.order').read(cr,uid,order_id,['name','amount_total'])
				order_name=order_erp['name']
				erp_total=order_erp['amount_total']
				cr.execute("INSERT INTO prestashop_order (erp_id, presta_id, object_name,name) VALUES (%s, %s, %s, %s)", (order_id, order_data['presta_order_id'], 'order',order_name+'('+order_data['presta_order_reference']+')'))
				cr.commit()
				# invoice_id='0'
				# if int(round(float(erp_total)))==int(round(float(order_data['ps_total']))):
					# workflow.trg_validate(uid, 'sale.order',order_id, 'order_confirm', cr)
					# invoice_id=self.create_order_invoice(cr,uid,order_id,context)
			return [{'erp_order_id':order_id,'prst_order_id':order_data['presta_order_id'],'erp_order_name':order_name,'erp_total':erp_total,'ps_total':order_data['ps_total']}]