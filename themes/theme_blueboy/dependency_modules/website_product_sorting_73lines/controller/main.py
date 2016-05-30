# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import QueryURL
from openerp import _
import collections

class WebsiteSale(website_sale):
    
    order_by = {
                'anew': {'query':'id DESC','display_name':_('New'),'code':'anew'},
                'aold':{'query':'id ASC','display_name':_('Old'),'code':'aold'},
                'natoz':{'query':'name ASC','display_name':_('Name : A to Z'),'code':'natoz'},
                'nztoa':{'query':'name desc','display_name':_('Name : Z to A'),'code':'nztoa'},
                'phtl':{'query':'list_price DESC','display_name':_('Price : High to Low'),'code':'phtl'},
                'plth':{'query':'list_price ASC','display_name':_('Price : Low to High'),'code':'plth'},
                }
    order_by = collections.OrderedDict(sorted(order_by.items()))
    
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        order = ""
        if post and 'order' in post and post['order']: 
            request.context.update({
                            'default_order':self.order_by[post['order']]['query']
                            })
            order=post['order']
            
        attrib_list = request.httprequest.args.getlist('attrib')
        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=order)
        request.context.update({ 
                             'order_by':self.order_by,
                             'keep':keep
                             })
        res = super(WebsiteSale, self).shop(page=page, category=category, search=search, 
                                             ppg=ppg, **post)
        
        res.qcontext.update({ 
                             'order_by':self.order_by,
                             'keep':keep 
                             })
        if post and 'order' in post and post['order']:
            ordb = self.order_by[post['order']]['display_name']
        else:
            ordb = _("Relevance")
        res.qcontext.update({
                                'order_by_name':ordb
                                })
        return res

