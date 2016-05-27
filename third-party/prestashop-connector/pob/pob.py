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
from openerp import tools
from openerp.tools.translate import _
import prestapi
from prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError

try:
	from openerp.loglevels import ustr as pob_decode
except:
	from openerp.tools.misc import ustr as pob_decode

def _unescape(text):
	##
	# Replaces all encoded characters by urlib with plain utf8 string.
	#
	# @param text source text.
	# @return The plain text.
	from urllib import unquote_plus
	return unquote_plus(text.encode('utf8'))

############## PrestaShop Information class #################
class prestashop_configure(osv.osv):			
	_name="prestashop.configure"
	
	def create(self, cr, uid, vals, context=None):	
		active_ids=self.pool.get('prestashop.configure').search(cr, uid, [('active','=',True)])	
		if vals['active'] is True:	
			if active_ids:
				raise osv.except_osv(_('Error'), _("Sorry, Only one active connection is allowed."))
			# else:
			# 	vals['default_lang_code']=self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.lang
			# 	vals['default_lang_name']=self.pool.get('res.lang').search(cr, uid,[('code', '=',vals['default_lang_code'])])[0]
		if vals.has_key('api_key'):
			vals['api_key']=vals['api_key'].strip()
		if vals.has_key('api_url'):
			if not vals['api_url'].endswith('/'):
				vals['api_url'] += '/'
			if not vals['api_url'].endswith('api/'):
				raise osv.except_osv(_('Warning!'), _("Root url must in the format ( base url of your prestashop + 'api' )"))
		return super(prestashop_configure, self).create(cr, uid, vals, context=context)
	
	def write(self, cr, uid, ids, vals, context=None):		
		active_ids=self.pool.get('prestashop.configure').search(cr, uid, [('active','=',True)])	
		if vals.has_key('active'):
			if vals['active'] is True:
				if len(active_ids)>1:
					raise osv.except_osv(_('Error'), _("Sorry, Only one active connection is allowed."))
		if vals.has_key('api_key'):
			vals['api_key']=vals['api_key'].strip()
		if vals.has_key('api_url'):
			if not vals['api_url'].endswith('/'):
				vals['api_url'] += '/'
			if not vals['api_url'].endswith('api/'):
				raise osv.except_osv(_('Warning!'), _("Root url must in the format ( base url of your prestashop + 'api' )"))
		return super(prestashop_configure, self).write(cr, uid, ids, vals, context=context)

	def _get_default_lang(self, cr, uid, context=None):
		lang = self.pool.get('res.users').browse(cr, uid, uid, context=context).lang
		lang_ids = self.pool.get('res.lang').search(cr, uid,[('code', '=',lang)])
		if not lang_ids:
		    raise osv.except_osv(_('Error!'), _('There is no default language for the current user\'s company!'))
		return lang_ids[0]

	def _get_default_category(self, cr, uid, context=None):
		cat_ids = self.pool.get('product.category').search(cr, uid,[])
		if not cat_ids:
		    raise osv.except_osv(_('Error!'), _('There is no category found on your Openerp ! Please create one.'))
		return cat_ids[0]

	def _get_default_location(self, cr, uid, context=None):
	    location_ids = self.pool.get('stock.location').search(cr, uid, [('usage', '=','internal')], context=context)
	    if not location_ids:
	        return False
	    return location_ids[0]


	def _get_list(self, cr, uid,context=None):
		try:
			return_list=[]
			config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
			if not config_id:
				raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
			if len(config_id)>1:
				raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
			else:
				obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
				url=obj.api_url
				key=obj.api_key
				try:
					prestashop = PrestaShopWebServiceDict(url,key)
				except PrestaShopWebServiceError, e:
					raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
				if prestashop:
					languages=prestashop.get('languages',options={'display': '[id,name]','filter[active]': '1'})
					if languages.has_key('languages'):
						languages = languages['languages']
					if type(languages['language'])==list:
						for row in languages['language']:
							return_list.append((row['id'],row['name']))
					else:
						return_list.append((languages['language']['id'],languages['language']['name'])) 
					return return_list
		except:
			return []

	_columns = {
		'api_url': fields.char('Root URL',size=100,help="e.g:-'http://localhost:8080/api'"),
		'api_key':fields.char('Authentication key',size=100,help="32 bit key like:-'BVWPFFYBT97WKM959D7AVVD0M4815Y1L'"),	
		'active':fields.boolean('Active'),			
		'pob_default_lang': fields.many2one('res.lang', 'Default Language', required=True),
		'pob_default_lang_code': fields.related('pob_default_lang', 'code', type="char", string="Language Locale Code", relation='res.lang',),
		'pob_default_stock_location': fields.many2one('stock.location', 'Stock Location',domain=[('usage', '=','internal')], required=True),
		'pob_default_category': fields.many2one('product.category', 'Default Category', required=True),
		'ps_language_id': fields.selection(_get_list, 'Prestashop Language'),

	}

	def refresh_list(self, cr, uid, ids, context=None):
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'pob', 'prestashop_configure_form')
		view_id = view_ref and view_ref[1] or False,

		return {
				'type': 'ir.actions.act_window',
	            'name': _('POB Configuration'),
	            'res_model': 'prestashop.configure',
	            'res_id': ids[0],
	            'view_type': 'form',
	            'view_mode': 'form',
	            'view_id': view_id,
	            'target': 'current',
	            'nodestroy': True,
				}

	
	def test_connection(self,cr,uid,ids,context=None):
		flag=0
		message="<h2>Connected successfully...you can start syncing data now.</h2>"
		extra_message=""
		try:
			obj = self.browse(cr,uid,ids[0])
			url = obj.api_url
			key = obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
				languages = prestashop.get("languages",options={'filter[active]':'1',})
				if languages.has_key('languages'):
					languages = languages['languages'] 
				if languages.has_key('language'):
					if type(languages['language'])==list:
						extra_message = 'Currently you have %s languages active on your Prestashop. Please use, use our POB Extension for MultiLanguage, in order to synchronize language wise.'%str(len(languages['language']))
			except Exception,e:
				message='Connection Error: '+str(e)+'\r\n'
				try:
					from prestapi import requests
					from lxml import etree
					client = requests.session()
					client.auth=(key, '')
					response=client.request('get',url)
					msg_tree=etree.fromstring(response.content)
					for element in msg_tree.xpath("//message"):
						message=message+element.text
				except Exception,e:
					message='\r\n'+message+str(e)
		except:
			message=reduce(lambda x, y: x+y,traceback.format_exception(*sys.exc_info()))
			#error_message= "Error :- \rFault Line No   - %s \r\nFault Message - %s"%(sys.exc_traceback.tb_lineno,sys.exc_value)
			#__log__.critical(error_message)
		finally:
			#__log__.info(message)
			message = message + '<br />' + extra_message
			partial_id = self.pool.get('pob.message').create(cr, uid, {'text':message}, context=context)
			return {
						'name':_("Test Result"),
						'view_mode': 'form',
						'view_id': False,
						'view_type': 'form',
						'res_model': 'pob.message',
						'res_id': partial_id,
						'type': 'ir.actions.act_window',
						'nodestroy': True,
						'target': 'new',
						'domain': '[]',
						'context': context
					}
		
	_defaults = {		
		'pob_default_stock_location': _get_default_location,
		'pob_default_lang': _get_default_lang,
		'pob_default_category': _get_default_category,
		'ps_language_id': _get_list,
	}
prestashop_configure()

############## PrestaShop Synchronization class #################
class prestashoperp_sync_now(osv.osv):			
	_name="prestashoperp.sync.now"

	def get_context_from_config(self, cr, uid, ids, context=None):
		ctx = {}
		config_id = self.pool.get('prestashop.configure').search(cr, uid, [('active','=',True)])[0]
		config_obj = self.pool.get('prestashop.configure').browse(cr, uid, config_id)
		lang = config_obj.pob_default_lang.code
		ctx['lang'] = config_obj.pob_default_lang.code
		ctx['location'] = config_obj.pob_default_stock_location.id
		return ctx		

	def _get_link_rewrite(self,cr,uid,zip,string):
		if type(string)!=str:
			string =string.encode('ascii','ignore')
			string=str(string)
		import re
		string=re.sub('[^A-Za-z0-9]+',' ',string)
		string=string.replace(' ','-').replace('/','-')
		string=string.lower()
		return string


	def action_multiple_synchronize_categories(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		selected_ids = context.get('active_ids')
		map=[]		
		length=0
		error_message=''
		status='yes'
		catg_map={}
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
		if len(config_id)>1:
			raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
		else:
			obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			url=obj.api_url
			key=obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
			except Exception, e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
			if prestashop:
				for l in selected_ids:
					check_in_merge_table=self.pool.get('prestashop.category').search(cr,uid,[('erp_category_id','=',l)])			 
					if not check_in_merge_table:
						length=length+1
						p_cat_id=self.sync_categories(cr,uid,prestashop,l,1,{'err_msg':''})[0]
					if status=='yes':
						error_message="%s Category(s) has been Exported to PrestaShop."%(length)
					if length == 0:
						error_message="Selected category(s) already synchronized with Prestashop."					
				partial_id = self.pool.get('pob.message').create(cr, uid, {'text':error_message}, context=context)
				return {
						'name':_("Message"),
						'view_mode': 'form',
						'view_id': False,
						'view_type': 'form',
						'res_model': 'pob.message',
						'res_id': partial_id,
						'type': 'ir.actions.act_window',
						'nodestroy': True,
						'target': 'new',
						'domain': '[]',
						'context': context
					}		


	def update_prest_categories(self,cr,uid,ids,context=None):		
		length=0
		error_message=''
		status='yes'
		catg_map={}
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
		if len(config_id)>1:
			raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
		else:
			obj = self.pool.get('prestashop.configure').browse(cr, uid, config_id[0])
			url = obj.api_url
			key = obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
			except Exception, e:
				raise osv.except_osv(_('Error'), _("Message:  %s")%str(e))
			try:
				add_data = prestashop.get('products', options={'schema': 'blank'})
			except Exception,e:
				raise osv.except_osv(_('Error'), _("Message:  %s")%str(e))
			if prestashop:			
				need_update_id=self.pool.get('prestashop.category').search(cr,uid,[('need_sync','=','yes')])
				if need_update_id:
					length=len(need_update_id)
					cc_obj=self.pool.get('prestashop.category')
					for m in need_update_id:
						presta_id=cc_obj.browse(cr,uid,m).presta_category_id
						erp_id=cc_obj.browse(cr,uid,m).erp_category_id
						response=self.export_update_cats(cr,uid,prestashop,erp_id,presta_id,m)					
					error_message="%s Category(s) has been Updated in PrestaShop."%(length)									
				if not need_update_id:
					error_message = "No Update Required !!!"				
				partial = self.pool.get('pob.message').create(cr, uid, {'text':error_message})
				return { 'name':_("Message"),
								 'view_mode': 'form',
								 'view_id': False,
								 'view_type': 'form',
								'res_model': 'pob.message',
								 'res_id': partial,
								 'type': 'ir.actions.act_window',
								 'nodestroy': True,
								 'target': 'new',
								 'domain': '[]',								 
							 }	


	def sync_categories(self,cr,uid,prestashop,cat_id,active='1',context=None):
		if context is None:
			context={}
		check=self.pool.get('prestashop.category').get_id(cr,uid,'prestashop',cat_id)
		if not check:
			obj_catg=self.pool.get('product.category').browse(cr,uid,cat_id)
			#name=obj_catg.name.encode('ascii','ignore')
			name=pob_decode(obj_catg.name)
			if obj_catg.parent_id.id:
				p_cat_id=self.sync_categories(cr,uid,prestashop,obj_catg.parent_id.id,1,context)[0]
			else:
				get_response=self.create_categories(cr,uid,prestashop,cat_id,name,'0','2',active)
				p_cat_id=get_response[2]
				context['err_msg']+=get_response[1]
				return [p_cat_id,context['err_msg']]
			get_response=self.create_categories(cr,uid,prestashop,cat_id,name,'0',p_cat_id,active)
			p_cat_id=get_response[2]
			context['err_msg']+=get_response[1]
			return [p_cat_id,context['err_msg']]
		else:
			return [check,context['err_msg']]

	def export_categories(self,cr,uid,ids,context=None):
		map=[]		
		length=0
		error_message=''
		status='yes'
		catg_map={}
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
		if len(config_id)>1:
			raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
		else:
			obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			url=obj.api_url
			key=obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
			except Exception, e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
			if prestashop:
				map_id=self.pool.get('prestashop.category').search(cr,uid,[])
				for m in map_id:
					map_obj=self.pool.get('prestashop.category').browse(cr,uid,m)				
					map.append(map_obj.erp_category_id)
				erp_catg=self.pool.get('product.category').search(cr,uid,[('id','not in',map)])
				length=len(erp_catg)
				if erp_catg:
					for l in erp_catg:
						get_response=self.sync_categories(cr,uid,prestashop,l,1,{'err_msg':''})
						p_cat_id=get_response[0]
						if get_response[1].strip():
							error_message= '\r\n'+error_message+get_response[1]
				need_update_id=self.pool.get('prestashop.category').search(cr,uid,[('need_sync','=','yes')])
				if need_update_id:
					cc_obj=self.pool.get('prestashop.category')
					for m in need_update_id:
						presta_id=cc_obj.browse(cr,uid,m).presta_category_id
						erp_id=cc_obj.browse(cr,uid,m).erp_category_id
						response=self.export_update_cats(cr,uid,prestashop,erp_id,presta_id,m)
				error_message=error_message.strip()
				if not error_message:
					error_message="%s Category(s) has been Exported to PrestaShop."%(length)
				if length == 0:
					error_message="No new category(s) Found."	
				partial = self.pool.get('pob.message').create(cr, uid, {'text':error_message})
				return { 'name':_("Message"),
								 'view_mode': 'form',
								 'view_id': False,
								 'view_type': 'form',
								'res_model': 'pob.message',
								 'res_id': partial,
								 'type': 'ir.actions.act_window',
								 'nodestroy': True,
								 'target': 'new',
								 'domain': '[]',								 
							 }


	def export_update_cats(self,cr,uid,prestashop,erp_id,presta_id,map_id,context=None):
		if context is None:
			context = {}
		obj_pro=self.pool.get('product.category').browse(cr,uid,erp_id)
		if obj_pro:
			if obj_pro.name:
				name=pob_decode(obj_pro.name)
			try:
				cat_data=prestashop.get('categories', presta_id)
			except Exception,e:
				return [0,' Error in Updating Category,can`t get category data %s'%str(e)]
			if type(cat_data['category']['name']['language'])==list:
				for i in range(len(cat_data['category']['name']['language'])):
					cat_data['category']['name']['language'][i]['value']=name
					cat_data['category']['link_rewrite']['language'][i]['value']=self._get_link_rewrite(cr,uid,zip,name)
			else:
				cat_data['category']['name']['language']['value']=name
				cat_data['category']['link_rewrite']['language']['value']=self._get_link_rewrite(cr,uid,zip,name)
			a1=cat_data['category'].pop('level_depth',None)
			a2=cat_data['category'].pop('nb_products_recursive',None)
			try:
				returnid=prestashop.edit('categories',presta_id,cat_data)
			except Exception,e:
				return [0,' Error in updating Categoty(s) %s'%str(e)]
			if returnid:
				cr.execute("UPDATE prestashop_category SET need_sync='no' WHERE erp_category_id=%s"%erp_id)
				cr.commit()



	def create_categories(self,cr,uid,prestashop,oe_cat_id,name,is_root_category,id_parent,active,link_rewrite='None',description='None',meta_description='None',meta_keywords='None',meta_title='None'):
		try:
			cat_data = prestashop.get('categories', options={'schema': 'blank'})
		except Exception,e:
			return [0,'\r\nCategory Id:%s ;Error in Creating blank schema for categories.Detail : %s'%(str(oe_cat_id),str(e)),False]
		if cat_data:
			if type(cat_data['category']['name']['language'])==list:
				for i in range(len(cat_data['category']['name']['language'])):
					cat_data['category']['name']['language'][i]['value']=name
					cat_data['category']['link_rewrite']['language'][i]['value']=self._get_link_rewrite(cr,uid,zip,name)
					cat_data['category']['description']['language'][i]['value']=description
					cat_data['category']['meta_description']['language'][i]['value']=meta_description
					cat_data['category']['meta_keywords']['language'][i]['value']=meta_keywords
					cat_data['category']['meta_title']['language'][i]['value']=name
			else:
				cat_data['category']['name']['language']['value']=name
				cat_data['category']['link_rewrite']['language']['value']=self._get_link_rewrite(cr,uid,zip,name)
				cat_data['category']['description']['language']['value']=description
				cat_data['category']['meta_description']['language']['value']=meta_description
				cat_data['category']['meta_keywords']['language']['value']=meta_keywords
				cat_data['category']['meta_title']['language']['value']=name
			cat_data['category']['is_root_category']=is_root_category
			cat_data['category']['id_parent']=id_parent
			cat_data['category']['active']=active
			try:
				returnid=prestashop.add('categories', cat_data)
			except Exception,e:
				return [0,'\r\nCategory Id:%s ;Error in creating Category(s).Detail : %s'%(str(oe_cat_id),str(e)),False]
			if returnid:
				cid=returnid
				cr.execute("INSERT INTO prestashop_category (category_name, erp_category_id, presta_category_id,need_sync) VALUES (%s, %s, %s,%s)", (oe_cat_id, oe_cat_id, cid,'no'))
				cr.commit()
				add_to_presta=self.addto_prestashop_merge(cr,uid,prestashop,'erp_category_merges',{'erp_id':oe_cat_id,'presta_id':cid})
				return [1,'',cid]



	def addto_prestashop_merge(self,cr,uid,prestashop,resource,data):
		try:
			resource_data = prestashop.get(resource, options={'schema': 'blank'})
		except Exception,e:
			return [0,' Error in Creating blank schema for resource.']
		if resource_data:
			if resource=='erp_attributes_merges':
				resource_data['erp_attributes_merge'].update({
					'erp_attribute_id':data['erp_id'],
					'prestashop_attribute_id':data['presta_id'],
					'created_by':'OpenERP',
					})
				try:
					returnid=prestashop.add(resource, resource_data)
					return [1,'']
				except Exception,e:
					return [0,' Error in Creating Entry in Prestashop for Attribute.']
			if resource=='erp_attribute_values_merges':
				resource_data['erp_attribute_values_merge'].update({
					'erp_attribute_id':data['erp_attr_id'],
					'erp_attribute_value_id':data['erp_value_id'],
					'prestashop_attribute_value_id':data['presta_id'],
					'prestashop_attribute_id':data['presta_attr_id'],
					'created_by':'OpenERP',
					})
				try:
					returnid=prestashop.add(resource, resource_data)
					return [1,'']
				except Exception,e:
					return [0,' Error in Creating Entry in Prestashop for Attribute Value.']
			if resource=='erp_product_merges':
				resource_data['erp_product_merge'].update({
					'erp_product_id':data['erp_id'],
					'erp_template_id':data['erp_temp_id'],
					'prestashop_product_id':data['presta_id'],
					'prestashop_product_attribute_id':data.get('prestashop_product_attribute_id','0'),
					'created_by':'OpenERP',
					})
				try:
					returnid=prestashop.add(resource, resource_data)
					return [1,'']
				except Exception,e:
					return [0,' Error in Creating Entry in Prestashop for Product.']
			if resource=='erp_product_template_merges':
				resource_data['erp_product_template_merge'].update({
					'erp_template_id':data['erp_id'],
					'ps_product_id':data['presta_id'],
					'created_by':'OpenERP',
					})
				try:
					returnid=prestashop.add(resource, resource_data)
					return [1,'']
				except Exception,e:
					return [0,' Error in Creating Entry in Prestashop for Template.']
			if resource=='erp_category_merges':
				resource_data['erp_category_merge'].update({
					'erp_category_id':data['erp_id'],
					'prestashop_category_id':data['presta_id'],
					'created_by':'OpenERP',
					})
				try:
					returnid=prestashop.add(resource, resource_data)
					return [1,'']
				except Exception,e:
					return [0,' Error in Creating Entry in Prestashop for Category.']
			if resource=='erp_customer_merges':
				resource_data['erp_customer_merge'].update({
					'erp_customer_id':data['erp_id'],
					'prestashop_customer_id':data['presta_id'],
					'created_by':'OpenERP',
					})
				try:
					returnid=prestashop.add(resource, resource_data)
					return [1,'']
				except Exception,e:
					return [0,' Error in Creating Entry in Prestashop for Customer.']
			if resource=='erp_address_merges':
				resource_data['erp_address_merge'].update({
					'erp_address_id':data['erp_id'],
					'prestashop_address_id':data['presta_id'],
					'id_customer':data['presta_cust_id'],
					'created_by':'OpenERP',
					})
				try:
					returnid=prestashop.add(resource, resource_data)
					return [1,'']
				except Exception,e:
					return [0,' Error in Creating Entry in Prestashop for Customer.']
		return [0,' Unknown Error in Creating Entry in Prestashop.']



	def action_multiple_synchronize_products(self,cr,uid,ids,context=None):
		if context is None:
			context={}
		message = ''
		count = 0		
		need_to_export = []
		prod_obj = self.pool.get('product.product')
		selected_ids = context.get('active_ids')		
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
		if len(config_id)>1:
			raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
		else:					
			obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			url=obj.api_url
			key=obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)				
			except Exception, e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
			if prestashop:
				product_bs = prestashop.get('products', options={'schema': 'blank'})
				combination_bs = prestashop.get('combinations', options={'schema': 'blank'})
				context = self.get_context_from_config(cr, uid, ids)
				for j in selected_ids:
					check = self.pool.get('prestashop.product').search(cr,uid,[('erp_product_id','=',j)])
					if not check:
						need_to_export.append(j)
				if len(need_to_export)==0:
					message = 'Selected product(s) are already exported to Prestashop.'
				for erp_product_id in need_to_export:
					response = self.export_product(cr,uid,prestashop,product_bs,combination_bs,erp_product_id,context)
					if response[0]>0:
						count = count+1
			message = message+ '\r\n'+'%s products has been exported to Prestashop .\r\n'%(count)			
		
		partial_id = self.pool.get('pob.message').create(cr, uid, {'text':message}, context=context)
		return { 'name':_("Message"),
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
		

	def export_all_products(self,cr,uid,ids,context=None):
		if context is None:
			context={}
		message = ''		
		count = 0
		map = []
		prod_obj = self.pool.get('product.product')		
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
		if len(config_id)>1:
			raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
		else:					
			obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			url=obj.api_url
			key=obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)				
			except Exception, e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
			if prestashop:
				product_bs = prestashop.get('products', options={'schema': 'blank'})
				combination_bs = prestashop.get('combinations', options={'schema': 'blank'})
				already_mapped=self.pool.get('prestashop.product').search(cr,uid,[])
				for m in already_mapped:
					map_obj=self.pool.get('prestashop.product').browse(cr,uid,m)				
					map.append(map_obj.erp_product_id)
				need_to_export=prod_obj.search(cr,uid,[('id','not in',map),('type','not in',['service'])])				
				if len(need_to_export)==0:
					message = 'Nothing to Export. All product(s) are already exported to Prestashop.'
				else:
					context = self.get_context_from_config(cr, uid, ids)
				for erp_product_id in need_to_export:
					response = self.export_product(cr,uid,prestashop,product_bs,combination_bs,erp_product_id,context)
					if response[0]>0:
						count = count+1
			message = message+ '\r\n'+'%s products has been exported to Prestashop .\r\n'%(count)		
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

	def export_product(self,cr,uid,prestashop,product_bs,combination_bs,erp_product_id,context=None):
		if context is None:
			context={}
		message = ''
		is_error = False
		template_obj = self.pool.get('prestashop.product.template')
		prod_obj = self.pool.get('product.product')
		product_data = prod_obj.browse(cr,uid,erp_product_id,context)
		if product_data.product_tmpl_id:
			erp_template_id = product_data.product_tmpl_id.id			
			check = template_obj.search(cr,uid,[('erp_template_id','=',erp_template_id)])
			if check:
				ps_template_id = template_obj.browse(cr,uid,check[0]).presta_product_id				
			else:
				response = self.export_template(cr,uid,prestashop,product_bs,erp_template_id,context)
				if response[0]>0:
					ps_template_id = response[0]			
				else:
					return response[1]
			if product_data.attribute_line_ids:
				response_combination = self.create_combination(cr,uid,prestashop,combination_bs,ps_template_id,product_data.product_tmpl_id.id,erp_product_id,context)	
				return response_combination
			else:				
				response_update = self.create_normal_product(cr,uid,prestashop,erp_template_id,erp_product_id,ps_template_id,context)				
				return response_update

	def export_template(self,cr,uid,prestashop,product_bs,erp_template_id,context=None):
		if context is None:
			context={}
		obj_template = self.pool.get('product.template')		
		template_data = obj_template.browse(cr, uid, erp_template_id, context)
		cost = template_data.standard_price
		erp_category_id = template_data.categ_id.id
		presta_default_categ_id=self.sync_categories(cr,uid,prestashop,erp_category_id,1,{'err_msg':''})[0]
		product_bs['product'].update({
						'price': str(template_data.list_price),
						'active':'1',
						'redirect_type':'404',
						'minimal_quantity':'1',
						'available_for_order':'1',
						'show_price':'1',
						'out_of_stock':'2',
						'condition':'new',									
						'id_category_default':str(presta_default_categ_id)	 
	                    })
		if cost:
			product_bs['product']['wholesale_price']= str(cost)
		if type(product_bs['product']['name']['language'])==list:
			for i in range(len(product_bs['product']['name']['language'])):
				product_bs['product']['name']['language'][i]['value']=template_data.name
				product_bs['product']['link_rewrite']['language'][i]['value']=self._get_link_rewrite(cr,uid,'',template_data.name)
				product_bs['product']['description']['language'][i]['value']=template_data.description
				product_bs['product']['description_short']['language'][i]['value']=template_data.description_sale
		else:
			product_bs['product']['name']['language']['value']=template_data.name
			product_bs['product']['link_rewrite']['language']['value']=self._get_link_rewrite(cr,uid,'',template_data.name)
			product_bs['product']['description']['language']['value']=template_data.description
			product_bs['product']['description_short']['language']['value']=template_data.description_sale
		product_bs['product']['associations']['categories']['category']['id']=str(presta_default_categ_id)
		pop_attr=product_bs['product']['associations'].pop('combinations',None)
		a1=product_bs['product']['associations'].pop('images',None)
		a2 = product_bs['product'].pop('position_in_category',None)
		try:
			returnid=prestashop.add('products', product_bs)
		except Exception,e:
			return [0,' Error in creating Product Template(ID: %s).%s'%(str(presta_default_categ_id),str(e))]
		if returnid:
			cr.execute("INSERT INTO prestashop_product_template (template_name, erp_template_id, presta_product_id,need_sync) VALUES (%s, %s, %s,%s)", (erp_template_id, erp_template_id, returnid,'no'))
			cr.commit()
			add_to_presta=self.addto_prestashop_merge(cr,uid,prestashop,'erp_product_template_merges',{'erp_id':erp_template_id,'presta_id':returnid})
			return [returnid,'']
		return [0,'Unknown Error']



	def create_combination(self,cr,uid,prestashop,add_comb,presta_main_product_id,erp_template_id,erp_product_id,context=None):
		if context is None:
			context = {}		
		obj_pro = self.pool.get('product.product').browse(cr,uid,erp_product_id,context)
		qty = self.pool.get('product.product')._product_available(cr,uid,[erp_product_id],None,False,context)
		quantity = qty[erp_product_id]['qty_available'] - qty[erp_product_id]['outgoing_qty']
		if type(quantity) == str:
			quantity = quantity.split('.')[0]
		if type(quantity) == float:
			quantity = quantity.as_integer_ratio()[0]
		image = obj_pro.image
		if image:
			image_id = self.create_images(cr,uid,prestashop,image,presta_main_product_id)
			if image_id:
				add_comb['combination']['associations']['images']['image']['id'] = str(image_id)
		price_extra = float(obj_pro.lst_price) - float(obj_pro.list_price)
		ean13 = obj_pro.ean13 or ''
		default_code = obj_pro.default_code or ''
		weight = obj_pro.weight
		presta_dim_list = []
		for value_id in obj_pro.attribute_value_ids:
			m_id = self.pool.get('prestashop.product.attribute.value').search(cr,uid,[('erp_id','=',value_id.id)])
			if m_id:
				presta_id = self.pool.get('prestashop.product.attribute.value').browse(cr,uid,m_id[0]).presta_id
				presta_dim_list.append({'id':str(presta_id)})
			else:
				return [0,'Please synchronize all Dimensions first.']			
		add_comb['combination']['associations']['product_option_values']['product_option_value'] = presta_dim_list
		add_comb['combination'].update({
								'ean13':ean13,										
								'weight':str(weight),
								'reference':default_code,							
								'price':str(price_extra),							
								'quantity':quantity,
								'id_product':str(presta_main_product_id),
								'minimal_quantity':'1',
								})
		try:
			returnid = prestashop.add('combinations', add_comb)
		except Exception,e:
			return [0,' Error in creating Variant(ID: %s).%s'%(str(erp_product_id),str(e))]
		if returnid:
			pid = returnid
			cr.execute("INSERT INTO prestashop_product (product_name,erp_template_id,erp_product_id, presta_product_id,presta_product_attr_id,need_sync) VALUES (%s, %s, %s, %s, %s, %s)", (erp_product_id,erp_template_id,erp_product_id,presta_main_product_id,pid,'no'))

			cr.commit()
			add_to_presta = self.addto_prestashop_merge(cr,uid,prestashop,'erp_product_merges',{'erp_id':erp_product_id,'presta_id':presta_main_product_id,'prestashop_product_attribute_id':pid,'erp_temp_id':erp_template_id})
			if float(quantity) > 0.0:
				get = self.update_quantity(cr,uid,prestashop,presta_main_product_id,quantity,None,pid,context)
				return [pid,get[1]]
			return [pid,'']


	def create_normal_product(self,cr,uid,prestashop,erp_template_id,erp_product_id,prest_main_product_id,context=None):
		if context is None:
			context = {}		
		obj_product = self.pool.get('product.product')
		product_data = obj_product.browse(cr,uid,erp_product_id,context)
		erp_category_id = product_data.categ_id.id
		presta_default_categ_id=self.sync_categories(cr,uid,prestashop,erp_category_id,1,{'err_msg':''})[0]
		if prestashop:
			add_data = prestashop.get('products', prest_main_product_id)
		if add_data:
			add_data['product'].update({
								'price': str(product_data.lst_price),
								'active':'1',
								'redirect_type':'404',
								'minimal_quantity':'1',
								'available_for_order':'1',
								'show_price':'1',
								'out_of_stock':'2',
								'condition':'new',
								'reference':product_data.default_code,					 
								'id_category_default':presta_default_categ_id
							})
			a1 = add_data['product'].pop('position_in_category',None)
			a2 = add_data['product'].pop('manufacturer_name',None)
			a3 = add_data['product'].pop('quantity',None)
			a4 = add_data['product'].pop('type',None)
			try:
				returnid = prestashop.edit('products',prest_main_product_id, add_data)
			except Exception,e:
				return [0,' Error in creating Product(ID: %s).%s'%(str(erp_product_id),str(e))]			
			cr.execute("INSERT INTO prestashop_product (name,product_name,erp_template_id,erp_product_id, presta_product_id,need_sync) VALUES (%s, %s, %s, %s, %s, %s)", (product_data.name,erp_product_id,erp_template_id,erp_product_id, prest_main_product_id,'no'))
			cr.commit()
			add_to_presta=self.addto_prestashop_merge(cr,uid,prestashop,'erp_product_merges',{'erp_id':erp_product_id,'presta_id':prest_main_product_id,'erp_temp_id':erp_template_id})
			if product_data.image:
				get=self.create_images(cr,uid,prestashop,product_data.image,prest_main_product_id)
			qty = self.pool.get('product.product')._product_available(cr,uid,[erp_product_id],None,False,context)
			quantity = qty[erp_product_id]['qty_available'] - qty[erp_product_id]['outgoing_qty']
			if type(quantity) == str:
				quantity = quantity.split('.')[0]
			if type(quantity) == float:
				quantity = quantity.as_integer_ratio()[0]
			if float(quantity) > 0.0 :
				get = self.update_quantity(cr,uid,prestashop,prest_main_product_id,quantity)
			return [prest_main_product_id,'']


	def create_images(self,cr,uid,prestashop,image_data,resource_id,image_name=None,resource='images/products'):
		if image_name==None:
			image_name='op'+str(resource_id)+'.png'
		try:
			returnid=prestashop.add(str(resource)+'/'+str(resource_id),image_data,image_name)
			return returnid
		except Exception,e:
			return False


	def update_product_prestashop(self,cr,uid,ids,context=None):
		if context is None:
			context={}
		message = ''
		error_message = ''
		update = 0		
		map = []
		prod_obj = self.pool.get('product.product')
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
			except Exception, e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
			if prestashop:					
				need_update_id=self.pool.get('prestashop.product').search(cr,uid,[('need_sync','=','yes')])
				if len(need_update_id)==0:
					message = 'Nothing to Update. All product(s) are already updated to Prestashop.'
				else:
					context = self.get_context_from_config(cr, uid, ids)
					context['ps_language_id'] = obj.ps_language_id
				if need_update_id:
					pp_obj=self.pool.get('prestashop.product')
					for m in need_update_id:
						attribute_id = pp_obj.browse(cr,uid,m).presta_product_attr_id
						presta_id = pp_obj.browse(cr,uid,m).presta_product_id	
						erp_id = pp_obj.browse(cr,uid,m).erp_product_id
						if int(attribute_id) >= 0 and int(presta_id) not in [0,-1]:
							response = self.export_update_products(cr,uid,prestashop,erp_id,presta_id,attribute_id,context)
							if response[0] == 0:								
								error_message += response[1]
							else:
								update += 1
						
					if len(error_message) == 0:
						message = message+ '\r\n'+'%s Products Successfully Updated to Prestashop .\r\n'%(update)
					else:
						message = message+ '\r\n'+'Error in Updating product(s): %s.\r\n'%(error_message)
			partial_id = self.pool.get('pob.message').create(cr, uid, {'text':message}, context=context)
			return { 'name':_("Message"),
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

	def export_update_products(self,cr,uid,prestashop,erp_id,presta_id,attribute_id,context=None):
		if context is None:
			context = {}	
		ps_option_ids = []		
		obj_pro=self.pool.get('product.product').browse(cr, uid, erp_id, context)
		if obj_pro:
			if not obj_pro.name:
				name = ''
			else:				
				name = pob_decode(obj_pro.name)
			if obj_pro.list_price:
				price = str(obj_pro.list_price)
			else:
				price = '0.00'
			categ_id = obj_pro.categ_id.id
			p_categ_id = self.sync_categories(cr,uid,prestashop,categ_id,1,{'err_msg':''})[0]
			if obj_pro.description:
				description = pob_decode(obj_pro.description)
			else:
				description = ''
			if obj_pro.description_sale:
				description_sale = pob_decode(obj_pro.description_sale)
			else:
				description_sale = ''
			qty = self.pool.get('product.product')._product_available(cr,uid,[erp_id],None,False,context)
			quantity = qty[erp_id]['qty_available'] - qty[erp_id]['outgoing_qty']
			image = obj_pro.image
			ean13 = obj_pro.ean13 or ''
			default_code = obj_pro.default_code or ''
			context['weight'] = obj_pro.weight	
			if obj_pro.attribute_value_ids:
				for value_id in obj_pro.attribute_value_ids:					
					m_id = self.pool.get('prestashop.product.attribute.value').search(cr,uid,[('erp_id','=',value_id.id)])
					if m_id:
						presta_value_id = self.pool.get('prestashop.product.attribute.value').browse(cr,uid,m_id[0]).presta_id
						ps_option_ids.append({'id':str(presta_value_id)})
					else:
						return [0,'Please synchronize all Dimensions first.']
			context['ps_option_ids'] = ps_option_ids				
			response=self.update_products(cr,uid,prestashop,erp_id,presta_id,attribute_id,name,price,quantity,p_categ_id,'new',description,description_sale,image,default_code,ean13,context)
			return response



	def update_products(self,cr,uid,prestashop,erp_id,presta_id,attribute_id,name,price,quantity,id_category_default='2',condition='new',description='None',description_short='None',image_data=False,default_code='',ean13='',context=None):
		if context is None:
			context = {}
		# message='Error in Updating Product with ERP-ID '+str(erp_id)
		message=''
		if int(presta_id) in [0,-1,-2,-3]:
			cr.execute("UPDATE prestashop_product SET need_sync='no' WHERE erp_product_id=%s"%erp_id)
			cr.commit()
		else:
			try:
				product_data=prestashop.get('products', presta_id)
			except Exception,e:
				return [0,' Error in Updating Product,can`t get product data %s'%str(e)]
			if product_data:
				if int(attribute_id)==0:
					product_data['product'].update({
										'price': price,								 
										'reference':default_code,
										'ean13':ean13									
										})
					if context.has_key('weight'):
						product_data['product']['weight']=str(context['weight'])
					if type(product_data['product']['name']['language'])==list:
						for i in range(len(product_data['product']['name']['language'])):
							presta_lang_id = product_data['product']['name']['language'][i]['attrs']['id']
							if presta_lang_id == str(context['ps_language_id']):
								product_data['product']['name']['language'][i]['value']=name
								product_data['product']['link_rewrite']['language'][i]['value']=self._get_link_rewrite(cr,uid,zip,name)
								product_data['product']['description']['language'][i]['value']=description
								product_data['product']['description_short']['language'][i]['value']=description_short
					else:
						product_data['product']['name']['language']['value']=name
						product_data['product']['link_rewrite']['language']['value']=self._get_link_rewrite(cr,uid,zip,name)
						product_data['product']['description']['language']['value']=description
						product_data['product']['description_short']['language']['value']=description_short					
					a1 = product_data['product'].pop('position_in_category',None)
					a2 = product_data['product'].pop('manufacturer_name',None)
					a3 = product_data['product'].pop('quantity',None)
					a4 = product_data['product'].pop('type',None)
					a4 = product_data['product'].pop('combinations',None)
					try:
						returnid = prestashop.edit('products',presta_id,product_data)		
					except Exception,e:
						return [0,' Error in updating Product(s) %s'%str(e)]
					if not product_data['product']['associations']['images'].has_key('image'):
						if image_data:
							get = self.create_images(cr,uid,prestashop,image_data,presta_id)
					up = True
				else:
					resp = self.update_products_with_attributes(cr,uid,prestashop,erp_id,presta_id,attribute_id,price,default_code,ean13,context)
					returnid = resp[0]
					up = False
					message = message+resp[1]
				if returnid:
					if up:
						if not context.has_key('template'):
							cr.execute("UPDATE prestashop_product SET need_sync='no' WHERE erp_product_id=%s"%(erp_id))
							cr.commit()
						# else:
						# 	cr.execute("UPDATE prestashop_product_template SET base_price=%s WHERE erp_template_id=%s"%(price,erp_id))
						# 	cr.commit()
					if type(product_data['product']['associations']['stock_availables']['stock_available'])==list:
						for data in product_data['product']['associations']['stock_availables']['stock_available']:
							if int(data['id_product_attribute'])==int(attribute_id):
								stock_id=data['id']
					else:
						stock_id=product_data['product']['associations']['stock_availables']['stock_available']['id']
					if float(quantity) > 0.0:
						return self.update_quantity(cr,uid,prestashop,presta_id,quantity,stock_id,attribute_id,context)
					else:
						return [1,'']
				else:
					return [0,message]


	def update_products_with_attributes(self,cr,uid,prestashop,erp_id,presta_id,attribute_id,new_price,reference=None,ean13=None,context=None):
		if context is None:
			context={}
		flag = True
		message = ''
		if context.has_key('ps_option_ids'):
			ps_option_ids = context['ps_option_ids']		
		try:
			attribute_data = prestashop.get('combinations', attribute_id)
		except Exception,e:
			message =' Error in Updating Product Attribute,can`t get product attribute data %s'%str(e)
			flag = False		
		map_id=self.pool.get('prestashop.product').search(cr,uid,[('erp_product_id','=',int(erp_id))])
		if flag and attribute_data and map_id:
			obj_pro = self.pool.get('product.product').browse(cr,uid,erp_id,context)
			impact_on_price=float(obj_pro.lst_price) - float(obj_pro.list_price)
			attribute_data['combination']['price']=str(impact_on_price)
			qq = attribute_data['combination']['associations'].pop('images')
			if ps_option_ids:				
				if attribute_data['combination']['associations']['product_option_values'].has_key('value'):
					a1 = attribute_data['combination']['associations']['product_option_values'].pop('value')
				if attribute_data['combination']['associations']['product_option_values'].has_key('product_option_value'):	
					a2 = attribute_data['combination']['associations']['product_option_values'].pop('product_option_value')
				a3 = attribute_data['combination']['associations']['product_option_values']['product_option_value']=[]
				for j in ps_option_ids:
					attribute_data['combination']['associations']['product_option_values']['product_option_value'].append(j)
			if reference: 
				attribute_data['combination']['reference']=reference
			if ean13:
				attribute_data['combination']['ean13']=ean13
			if context.has_key('weight'):
				attribute_data['combination']['weight']=str(context['weight'])
			try:
				returnid=prestashop.edit('combinations',attribute_id,attribute_data)
			except Exception,e:
				message =' Error in updating Product(s) %s'%str(e)
				flag =False
			if flag:
				cr.execute("UPDATE prestashop_product SET need_sync='no' WHERE erp_product_id=%s"%(erp_id))
				cr.commit()
		return [flag,message]


	def update_quantity(self,cr,uid,prestashop,pid,quantity,stock_id=None,attribute_id=None,context=None):
		if attribute_id is not None:
			try:
				stock_search=prestashop.get('stock_availables',options={'filter[id_product]':pid,'filter[id_product_attribute]':attribute_id})
			except Exception,e:
				return [0,' Unable to search given stock id',check_mapping[0]]
			if type(stock_search['stock_availables'])==dict:
				stock_id=stock_search['stock_availables']['stock_available']['attrs']['id']
				try:
					stock_data=prestashop.get('stock_availables', stock_id)
				except Exception,e:
					return [0,' Error in Updating Quantity,can`t get stock_available data.']
				if type(quantity)==str:
					quantity=quantity.split('.')[0]
				if type(quantity)==float:
					quantity=int(quantity)
				stock_data['stock_available']['quantity']=int(quantity)				
				try:
					up=prestashop.edit('stock_availables',stock_id,stock_data)
				except Exception,e:
					pass
				return [1,'']
			else:
				return [0,' No stock`s entry found in prestashop for given combination (Product id:%s ; Attribute id:%s)'%str(pid)%str(attribute_id)]
		if stock_id is None and attribute_id is None:
			try:
				product_data=prestashop.get('products', pid)
			except Exception,e:
				return [0,' Error in Updating Quantity,can`t get product data.']
			stock_id=product_data['product']['associations']['stock_availables']['stock_available']['id']
		if stock_id:			
			try:
				stock_data=prestashop.get('stock_availables', stock_id)
			except Exception,e:
				return [0,' Error in Updating Quantity,can`t get stock_available data.']
			except Exception,e:
				return [0,' Error in Updating Quantity,%s'%str(e)]
			if type(quantity)==str:
				quantity=quantity.split('.')[0]
			if type(quantity)==float:
				quantity=quantity.as_integer_ratio()[0]			
			stock_data['stock_available']['quantity']=quantity
			try:
				up=prestashop.edit('stock_availables',stock_id,stock_data)
			except Exception,e:
				return [0,' Error in Updating Quantity,Unknown Error.']
			except Exception,e:
				return [0,' Error in Updating Quantity,Unknown Error.%s'%str(e)]
			return [1,'']
		else:
			return [0,' Error in Updating Quantity,Unknown stock_id.']



	def export_attributes_and_their_values(self,cr,uid,ids,context=None):
		map=[]		
		map_dict={}	
		type=0
		value=0
		error_message=''
		status='yes'
		config_id=self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
		if len(config_id)>1:
			raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
		else:
			obj=self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			url=obj.api_url
			key=obj.api_key
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
			except Exception, e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
			try:
				add_data = prestashop.get('product_options', options={'schema': 'blank'})
			except Exception,e:
				raise osv.except_osv(_('Error %s')%str(e), _("Error in Creating blank schema for product_options"))
			try:
				add_value = prestashop.get('product_option_values', options={'schema': 'blank'})
			except Exception,e:
				raise osv.except_osv(_('Error %s')%str(e), _("Error in Creating blank schema for product_options"))
			if prestashop and add_data and add_value:
				context = self.get_context_from_config(cr, uid, ids)
				map_id=self.pool.get('prestashop.product.attribute').search(cr,uid,[])
				for m in map_id:
					map_obj=self.pool.get('prestashop.product.attribute').browse(cr,uid,m)				
					map.append(map_obj.erp_id)
					map_dict.update({map_obj.erp_id:map_obj.presta_id})
				erp_pro=self.pool.get('product.attribute').search(cr,uid,[])
				if erp_pro:
					for type_id in erp_pro:
						obj_dimen_opt = self.pool.get('product.attribute').browse(cr,uid,type_id,context)
						if type_id not in map:
							name = obj_dimen_opt.name							
							create_dim_type = self.create_dimension_type(cr,uid,prestashop,add_data,type_id,name,context)
							type+=1
						else:
							presta_id = map_dict.get(type_id)
							create_dim_type = [int(presta_id)]
						if create_dim_type[0]==0:
							status = 'no'
							error_message = error_message + create_dim_type[1]
						else:
							presta_id = create_dim_type[0]
							for value_id in obj_dimen_opt.value_ids:

								if not self.pool.get('prestashop.product.attribute.value').search(cr,uid,[('erp_id','=',value_id.id)]):
									name = self.pool.get('product.attribute.value').browse(cr,uid,value_id.id,context).name					
									create_dim_opt = self.create_dimension_option(cr,uid,prestashop,type_id,add_value,presta_id,value_id.id,name,context)
									if create_dim_opt[0]==0:
										status = 'no'
										error_message = error_message + create_dim_opt[1]
									else:
										value += 1
						
				if status == 'yes':
					error_message += " %s Dimension(s) and their %s value(s) has been created. "%(type,value)
				if not erp_pro:
					error_message = "No new Dimension(s) found !!!"
				partial = self.pool.get('pob.message').create(cr, uid, {'text':error_message})
				return {'name':_("Message"),
						'view_mode': 'form',
						'view_id': False,
						'view_type': 'form',
						'res_model': 'pob.message',
						'res_id': partial,
						'type': 'ir.actions.act_window',
						'nodestroy': True,
						'target': 'new',
						'domain': '[]',								 
					}

	def create_dimension_type(self,cr,uid,prestashop,add_data,erp_dim_type_id,name,context=None):
		if context is None:
			context = {}
		if add_data:
			add_data['product_option'].update({
										'group_type': 'select',
										'position':'0'
                                    })
			if type(add_data['product_option']['name']['language'])==list:
				for i in range(len(add_data['product_option']['name']['language'])):
					add_data['product_option']['name']['language'][i]['value']=name
					add_data['product_option']['public_name']['language'][i]['value']=name
			else:
				add_data['product_option']['name']['language']['value']=name
				add_data['product_option']['public_name']['language']['value']=name
			try:
				returnid=prestashop.add('product_options', add_data)
			except Exception,e:
				return [0,' Error in creating Dimension Type(ID: %s).%s'%(str(erp_dim_type_id),str(e))]
			if returnid:
				pid=returnid
				cr.execute("INSERT INTO prestashop_product_attribute (name,erp_id,presta_id,need_sync) VALUES (%s, %s, %s,%s)", (erp_dim_type_id, erp_dim_type_id, pid,'no'))
				cr.commit()
				add_to_presta=self.addto_prestashop_merge(cr,uid,prestashop,'erp_attributes_merges',{'erp_id':erp_dim_type_id,'presta_id':pid})
				return [pid,'']


	def create_dimension_option(self,cr,uid,prestashop,erp_attr_id,add_value,presta_attr_id,erp_dim_opt_id,name,context=None):
		if context is None:
			context = {}
		if add_value:
			add_value['product_option_value'].update({
										'id_attribute_group': presta_attr_id,
										'position':'0'
                                    })
			if type(add_value['product_option_value']['name']['language'])==list:
				for i in range(len(add_value['product_option_value']['name']['language'])):
					add_value['product_option_value']['name']['language'][i]['value']=name
			else:
				add_value['product_option_value']['name']['language']['value']=name
			try:
				returnid=prestashop.add('product_option_values', add_value)
			except Exception,e:
				return [0,' Error in creating Dimension Option(ID: %s).%s'%(str(erp_dim_opt_id),str(e))]
			if returnid:
				pid=returnid
				cr.execute("INSERT INTO prestashop_product_attribute_value (name,erp_id,presta_id,erp_attr_id,presta_attr_id,need_sync) VALUES (%s, %s, %s, %s, %s, %s)", (erp_dim_opt_id, erp_dim_opt_id, pid, erp_attr_id, presta_attr_id, 'no'))
				cr.commit()
				add_to_presta=self.addto_prestashop_merge(cr,uid,prestashop,'erp_attribute_values_merges',{'erp_value_id':erp_dim_opt_id,'presta_id':pid,'presta_attr_id':presta_attr_id,'erp_attr_id':erp_attr_id})
				return [pid,'']




	def action_multiple_synchronize_templates(self, cr, uid, ids, context=None):
		if context is None:
			context = {}		
		message = ''
		count = 0
		temp = context.get('active_ids')		
		need_to_export = []	
		exported_ids = []	
		erp_product_ids = []
		config_id = self.pool.get('prestashop.configure').search(cr,uid,[('active','=',True)])
		if not config_id:
			raise osv.except_osv(_('Error'), _("Connection needs one Active Configuration setting."))
		if len(config_id)>1:
			raise osv.except_osv(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
		else:
			obj = self.pool.get('prestashop.configure').browse(cr,uid,config_id[0])
			key = obj.api_key
			url = obj.api_url						
			try:
				prestashop = PrestaShopWebServiceDict(url,key)
			except Exception, e:
				raise osv.except_osv(_('Error %s')%str(e), _("Invalid Information"))
			for i in temp:	
				search = self.pool.get('prestashop.product.template').search(cr,uid,[('erp_template_id','=',i)])
				if search:
					exported_ids.append(i)
				else:
					need_to_export.append(i)
			context = self.get_context_from_config(cr, uid, ids)		
			if exported_ids and prestashop:	
				pp_obj = self.pool.get('prestashop.product.template')	
				for j in exported_ids:				
					need_update_id = pp_obj.search(cr, uid, [('erp_template_id','=',j)])
					presta_id = pp_obj.browse(cr,uid,need_update_id[0]).presta_product_id
					erp_id = j					
					if prestashop and need_update_id:				
						temp_obj = self.pool.get('product.template').browse(cr, uid, erp_id,context)					
						if temp_obj:							
							if not temp_obj.name:
								name='None'
							else:							
								name=temp_obj.name					
							if temp_obj.description:
								description = temp_obj.description
							else:
								description = ' '
							if temp_obj.description_sale:
								description_sale = temp_obj.description_sale
							else:
								description_sale=' '
							if temp_obj.list_price:
								price = temp_obj.list_price
							else:
								price = 0.0
							if temp_obj.weight:
								weight = temp_obj.weight
							else:
								weight = 0.000000
							if temp_obj.standard_price:
								cost = temp_obj.standard_price
							else: 
								cost = 0.0
							if temp_obj.categ_id:
								def_categ = temp_obj.categ_id.id
							else:
								raise osv.except_osv(_('Error!'),_('Template Must have a Default Category')%())		

							update = self.update_template(cr, uid, prestashop, erp_id, presta_id, name, description, description_sale, {'price':price,'weight':weight,'cost':cost, 'def_categ':def_categ})
			if need_to_export and prestashop:
				for k in self.pool.get('product.template').browse(cr, uid, need_to_export):
					for l in k.product_variant_ids:
						erp_product_ids.append(l.id)
				prod_ids = self.pool.get('product.product').search(cr,uid,[('id','in',erp_product_ids),('type','not in',['service'])])
				product_bs = prestashop.get('products', options={'schema': 'blank'})
				combination_bs = prestashop.get('combinations', options={'schema': 'blank'})
				for erp_product_id in prod_ids:
					response = self.export_product(cr,uid,prestashop,product_bs,combination_bs,erp_product_id,context)			
			message = 'Product Template(s) Updated: %s\r\nNumber of Product Template(s) Exported: %s'%(len(exported_ids),len(need_to_export))+' \r\n'+message		
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
						
					

	def update_template(self, cr, uid, prestashop, erp_id, presta_id, name, description, description_sale, context=None):
		if context is None:
			context = {}
		message=''		
		template_data = self.update_template_category(cr, uid, prestashop, erp_id, presta_id,context)	
		if template_data:			
			if context.has_key('price'):
				template_data['product']['price'] = str(context['price'])
			if context.has_key('cost'):
				template_data['product']['wholesale_price'] = str(context['cost'])			
			if context.has_key('weight'):
				template_data['product']['weight'] = str(context['weight'])
		
			if type(template_data['product']['name']['language'])==list:
				for i in range(len(template_data['product']['name']['language'])):
					template_data['product']['name']['language'][i]['value'] = 	name				
					template_data['product']['description']['language'][i]['value'] = description
					template_data['product']['description_short']['language'][i]['value'] = description_sale
			else:
				template_data['product']['name']['language']['value'] = name					
				template_data['product']['description']['language']['value'] = description
				template_data['product']['description_short']['language']['value'] = description_sale
				# template_data['product']['associations']['categories']['category']['id']=str(presta_default_categ_id)			
			a1=template_data['product'].pop('position_in_category',None)
			a2=template_data['product'].pop('manufacturer_name',None)
			a3=template_data['product'].pop('quantity',None)
			a4=template_data['product'].pop('type',None)				
			try:
				returnid=prestashop.edit('products',presta_id,template_data)
			except Exception,e:
				# raise osv.except_osv(_('Error!'),_('template_bfgbdata=%s')%(e))
				return [0,' Error in updating Template(s) %s'%str(e)]			
			if returnid:									
				cr.execute("UPDATE prestashop_product_template SET need_sync='no' WHERE template_name=%s"%(erp_id))
				cr.commit()
				return [1,'Template Successfully Updated']
								
			else:
				return [0,str(e)]

	def update_template_category(self, cr, uid, prestashop, erp_id, presta_id, context=None):
		if context is None:
			context = {}
		message=''
		count = 0
		cat_id =[]
		cat_obj = self.pool.get('prestashop.category')
		try:
			template_data = prestashop.get('products', presta_id)
		except Exception,e:
			return [0,' Error in Updating Product,can`t get product data %s'%str(e)]

		search_cat =  self.pool.get('prestashop.category').search(cr, uid, [('erp_category_id','=',context.get('def_categ'))])
		if search_cat:
			default_category = self.pool.get('prestashop.category').browse(cr, uid,search_cat[0]).presta_category_id
		else:
			resp = self.sync_categories(cr, uid, prestashop, context.get('def_categ'), active='1',context={'err_msg':''})
			default_category = resp[0]
		template_data['product'].update({																 
										'id_category_default':default_category
										})

		if type(template_data['product']['associations']['categories']['category'])==list:
			length = len(template_data['product']['associations']['categories']['category'])
			for i in range(length):
				if (template_data['product']['associations']['categories']['category'][i]['id']==str(default_category)):
					count = count+1
			if count==0:
				template_data['product']['associations']['categories']['category'].append({'id':str(default_category)})
		else:
			cat_id.append(template_data['product']['associations']['categories']['category']['id'])			
			if not (cat_id[0]==str(default_category)):
				cat_id.append(str(default_category))
				a1 = template_data['product']['associations']['categories'].pop('category')	
				a2 = template_data['product']['associations']['categories']['category']=[]
				for j in cat_id:
					template_data['product']['associations']['categories']['category'].append({'id':j})							

		return template_data

prestashoperp_sync_now()

############## Mapping classes #################
class prestashop_order(osv.osv):			
	_name="prestashop.order"
	
	def get_id(self,cr,uid,shop,object,ur_id,context=None):
		if context is None:
			context = {}
		if shop=='prestashop':
			presta_id=False
			got_id=self.search(cr,uid,[('object_name','=',object),('erp_id','=',ur_id)])
			if got_id:
				presta_id=self.browse(cr,uid,got_id[0]).presta_id
			return presta_id
		elif shop=='openerp':
			erp_id=False
			got_id=self.search(cr,uid,[('object_name','=',object),('presta_id','=',ur_id)])
			if got_id:
				erp_id=self.browse(cr,uid,got_id[0]).erp_id
			return erp_id
		else:
			return "Shop not found"
	
	def get_all_ids(self,cr,uid,shop,object,context=None):
		if context is None:
			context = {}
		all_ids=[]
		if shop=='prestashop':
			got_ids=self.search(cr,uid,[('object_name','=',object)])
			for i in got_ids:
				all_ids.append(i.presta_id)
			return all_ids
		elif shop=='openerp':
			got_ids=self.search(cr,uid,[('object_name','=',object)])
			for i in got_ids:
				all_ids.append(self.browse(cr,uid,i).erp_id)
			return all_ids
		else:
			return "Shop not found"
				
		
	_columns = {
		'name': fields.char('Order Ref Name',size=100),
		'object_name':fields.selection((('customer','Order'),('product','Order'),('category','Order'),('order','Order')),'Object'),
		
		'erp_id':fields.integer('Openerp`s Order Id',required=1),	
		'presta_id':fields.integer('PrestaShop`s Order Id',required=1),			
	}
prestashop_order()

class prestashop_category(osv.osv):			
	_name="prestashop.category"
	_order = 'need_sync'
	
	def get_id(self,cr,uid,shop,ur_id,context=None):
		if context is None:
			context = {}
		if shop=='prestashop':
			presta_id=False
			got_id=self.search(cr,uid,[('erp_category_id','=',ur_id)])
			if got_id:
				presta_id=self.browse(cr,uid,got_id[0]).presta_category_id
			return presta_id
		elif shop=='openerp':
			erp_id=False
			got_id=self.search(cr,uid,[('presta_category_id','=',ur_id)])
			if got_id:
				erp_id=self.browse(cr,uid,got_id[0]).erp_category_id
			return erp_id
		else:
			return "Shop not found"
			
	_columns = {
		'name': fields.char('Category Name',size=100),
		'category_name':fields.many2one('product.category', 'Category Name'),
		'erp_category_id':fields.integer('Openerp`s Category Id'),	
		'presta_category_id':fields.integer('PrestaShop`s Category Id'),
		'need_sync': fields.selection((('yes','Yes'),('no','No')),'Update Required'),
	}
	_defaults={
				'need_sync':'no',
				
	 }
prestashop_category()

class prestashop_customer(osv.osv):			
	_name="prestashop.customer"	
	_order = 'need_sync'
	
	_columns = {
		'name': fields.char('Customer Name',size=100),
		'customer_name':fields.many2one('res.partner', 'Customer Name'),
		'erp_customer_id':fields.integer('Openerp`s Customer Id'),	
		'presta_customer_id':fields.integer('PrestaShop`s Customer Id'),
		'presta_address_id':fields.char('PrestaShop`s Address Id',size=100),
		'need_sync': fields.selection((('yes','Yes'),('no','No')),'Update Required'),
	}
	_defaults={
				'need_sync':'no',
				
	 }
prestashop_customer()

class prestashop_product_attribute(osv.osv):			
	_name="prestashop.product.attribute"
	_order = 'need_sync'
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if not vals.has_key('erp_id'):
			vals['erp_id']=vals['name']	
		return super(prestashop_product_attribute, self).create(cr, uid, vals, context=context)
	
	def write(self,cr,uid,ids,vals,context=None):
		if context is None:
			context = {}
		if vals.has_key('name'):
			vals['erp_id']=vals['name']	
		return super(prestashop_product_attribute,self).write(cr,uid,ids,vals,context=context)
	
	_columns = {
		'name':fields.many2one('product.attribute', 'Product Attribute'),
		'erp_id':fields.integer('Openerp`s Attribute Id'),	
		'presta_id':fields.integer('PrestaShop`s Attribute Id'),
		'need_sync': fields.selection((('yes','Yes'),('no','No')),'Update Required'),
	}
	_defaults={
				'need_sync':'no',
	 }
prestashop_product_attribute()

class prestashop_product_attribute_value(osv.osv):			
	_name="prestashop.product.attribute.value"
	_order = 'need_sync'
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if not vals.has_key('erp_id'):
			vals['erp_id']=vals['name']	
		return super(prestashop_product_attribute_value, self).create(cr, uid, vals, context=context)
	
	def write(self,cr,uid,ids,vals,context=None):
		if context is None:
			context = {}
		if vals.has_key('name'):
			vals['erp_id']=vals['name']	
		return super(prestashop_product_attribute_value,self).write(cr,uid,ids,vals,context=context)
	
	_columns = {
		'name':fields.many2one('product.attribute.value', 'Product Attribute Value'),
		'erp_id':fields.integer('Openerp`s Attribute Value Id'),	
		'presta_id':fields.integer('PrestaShop`s Attribute Value Id'),
		'erp_attr_id':fields.integer('Openerp`s Attribute Id'),	
		'presta_attr_id':fields.integer('PrestaShop`s Attribute Id'),
		'need_sync': fields.selection((('yes','Yes'),('no','No')),'Update Required'),
	}
	_defaults={
				'need_sync':'no',
	 }
prestashop_product_attribute_value()

class prestashop_product(osv.osv):			
	_name="prestashop.product"
	_order = "need_sync"
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if not vals.has_key('product_name'): 
			vals['product_name']=vals['erp_product_id']	
		return super(prestashop_product, self).create(cr, uid, vals, context=context)
	_columns = {
		'name': fields.char('Product Name',size=100),
		'product_name':fields.many2one('product.product', 'Product Name',ondelete='cascade'),
		'erp_product_id':fields.integer('Openerp`s Product Id'),	
		'erp_template_id':fields.integer('Openerp`s Template Id'),	
		'presta_product_id':fields.integer('PrestaShop`s Product Id'),			
		'presta_product_attr_id':fields.integer('PrestaShop`s Product Attribute Id'),
		'need_sync': fields.selection((('yes','Yes'),('no','No')),'Update Required'),
	}
	_defaults={
				'need_sync':'no',
				'presta_product_attr_id':0
	 }
prestashop_product()

class prestashop_product_template(osv.osv):			
	_name="prestashop.product.template"
	_order = "need_sync"

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if not vals.has_key('template_name'): 
			vals['template_name']=vals['erp_template_id']	
		return super(prestashop_product_template, self).create(cr, uid, vals, context=context)
	_columns = {
		'name': fields.char('Product Name',size=100),
		'template_name':fields.many2one('product.template', 'Template Name',ondelete='cascade'),
		'erp_template_id':fields.integer('Openerp`s Template Id'),
		'presta_product_id':fields.integer('PrestaShop`s Product Id'),
		'need_sync': fields.selection((('yes','Yes'),('no','No')),'Update Required'),
		'default_attribute': fields.boolean('Default Attribute is set'),
	}
	_defaults={
				'need_sync':'no'
	 }
prestashop_product_template()