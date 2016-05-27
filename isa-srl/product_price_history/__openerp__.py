# -*- coding: utf-8 -*-
{
    'name': "product_price_history",

    'summary': """
        View the product price history change.""",

    'description': """
       Adding smart button to product to show the product price history.
    """,

    'author': "isa s.r.l",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'purchase',
    ],

    # always loaded
    'data': [
        'views/product_price_history.xml',
        'views/product_template.xml'
    ]
}
