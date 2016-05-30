# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name':'Products Category Carousel Snippet By 73Lines',
    'description':'Products Category Carousel Snippet By 73Lines',
    'category': 'Website',
    'version':'1.2',
    'author':'73Lines',
    'data': [
        'data/filter_demo.xml',        
        'views/assets.xml',
        'views/s_product_category_carousel.xml',        
        
    ],
    'depends': ['website', 'website_sale','snippet_object_carousel_73lines',
                'website_category_banner_73lines'],
    'images': [
        'static/description/snippet_product_category_carousel.jpg',
    ],
    'price': 20,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}
