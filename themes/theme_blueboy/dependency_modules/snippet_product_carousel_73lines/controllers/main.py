# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp.addons.web.http import request
from openerp.addons.web import http

from openerp.addons.website_sale.controllers.main import QueryURL

from openerp.addons.snippet_object_carousel_73lines.controllers.main import snippet_object_carousel_73lines_controller
from openerp.addons.website_sale.controllers.main import get_pricelist

class snippet_product_carousel_73lines_controller(snippet_object_carousel_73lines_controller):
    
    def get_pricelist(self):
        return get_pricelist()
    
    @http.route(['/snippet_object_carousel_73lines/render/product.template'], type='json', auth='public', website=True ,cache=300)
    def render_product_carousel(self, template, filter_id=16, objects_in_slide=4, limit=1, object_name="product.template",in_row=1):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category=None
        
        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)
         
        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)
         
        values = {
                      'compute_currency':compute_currency,
                      }
        request.context.update(values)
        res = super(snippet_product_carousel_73lines_controller,self).render_object_carousel(template, filter_id=filter_id, 
                                                                                            objects_in_slide=objects_in_slide, limit=limit, 
                                                                                            object_name=object_name,in_row=in_row)
        
        return res