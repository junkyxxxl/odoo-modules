# -*- coding: utf-8 -*-
{
    'name': "account_report",

    'summary': """
        Stampe base per contabilità""",

    'description': """
        Stampe base delle fatture e dei ddt
    """,

    'author': "Isa s.r.l.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Invoicing & Payments',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'report',
        'web',
        'l10n_it_ddt_makeover',
        'account',
        'account_makeover',
        'account_discount',
        'free_invoice_line',
        'l10n_it_fiscalcode',
        'account_cashing_fees',
        'account_account_partner',
        'sale'
    ],

    # always loaded
    'data': [
        'report_style.xml',
        'report_ddt.xml',
        'report_shipping_invoice.xml',
        'report_delay_invoice.xml',
        'report_invoice.xml',
        'report_saleorder.xml',
        'res_company.xml',
    ]
}
