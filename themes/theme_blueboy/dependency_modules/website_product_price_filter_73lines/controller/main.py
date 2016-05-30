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
        if post and 'price_range' in post:
            price_from,price_to= post['price_range'].split(";")
            request.context.update({'price_range_from':price_from,'price_range_to':price_to})
        res = super(WebsiteSale,self).shop(page=page,category=category,search=search,ppg=ppg,**post)
        product_prices = [product.list_price for product in res.qcontext['products']]
        product_prices.sort()
        price_min = product_prices and product_prices[0] or 0
        price_max = product_prices and product_prices[-1] or 0
        step = (price_max - price_min) / 5
        
        if not 'price_range' in post and not 'price_min_max' in post:
            price_from = price_min
            price_to = price_max
            
        if 'price_min_max' in post:
            price_min,price_max = post['price_min_max'].split(";")        
        res.qcontext.update({'price_range':str(price_from)+";"+str(price_to)+";"+str(price_min)+";"+str(price_max)+";"+str(step),
                             'price_min_max':str(price_min)+";"+str(price_max)
                             })
        return res