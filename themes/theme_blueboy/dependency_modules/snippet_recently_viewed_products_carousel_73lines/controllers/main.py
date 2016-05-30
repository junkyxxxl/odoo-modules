# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale

from openerp.addons.snippet_product_carousel_73lines.controllers.main import snippet_product_carousel_73lines_controller

class WebsiteSale(website_sale):

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        uid= request.uid
        record = request.env['product.template.recent.view'].search([
            ('sessionid', '=', request.session.sid),
            ('product_id', '=', product.id),
            ('user_id','=',uid or False)
        ])
        if not record:
            record = request.env['product.template.recent.view'].create({
                'sessionid': request.session.sid,
                'product_id': product.id,
                'user_id':uid or False,
            })
        return super(WebsiteSale, self).product(product, category,
                                                search, **kwargs)

class snippet_product_template_recent_view_carousel_controller(snippet_product_carousel_73lines_controller):
    
    @http.route(['/snippet_object_carousel_73lines/render/product.template.recent.view'], type='json', auth='public', website=True , csrf=False,cache=300)
    def render_product_recent_carousel(self, template, filter_id=False, objects_in_slide=4, limit=1, object_name=False,in_row=1):
        cr, uid, context = request.cr, request.uid, request.context
        res = super(snippet_product_template_recent_view_carousel_controller,self).render_product_carousel(template, filter_id=filter_id, objects_in_slide=objects_in_slide, 
                                                                                                           limit=limit, object_name=object_name,in_row=in_row)
       
        return res
