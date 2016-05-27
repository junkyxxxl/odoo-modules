# -*- coding: utf-8 -*-
{
    'name': "account_report_family",

    'summary': """
        Introduce sul modulo account_report informazioni di spedizioni aggiuntive se presente
        anche il modulo delle famiglie dei prodotti.""",

    'description': """
        Il modulo è autoinstallante e si installa automaticamente se sono presenti entrambi i moduli:
        account_report, producy_family
    """,

    'author': "Isa Srl",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Invoicing & Payments',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account_report',
        'product_family',
    ],
    # always loaded
    'data': [
        'report_ddt.xml',
        'report_shipping_invoice.xml',
        'res_company.xml',
    ],
    'auto_install': True,
}
