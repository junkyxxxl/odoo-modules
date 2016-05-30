# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name':'Brand Carousel By 73Lines',
    'description':'Brand Carousel By 73Lines',
    'category': 'Website',
    'version':'1.2',
    'author':'73Lines',
    'data': [
        'views/assets.xml',
        'views/s_brand_carousel.xml',
        'data/filter_demo.xml',
        
    ],
    'depends': ['website', 'website_blog','snippet_object_carousel_73lines','website_product_by_brand_73lines'],
    'images': [
        'static/description/snippet_brand_carousel.jpg',
    ],
    'price': 10,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}
