# -*- coding: utf-8 -*-
{
    'name': "account_report_primapaint",

    'summary': """
        Stampa budget agenti""",

    'description': """
        Stampa base del fatturato e budget per agenti
    """,

    'author': "Isa s.r.l.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Invoicing & Payments',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'report',
                'account',
                ],

    # always loaded
    'data': [
        'wizard/account_report_view.xml',
        'report/template.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}