# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Category Banner By 73Lines ',
    'description': 'Website Category Banner By 73Lines ',
    'category': 'Website',
    'version': '1.0',
    'author': '73Lines',
    'depends': ['website_sale','website_sale_options'],
    'data': [
        'views/category_banner_template.xml',
        'views/product_category_view.xml',
        ],
    'images': [
        'static/description/website_category_banner.jpg',
    ],
    'price': 40,
    'currency': 'EUR',
}