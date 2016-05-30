# -*- coding: utf-8 -*-
##############################################################################
#
#    73Lines Development Pvt. Ltd.
#    Copyright (C) 2009-TODAY 73Lines(<http://www.73lines.com>).
#
#    you can modify it under the terms of the GNU LESSER 
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies 
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE 
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.  
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import http
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.http import request
from openerp import SUPERUSER_ID

class WebsiteSale(website_sale):
    
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        feature_list = request.httprequest.args.getlist('feature')
        feature_values = [map(int, v.split("-")) for v in feature_list if v]
        features_ids = set([v[0] for v in feature_values])
        feature_set = set([v[1] for v in feature_values])
        
        request.context.update({'search_default_feature_line_ids':list(feature_set)})        
        res = super(WebsiteSale,self).shop(page=page,category=category,search=search,ppg=ppg,**post)
        
        product_ids = [product.id for product in res.qcontext['products']]
        pf_pool = request.registry["product.feature"]
        if product_ids:
            features_ids = pf_pool.search(cr, uid, [('feature_line_ids.product_tmpl_id', 'in', product_ids)], context=context)
        features_objs = pf_pool.browse(cr, uid, features_ids, context=context)
        res.qcontext.update({'features':features_objs,
                             'feature_set':feature_set})
        return res