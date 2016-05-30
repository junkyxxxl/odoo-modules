# -*- coding: utf-8 -*-
{
    'name': "stock_picking_transfer_all",

    'summary': """
        This module enable user to bulk transfer picking.""",

    'description': """
        Adding option to picking for bulk transfer
    """,

    'author': "isa s.r.l.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
    ],

    # always loaded
    'data': [
        'stock_config_settings.xml',
        'wizard/stock_picking_transfer_all.xml'
    ],
}
