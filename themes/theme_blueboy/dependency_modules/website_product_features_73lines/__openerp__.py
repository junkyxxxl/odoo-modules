# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name':'Website Product Features By 73Lines',
    'description':'Website Product Features By 73Lines',
    'category': 'Website',
    'version':'1.2',
    'author':'73Lines',
    'data': [
        'views/product_view.xml',
        'views/website_sale_template.xml',
        'security/ir.model.access.csv'
    ],
    'images': [
        'static/description/website_product_features.jpg',    
    ],
    'depends': ['website_sale','website_product_content_block_73lines'],
    'price': 50,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}
