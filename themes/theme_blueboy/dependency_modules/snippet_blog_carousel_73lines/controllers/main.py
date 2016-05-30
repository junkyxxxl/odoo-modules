# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp.addons.web.http import request
import json
from openerp.addons.web import http
from openerp.addons.snippet_object_carousel_73lines.controllers.main import snippet_object_carousel_73lines_controller

class snippet_blog_carousel_73lines_controller(snippet_object_carousel_73lines_controller):
    
    @http.route(['/snippet_object_carousel_73lines/render/blog.post'], type='json', auth='public', website=True , csrf=False,cache=300)
    def render_blog_carousel(self, template, filter_id=False, objects_in_slide=4, limit=1, object_name=False,in_row=1):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
#         request.context.update({'get_property_value': self.get_property_value})
        res = super(snippet_blog_carousel_73lines_controller,self).render_object_carousel(template, filter_id=filter_id, 
                                                                                            objects_in_slide=objects_in_slide, limit=limit, object_name=object_name,in_row=in_row)
        return res