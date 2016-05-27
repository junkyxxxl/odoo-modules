# -*- coding: utf-8 -*-
{
    'name': "Account Journal DDT",

    'summary': """
        All'interno del picking_type viene data la possibilità di impostare il
        sezionale vendite da impostare di default durante la creazione delle fatture differite.""",

    'description': """
        All'interno del picking_type viene data la possibilità di impostare il
        sezionale vendite da impostare di default durante la creazione delle fatture differite.
    """,

    'author': "Isa s.r.l.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'l10n_it_ddt_makeover',
        'account',
        'stock'
    ],

    # always loaded
    'data': [
        'stock_picking_type.xml',
        'ddt_create_invoice.xml'
    ],
}
