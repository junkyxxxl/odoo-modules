# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Product Tags by 73Lines',
    'description': 'Website Product Tags by 73Lines',
    'category': 'Website',
    'version':'1.2',
    'author': '73Lines',
    'depends': ['website','website_sale'],
    'data': [
         'security/ir.model.access.csv',    
         'views/product_view.xml',
         'views/website_sale_template.xml',
        ],
    'images': [
        'static/description/website_product_tags.jpg',    
    ],
    'price': 40,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}