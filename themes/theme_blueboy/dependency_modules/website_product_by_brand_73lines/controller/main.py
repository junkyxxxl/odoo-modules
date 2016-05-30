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

class WebsiteSale(website_sale):
    
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        brand_list = request.httprequest.args.getlist('brand')
        brand_list = [int(i) for i in brand_list]
        request.context.update({'search_default_brand_id':brand_list})
        res = super(WebsiteSale,self).shop(page=page,category=category,search=search,ppg=ppg,**post)
        res.qcontext['brand_set']=brand_list
        return res