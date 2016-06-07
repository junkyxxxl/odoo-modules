# -*- coding: utf-8 -*-
{
    'name': "account_commission_followup",

    'summary': """
        Questo modulo integra le funzioni del modulo account_commission e account_follow_up""",

    'description': """
        Questo modulo integra le funzioni del modulo account_commission e account_follow_up
    """,

    'author': "Isa-Srl",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'account_commission',
                'account_followup'],

    # always loaded
    'data': ['views/res.partner.xml',
             'security/commission_security.xml',
             'security/ir.model.access.csv',
             'security/ir.rule.csv',
             'security/ir.ui.menu.csv'
             ],
    'auto_install': True,
}