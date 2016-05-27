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

class billing_default_fields(orm.Model):
	_name="billing.default.fields"

	_columns = {
		'name':fields.char(string = "Defaults Fields for Billing", required = "1"),
	}

class shipping_default_fields(orm.Model):
	_name="shipping.default.fields"

	_columns = {
		'name':fields.char(string="Defaults Fields for Billing", required = "1"),
	}

class website(orm.Model):
	_inherit = 'website'

	def get_onepage_checkout_val(self, cr, uid, ids, choise=0, context=False):
		irmodule_obj = self.pool.get('ir.module.module')
		use_onepage = irmodule_obj.search(cr, uid, [('name','in',['website_onepage_checkout']), ('state', 'in', ['to install', 'installed', 'to upgrade'])], context=context)
		if use_onepage:
			if choise == 0:
				return use_onepage
				
			if choise == 1:
				address_val = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_address_panel')
				if address_val:
					return True

			elif choise == 2:
				orderreview_val = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_orderreview_panel')
				if orderreview_val:
					return True

			elif choise == 3:
				payment_val = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_payment_panel')
				if payment_val:
					return True
		else:
			return False

	def get_onepage_checkout_name(self, cr, uid, ids, choise=0, context=False):
		irmodule_obj = self.pool.get('ir.module.module')
		use_onepage = irmodule_obj.search(cr, uid, [('name','in',['website_onepage_checkout']), ('state', 'in', ['to install', 'installed', 'to upgrade'])], context=context)
		if use_onepage:
			if choise == 1:
				address_name = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_address_panel_name')
				if address_name:
					return address_name
				else:
					return "Billing and Shipping Information"

			elif choise == 2:
				orderreview_name = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_orderreview_panel_name')
				if orderreview_name:
					return orderreview_name
				else:
					return "Order Preview and Delivery Method"

			elif choise == 3:
				payment_name = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_payment_panel_name')
				if payment_name:
					return payment_name
				else:
					return "Payement Option"
		else:
			return False

	def show_required_asterisk(self, cr, uid, ids, choise = 0, field_name = None, context=False):
		if choise == 1:
			billing_required = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_billing_required')
			if billing_required:
				billing_asterisk = ["name", "country_id", "email"]
				billing_temp = {"Your Name":"name",
								"Company Name":"street",
								"Email":"email",
								"Phone":"phone" ,
								"Street":"street2" ,
								"VAT Number":"vat" ,
								"City":"city" ,
								"Zip / Postal Code":"zip" ,
								"Country":"country_id" ,
							}
				billing_keys_temp = billing_temp.keys();
				billing_obj = self.pool.get('billing.default.fields')
				for temp in billing_required:
					fields_name = billing_obj.browse(cr, SUPERUSER_ID, int(temp), context=context).name
					if fields_name in billing_keys_temp:
						billing_asterisk.append(billing_temp[fields_name])
				if field_name in billing_asterisk:
					return True
				else:
					return False
			else:
				return False

		elif choise == 2:
			shipping_required = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_shipping_required')
			if shipping_required:
				shipping_asterisk = ["name", "country_id"]
				shipping_temp = {"Name":"name",
								"Phone":"phone" ,
								"Street":"street" ,
								"City":"city" ,
								"Zip / Postal Code":"zip" ,
								"Country":"country_id" ,
							}
				shipping_keys_temp = shipping_temp.keys();
				shipping_obj = self.pool.get('shipping.default.fields')
				for temp in shipping_required:
					fields_name = shipping_obj.browse(cr, SUPERUSER_ID, int(temp), context=context).name
					if fields_name in shipping_keys_temp:
						shipping_asterisk.append(shipping_temp[fields_name])
				if field_name in shipping_asterisk:
					return True
				else:
					return False
			else:
				return False
		return False

	def get_shipping_field_val(self, cr, uid, ids, context=False):
		shipping_val = self.pool.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_shipping_information')
		if shipping_val:
			return True
		return False


	# define two different fuction for check modules install or not but we can pass a list of module...
	def get_terms_conditions_module(self, cr, uid, ids,context=None):
		irmodule_obj = self.pool.get('ir.module.module')
		vals = irmodule_obj.search(cr, uid, [('name','in',['website_terms_conditions']), ('state', 'in', ['to install', 'installed', 'to upgrade'])], context=context)
		if vals:
			return True
		return False

	def get_order_notes_module(self, cr, uid, ids,context=None):
		irmodule_obj = self.pool.get('ir.module.module')
		vals = irmodule_obj.search(cr, uid, [('name','in',['website_order_notes']), ('state', 'in', ['to install', 'installed', 'to upgrade'])], context=context)
		if vals:
			return True
		return False
		




