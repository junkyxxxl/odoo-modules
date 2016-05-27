# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp import fields
from openerp import models
import openerp
from openerp import tools, api
from openerp.osv import osv, orm, fields
from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.addons.website_sale.controllers.main import get_pricelist
import logging
logger = logging.getLogger(__name__)


class res_users(osv.osv):
	_inherit = 'res.users'

	def add_product(self, cr, uid, template_id, context=None):
		obj  = self.browse(cr, SUPERUSER_ID, uid)
		if obj.partner_id:
			vals = {
				'template_id': template_id,
				'partner_id':obj.partner_id.id
			}
			self.pool.get('website.wishlist').create(cr, SUPERUSER_ID, vals)
			if obj.partner_id.website_wishlist:
				return len(obj.partner_id.website_wishlist)
		return False

	def remove_product(self,cr,uid, template_id,context=None):
		obj  = self.browse(cr, SUPERUSER_ID, uid)
		if obj.partner_id:
			search = self.pool.get('website.wishlist').search(cr, SUPERUSER_ID, [('template_id','=',template_id),('partner_id','=',obj.partner_id.id)])
			if search:
				self.pool.get('website.wishlist').unlink(cr, SUPERUSER_ID, search)
				if obj.partner_id.website_wishlist:
					return len(obj.partner_id.website_wishlist)
		return False


class website(orm.Model):
	_inherit = 'website'
	
	def get_pricelist(self):
		return get_pricelist()
	
	def get_Product_template_priced(self, cr, uid, ids, product_template, context = None):
		ctx = dict(context,)
		if not context.get('pricelist'):
			pricelist = self.get_pricelist()
			ctx['pricelist'] = int(pricelist)
		product_template = self.pool.get('product.template').browse(cr, uid, product_template, ctx)
		return product_template

	def get_wishlist_products(self, cr, uid, context = None):
		obj = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
		if obj.partner_id:
			if obj.partner_id.website_wishlist:
				return obj.partner_id.website_wishlist
		return []

	def check_wishlist_product(self, cr, uid, context = None):
		product_ids = []
		obj = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
		if obj.partner_id.website_wishlist:
			for i in obj.partner_id.website_wishlist:
				product_ids.append(i.template_id.id)
			if product_ids:
				return product_ids
		return []


class res_partner(osv.osv):
	_inherit = 'res.partner'

	_columns={
		'website_wishlist':fields.one2many('website.wishlist','partner_id','Wishlist')
	}

class website_wishlist(osv.osv):
	_name = "website.wishlist"

	def create(self, cr, uid, vals, context=None):
		if vals.has_key('template_id') and vals.has_key('partner_id'):
			check = self.search(cr, SUPERUSER_ID, [('template_id','=',vals['template_id']),('partner_id','=',vals['partner_id'])])
			if check:
				return check[0]
		return super(website_wishlist, self).create(cr, uid, vals, context)

	def get_wishlist_products(self, cr, uid, context=None):
		obj = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
		if obj.partner_id:
			if obj.partner_id.website_wishlist:
				return obj.partner_id.website_wishlist
		return False

	def _get_uid(self, cr, uid, ids, names, args, context=None):
		res ={}
		res = dict.fromkeys(ids, uid)
		return res

	_columns = {
		'template_id':fields.many2one('product.product','Product'),
		'partner_id':fields.many2one('res.partner','Partner'),
		'user_id':fields.function(_get_uid, type="integer", string='User ID'),
	}
