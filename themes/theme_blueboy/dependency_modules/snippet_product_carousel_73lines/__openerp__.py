# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name':'Products Carousel Snippet By 73Lines',
    'description':'Products Carousel Snippet By 73Lines',
    'category': 'Website',
    'version':'1.2',
    'author':'73Lines',
    'data': [
        'data/filter_demo.xml',
        'views/product_view.xml',
        'views/assets.xml',
        'views/s_product_carousel.xml',
        'views/s_product_mini_carousel.xml',
        
    ],
    'depends': ['website', 'website_sale','snippet_object_carousel_73lines'],
    'images': [
        'static/description/snippet_product_carousel.jpg',
    ],
    'price': 30,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}
