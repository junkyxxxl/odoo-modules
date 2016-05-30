# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website User Wishlist by 73Lines',
    'description': 'Website User Wishlist by 73Lines',
    'category': 'Website',
    'version':'1.2',
    'author': '73Lines',
    'depends': ['website_sale','website_portal'],
    'demo': [
    ],
    'data': [
            'views/website_user_wishlist_backend.xml',
            'views/website_user_wishlist.xml',
            'views/assets.xml',
            'views/user_account_template.xml',
            'security/ir.model.access.csv'
    ],
    'images': [
        'static/description/website_user_wishlist.jpg',    
    ],
    'installable': True,
    'price': 40,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}
