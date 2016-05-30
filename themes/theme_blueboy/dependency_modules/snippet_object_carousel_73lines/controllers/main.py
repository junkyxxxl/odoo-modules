# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp import SUPERUSER_ID
from openerp.tools.safe_eval import safe_eval

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class snippet_object_carousel_73lines_controller(http.Controller):
    
    def split_objects(self,in_row,objects):
        res = list(chunks(objects, in_row))
        return res
    
    @http.route(['/snippet_object_carousel_73lines/render'], type='json', auth='public', website=True , csrf=False,cache=300)
    def render_object_carousel(self, template, filter_id=False, objects_in_slide=4, limit=1, object_name=False,in_row=1):
        cr, uid, context = request.cr, request.uid, request.context
        res = request.registry[object_name].get_objects_for_carousel(cr,uid,filter_id=filter_id, limit=limit,context=context)
        values = {}
        values['objects'] = self.split_objects(in_row,res['objects'])
        values['title']=res['name']
        print "VALUES ---------------",values
        return request.registry['ir.ui.view'].render(request.cr, request.uid, template, values, context=request.context)