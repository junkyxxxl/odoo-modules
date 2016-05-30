# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name':'Blog Carousel By 73Lines',
    'description':'Blog Carousel By 73Lines',
    'category': 'Website',
    'version':'1.2',
    'author':'73Lines',
    'data': [
        'data/filter_demo.xml',
        'views/assets.xml',
        'views/s_blog_carousel.xml',
        
    ],
    'depends': ['website', 'website_blog','snippet_object_carousel_73lines'],
    'images': [
        'static/description/snippet_blog_carousel_73lines.jpg'
    ],
    'price': 20,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}
