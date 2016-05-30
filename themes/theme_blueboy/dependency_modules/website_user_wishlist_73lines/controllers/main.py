# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp import SUPERUSER_ID
from openerp.addons.website_portal.controllers.main import WebsiteAccount

class WebsiteUserWishList(http.Controller):
    @http.route(['/profile/add_to_wishlist/'], type='json', auth="public", website=True, multilang=True)
    def add_wishlist_json(self, product_id=None):
        cr, context = request.cr, request.context
        dic_wishlist = {}
        if product_id:            
            dic_wishlist = {
                            'product_template_id': product_id,
                            'user_id': request.uid,
                            }
        request.registry['user.wishlist'].create(cr, SUPERUSER_ID, dic_wishlist,context=context)
        return True

class WebsiteAccount(WebsiteAccount):
    @http.route(['/my/home'], type='http', auth="user", website=True)
    def account(self, **kw):
        """ Add sales documents to main account page """
        response = super(WebsiteAccount, self).account()
        uw_obj = request.registry['user.wishlist']
        cr, uid = request.cr, request.uid
        uw_ids = uw_obj.search(cr,SUPERUSER_ID,[('user_id','=',uid)])
#         values=self.view().params['values']
        print "UW IDS ---------------------",uw_ids
        if uw_ids:
            wishlists = uw_obj.browse(cr,SUPERUSER_ID,uw_ids)
            response.qcontext.update({
                                       'wishlists':wishlists
                                       })
        return response 