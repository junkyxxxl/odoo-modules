# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.website_sale.controllers.main import get_pricelist

class website_wishlist(http.Controller):
	
	def get_pricelist(self):
		return get_pricelist()
	 
	@http.route(['/wishlist'], type='http', auth="public", website=True)
	def wishlist(self, **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		if not context.get('pricelist'):
			pricelist = self.get_pricelist()
			context['pricelist'] = int(pricelist)
		else:
			pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)
	 	from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
	 	to_currency = pricelist.currency_id
	 	compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)
		
		values={
			'wishlist': False,
			'compute_currency': compute_currency
		}
		values['wishlist'] = pool['website.wishlist'].get_wishlist_products(cr, SUPERUSER_ID, context=context)
		return http.request.render("website_wishlist.wishlist", values)



	@http.route('/wishlist/add_to_wishlist', type='json', auth='public', website=True)
	def add_to_wishlist(self, product, *args, **kwargs):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		add = pool['res.users'].add_product(cr, uid, int(product), context=context)
		return add

	@http.route('/wishlist/remove_from_wishlist', type='json', auth='public', website=True)
	def remove_from_wishlist(self, product, *args, **kwargs):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		remove = pool['res.users'].remove_product(cr, uid, int(product), context=context)
		return remove
