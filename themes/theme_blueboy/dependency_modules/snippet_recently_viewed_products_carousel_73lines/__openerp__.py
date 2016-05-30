# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name':'Recently Viewed Products Carousel Snippet By 73Lines',
    'description':'Recently Viewed Products Carousel Snippet By 73Lines',
    'category': 'Website',
    'version':'1.2',
    'author':'73Lines',
    'data': [
        'security/ir.model.access.csv',
        'data/filter_demo.xml',
        'views/assets.xml',
        'views/s_product_recent_carousel.xml',
    ],
    'depends': ['snippet_product_carousel_73lines'],
    'images': [
        'static/description/snippet_recently_viewed_products_carousel.jpg',
    ],
    'price': 10,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}