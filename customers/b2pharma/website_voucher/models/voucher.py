
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
from openerp.http import request
from openerp.osv import fields, osv
import string
import random
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)
	
def _code_generator(size=13, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

class sale_order(osv.Model):
	_inherit = "sale.order"
	def _add_voucher(self, cr, uid, ids, voucher_product_id, voucher_value, voucher_id, voucher_name,total_available,wk_order_total,voucher_val_type,context=None):
		order_id = ids[0]
		result={}
		already_exists = self._cart_find_product_line(cr, uid, ids, voucher_product_id)
		if already_exists:
			result['status']=False
			result['message']	= _('You can use only 1 Voucher per Order.')
		else:
			values = self._website_product_id_change(cr, uid, [order_id], order_id, voucher_product_id, qty=1, context=context)
			values['name'] = voucher_name
			if voucher_val_type == 'amount':
				if wk_order_total < voucher_value:
					values['price_unit'] = -wk_order_total
				else:
					values['price_unit'] = -voucher_value
			else:

				values['price_unit'] = -(wk_order_total*voucher_value)/100

			values['product_uom_qty'] = 1
			line_id = self.pool.get('sale.order.line').create(cr, SUPERUSER_ID, values, context=context)
			voucher_history_value={
				'name':voucher_name,
				'voucher_id':voucher_id,
				'voucher_value':values['price_unit'],
				'order_id':order_id,
				'sale_order_line_id':line_id
			}
			self.pool.get('wk_website.history').create(cr, SUPERUSER_ID,voucher_history_value, context=context)

			result['status']=True
			if total_available != -1:
				self.pool.get('website.voucher').redeem_voucher(cr,uid,voucher_id,context) 
		return result

class wk_website_history(osv.osv):
	_name = "wk_website.history"
	_order = 'create_date desc'
	_columns={
		'name': fields.char('Voucher Name', size=100, required=True),
		'voucher_id':fields.many2one('website.voucher','Voucher'),
		'order_id':fields.many2one('sale.order','Sale order'),
		'create_date':fields.datetime('Used Date', help="Date on which voucher used."),
		'sale_order_line_id':fields.many2one('sale.order.line','Sale order line id',select=True,ondelete='cascade'),
		'voucher_value':fields.related('sale_order_line_id','price_unit',type='float',string='Voucher Value', required=True),
		'user_id':fields.related('sale_order_line_id','order_partner_id',relation="res.partner",type='many2one',string='User'),
	}




class website_voucher(osv.osv):
	_name = "website.voucher"
	_order = 'create_date desc'

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		default_values = self.pool.get('website.voucher.config')._get_default_values(cr,uid)
		if vals['validity'] ==0:
			raise osv.except_osv(_('Error!'), _('Validiy can`t be 0. Choose -1 for unlimited or greater than 0 !!!'))
		if vals['total_available'] ==0:
			raise osv.except_osv(_('Error!'), _('Total Availability can`t be 0. Choose -1 for unlimited or greater than 0 !!!'))
		if vals['voucher_value'] < default_values['min_amount']:
			raise osv.except_osv(_('Error!'), _('You can`t create voucher below this minimum amount (%s) !!!')%default_values['min_amount'])
		if vals['voucher_value'] > default_values['max_amount']:
			raise osv.except_osv(_('Error!'), _('You can`t create voucher greater than this maximum amount (%s) !!!')%default_values['max_amount'])
		vals['user_id']=uid
		if vals['voucher_code'] == 0:
			vals['voucher_code']=self._generate_code(cr,uid)
		else:
			vals['voucher_code']=self._check_code(cr,uid,vals['voucher_code'])																												
		max_expiry_date = self.pool.get('website.voucher.config')._get_default_values(cr,uid)['max_expiry_date']
		if vals['validity'] >0:
			vals['expiry_date']=datetime.strptime(vals['issue_date'],DEFAULT_SERVER_DATETIME_FORMAT)+timedelta(days=vals['validity'])
			if vals['expiry_date'] > datetime.strptime(max_expiry_date,DEFAULT_SERVER_DATETIME_FORMAT):
				vals['expiry_date'] = max_expiry_date
		else:
			vals['expiry_date'] = max_expiry_date
		return super(website_voucher, self).create(cr, uid, vals, context=context)

	def write(self,cr,uid,ids,vals,context=None):
		if context is None:
			context = {}
		if vals.get('validity',False) or vals.get('issue_date',False):
			if not vals.get('issue_date',False):
				vals['issue_date'] = self.read(cr,uid,ids[0],['issue_date'])['issue_date']
			if not vals.get('validity',False):
				vals['validity'] = self.read(cr,uid,ids[0],['validity'])['validity']
			max_expiry_date = self.pool.get('website.voucher.config')._get_default_values(cr,uid)['max_expiry_date']
			if vals['validity'] >0:
				vals['expiry_date']=datetime.strptime(vals['issue_date'],DEFAULT_SERVER_DATETIME_FORMAT)+timedelta(days=vals['validity'])
				if vals['expiry_date'] > datetime.strptime(max_expiry_date,DEFAULT_SERVER_DATETIME_FORMAT):
					vals['expiry_date'] = max_expiry_date
			else:
				vals['expiry_date'] = max_expiry_date
		if vals.has_key('validity') and vals['validity'] ==0:
			raise osv.except_osv(_('Error!'), _('Validiy can`t be 0. Choose -1 for unlimited or greater than 0 !!!'))
		
		# if vals.has_key('total_available') and vals['total_available'] ==0:
		# 	raise osv.except_osv(_('Error!'), _('Total Availability can`t be 0. Choose -1 for unlimited or greater than 0 !!!'))
		default_values = self.pool.get('website.voucher.config')._get_default_values(cr,uid)
		
		if vals.has_key('voucher_value') and vals['voucher_value'] < default_values['min_amount']:
			raise osv.except_osv(_('Error!'), _('You can`t create voucher below this minimum amount (%s) !!!')%default_values['min_amount'])
		
		if  vals.has_key('voucher_value') and vals['voucher_value'] > default_values['max_amount']:
			raise osv.except_osv(_('Error!'), _('You can`t create voucher greater than this maximum amount (%s) !!!')%default_values['max_amount'])

		if vals.has_key('voucher_code'):
			vals['voucher_code']=self._check_write_code(cr,uid,vals['voucher_code'],ids)
		return super(website_voucher, self).write(cr, uid,ids, vals, context=context)

	def default_get(self, cr, uid, fields, context=None):
		if context is None:
			context={}
		res = super(website_voucher, self).default_get(cr, uid, fields, context)
		default_values = self.pool.get('website.voucher.config')._get_default_values(cr,uid)
		res['voucher_value'] = default_values['default_value']
		res['validity'] = default_values['default_validity']
		if res['validity'] < 0:
			res['expiry_date'] = default_values['max_expiry_date']
		res['total_available'] = default_values['default_availability']
		res['name'] = default_values['default_name']
		return res

	def create_voucher(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		message=_("<h2>A new Gift Voucher has been created successfully.</h2>")
		partial_id = self.pool.get('wk.wizard.message').create(cr, uid, {'text':message}, context=context)
		return {
						'name':"Summary",
						'view_mode': 'form',
						'view_id': False,
						'view_type': 'form',
						'res_model': 'wk.wizard.message',
						'res_id': partial_id,
						'type': 'ir.actions.act_window',
						'nodestroy': True,
						'target': 'new',
						'domain': '[]',
						'context': context
					}

	def _generate_code(self,cr,uid,context=None):
		if context is None:
			context = {}
		while True:
			code = _code_generator()
			check = self.search(cr,uid,[('voucher_code','=',code),('active','in',[True,False])])
			if not check:
				break
		return code

	def _check_code(self,cr,uid,code,context=None):
		if context is None:
			context = {}
		check = self.search(cr,uid,[('voucher_code','=',code),('active','in',[True,False])])
		if not (check == []) or (check):
			raise osv.except_osv(_('Error'), _("Coupon code already exist !!!"+str(check)))
		return code

	def _check_write_code(self,cr,uid,code,code_id,context=None):
		if context is None:
			context = {}
		check = self.search(cr,uid,[('voucher_code','=',code),('active','in',[True,False])])
		if not (check == []) or (check):
			if len(check)==1 and check[0]==code_id:
				return code
			else:
				raise osv.except_osv(_('Error'), _("Coupon code already exist !!!"+str(check)))
		return code

	def _validate_n_get_value(self,cr,uid,secret_code,wk_order_total,context=None):
		if context is None:
			context = {}
		result={}
		result['status']=False
		# if len(secret_code)!=13:
		# 	result['type']		= _('ERROR')
		# 	result['message']	= _('Invalid Voucher.')
		# 	return result
		# 	# raise osv.except_osv(_('Error'), _("Invalid Coupon."))
		check_existense = self.search(cr,uid,[('voucher_code','=',secret_code),('active','in',[True,False])])
		if not check_existense:
			result['type']		= _('ERROR')
			result['message']	= _('Voucher doesn`t exist !!!')
			return result
			# raise osv.except_osv(_('Error'), _("Coupon doesn`t exist !!!"))
		self_browse = self.browse(cr,uid,check_existense[0])
		if not self_browse.active:
			result['type']		= _('ERROR')
			result['message']	= _('Voucher has been de-avtivated !!!')
			return result
			# raise osv.except_osv(_('Error'), _("Coupon has been de-avtivated !!!"))

		if self_browse.active and (self_browse.customer_id):
			if self_browse.customer_id.id != uid:
				result['type']		= _('ERROR')
				result['message']	= _('Voucher doesn`t exist !!!')
				return result

		if self_browse.total_available == 0:
			result['type']		= _('ERROR')
			result['message']	= _('Total Availability of this Voucher is 0. You can`t redeem this voucher anymore !!!')
			return result

		if self_browse.total_available > 0 or self_browse.total_available==-1:
			customer_id=self.pool.get('res.users').browse(cr,SUPERUSER_ID,uid).partner_id
			check = self.pool.get('wk_website.history').search(cr,SUPERUSER_ID,[('voucher_id','=',self_browse.id),('user_id','=',customer_id.id)])
			if len(check)>=self_browse.available_each_user and self_browse.available_each_user != -1:
				result['type']		= _('ERROR')
				result['message']	= _('Total Availability of this Voucher is 0. You can`t redeem this voucher anymore !!!')
				return result

			# raise osv.except_osv(_('Error'), _("Total Availability of this Coupon is 0. You can`t redeem this coupon anymore !!!"))
		# if datetime.strptime(self_browse.expiry_date,DEFAULT_SERVER_DATETIME_FORMAT) < fields.date.context_today(self, cr, uid, context=context):
		
		if datetime.strptime(self_browse.expiry_date,DEFAULT_SERVER_DATETIME_FORMAT) < datetime.now():
			result['type']		= _('ERROR')
			result['message']	= _('This Voucher has been expired on (%s) !!!')%self_browse.expiry_date
			return result
			# raise osv.except_osv(_('Error'), _("This coupon has been expired on (%s) !!!")%self_browse.expiry_date)
		
		# if self_browse.minimum_cart_amount > wk_order_total:
		# 	result['status']=False
		# 	result['message']= _('You can use this Voucher when order amount is greater then.'+str(self_browse.minimum_cart_amount))
		# 	return result

		result = self.pool.get('website.voucher.config')._get_default_values(cr,uid)
		result['status']=True
		result['type']  =_('SUCCESS')
		result['value'] = self_browse.voucher_value
		result['coupon_id'] = self_browse.id
		result['coupon_name'] = self_browse.name
		result['total_available'] = self_browse.total_available
		result['voucher_val_type']=self_browse.voucher_val_type
		result['message']  =_('Validated successfully. Using this voucher you can make discount of %s amount.')%result['value']
		
		return result

	def validate_voucher(self,cr,uid,secret_code,wk_order_total,context=None):
		if context is None:
			context = {}
		result = self._validate_n_get_value(cr,uid,secret_code,wk_order_total)
		# if result['status']:
		# 	self.redeem_voucher(cr,uid,result['coupon_id'],result['total_available'])
		return result

	def return_voucher(self,cr,uid,coupon_id,context=None):
		if context is None:
			context = {}
		total_availability = self.browse(cr, uid, coupon_id).total_available
		if total_availability>0:
			self.write(cr,uid,coupon_id,{'total_available':total_availability +1 })
		return True

	def redeem_voucher(self,cr,uid,coupon_id,context=None):
		if context is None:
			context = {}
		total_availability = self.browse(cr, uid, coupon_id ).total_available
		if total_availability>0:
			self.write(cr,uid,coupon_id,{'total_available':total_availability - 1})
		return True

	_columns={
			'name': fields.char('Name', size=100, required=True,select=True, help="This will be displayed in the order summary, as well as on the invoice."),
			'voucher_code': fields.char('Code', size=13, help="Secret 13 digit code use by customer to redeem this coupon."),
			'create_date': fields.datetime('Create Date', help="Date on which voucher is created."),
			'issue_date': fields.datetime('Issue Date', help="Date on which voucher is issued."),
			'expiry_date': fields.datetime('Expiry Date', help="Date on which voucher is expired."),
			'validity': fields.integer('Validity(in days)',required=True, help="Validity of this Voucher in days( -1 for unlimited )"),
			'total_available': fields.integer('Total Available',required=True, help="The cart rule will be applied to the first 'X' customers only.(-1 for unlimited )"),
			'minimum_cart_amount': fields.integer('Minimum Cart Amount'),			
			'voucher_value': fields.float('Voucher Value', required=True),
			'note': fields.text('Description',help="For your eyes only. This will never be displayed to the customer."),
			'active': fields.boolean('Active', help="By unchecking the active field you can disable this voucher without deleting it."),
	        'user_id': fields.many2one('res.users', 'Created By'),
	        'customer_id': fields.many2one('res.users', 'Limit to a single customer',help='Optional: The cart rule will be available to everyone if you leave this field blank.'),
			'available_each_user': fields.integer('Total available for each user', help="A customer will only be able to use the cart rule 'X' time(s)."),
	        
	        'voucher_val_type': fields.selection([('percent', '%'),('amount', 'Amount'),],required=True),
	        # 'dicount_applied_tax': fields.selection([('before_tax', 'Before tax'),('after_tax', 'After tax'),],required=True),
	        
	         }
	_defaults = {
		'available_each_user': -1,
        'active': 1,
        'issue_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
		'total_available':-1,
		'validity':-1,
		'voucher_val_type':'percent',
    }
	_sql_constraints = [
        ('voucher_code_uniq', 'unique(voucher_code)', 'Voucher Code Must Be Unique !!!'),
    ]
website_voucher()

class website_voucher_config(osv.osv):
	_name = "website.voucher.config"
	
	def _get_default_values(self,cr,uid,context=None):
		if context is None:
			context = {}
		active_id=self.search(cr, uid,[('active','=',True)])
		if not active_id:
			raise osv.except_osv(_('Error'), _("Sorry, Please configure the module before creating any voucher."))
		default_values = self.browse(cr,uid,active_id[0])
		temp_dict = {
		'product_id':default_values.product_id.id,
		'max_amount':default_values.max_amount,
		'min_amount':default_values.min_amount,
		'max_expiry_date':default_values.max_expiry_date,
		'one_time_use':default_values.one_time_use,
		'default_name':default_values.default_name,
		'default_validity':default_values.default_validity,
		'default_availability':default_values.default_availability,
		'default_value':default_values.default_value,
		}
		return temp_dict
	
	def create(self, cr, uid, vals, context=None):	
		active_ids=self.pool.get('website.voucher.config').search(cr, uid, [('active','=',True)])	
		if vals.has_key('active')==True and vals['active']:	
			if len(active_ids) >= 1:
				raise osv.except_osv(_('Error'), _("Sorry, Only one active configuration is allowed."))
		return super(website_voucher_config, self).create(cr, uid, vals, context=context)
	
	def write(self, cr, uid, ids, vals, context=None):		
		active_ids=self.pool.get('website.voucher.config').search(cr, uid, [('active','=',True)])	
		if vals.has_key('active'):
			if vals['active'] is True:
				if len(active_ids)>=1:
					raise osv.except_osv(_('Error'), _("Sorry, Only one active configuration is allowed."))
		return super(website_voucher_config, self).write(cr, uid, ids, vals, context=context)
		
	_columns={
			'name': fields.char('Name', size=100),
			'product_id': fields.many2one('product.product', 'Product', domain=[('type', '=','service'),('sale_ok','=',False)]),
			'min_amount': fields.float('Minimum Voucher Value'),
			'max_amount': fields.float('Maximum Voucher Value'),
			'max_expiry_date': fields.datetime('Maximum Expiry Date',help="Date on which Voucher is expired."),
			'one_time_use': fields.boolean('One Time Use Only',readonly=1),
			'partially_use': fields.boolean('Partially Use',readonly=1),
			'active': fields.boolean('Active', help="By unchecking the active field you can disable this voucher  configuration without deleting it."),
			'default_name': fields.char('Name', size=100, help="This will be displayed in the order summary, as well as on the invoice."),
			'default_validity': fields.integer('Validity(in days)', help="Validity of this Voucher in days( -1 for unlimited )"),
			'default_availability': fields.integer('Total Available', help="Total availability of this voucher( -1 for unlimited )"),
			'default_value': fields.float('Voucher Value'),
	         }
	_defaults = {
        'active': 1,
        'one_time_use': 0,
        'partially_use': 0,
        'name': 'Default Configuration for Website Gift Voucher',
        'min_amount': 0.001,
        'default_validity': -1,
        'default_availability': -1,
        'default_value': 0.0,
    }
website_voucher_config()

class website(osv.osv):
	_inherit = 'website'


	def wk_get_default_product(self, cr, uid):
		return self.pool.get('website.voucher.config')._get_default_values(cr,uid)['product_id']

	def sale_get_order(self, cr, uid, ids, force_create=False, code=None, update_pricelist=None, context=None):
		sale_order = super(website, self).sale_get_order(cr, uid, ids, force_create, code, update_pricelist, context)
		order_total_price=0

		if hasattr(sale_order,'order_line'):
			for order_line_id in sale_order.order_line:
				if order_line_id.product_id.id != self.wk_get_default_product(cr,uid):
					order_total_price += order_line_id.product_uom_qty * order_line_id.price_unit
			for order_line_id in sale_order.order_line:
				if order_line_id.product_id.id == self.wk_get_default_product(cr,uid):
					voucher_value=request.session.get('secret_key_data')
					if voucher_value.has_key('wk_voucher_value'):
						wk_voucher_value=voucher_value['wk_voucher_value']
						if voucher_value['voucher_val_type']== 'amount':
							if order_total_price >= wk_voucher_value:
								order_line_id.price_unit = - wk_voucher_value
							elif order_total_price < wk_voucher_value:
								order_line_id.price_unit = - order_total_price
							else:
								order_line_id.price_unit = 0
						else:
							order_line_id.price_unit=-((wk_voucher_value * order_total_price) /100)

		return sale_order
            