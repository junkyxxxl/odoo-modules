# -*- coding: utf-8 -*-
{
    'name': "salesagent_target_primapaint",

    'summary': """
        Gestione del target per gli agenti""",

    'description': """
        Prmette di gestire il target relativamente agli agenti di vendita.
    """,

    'author': "Isa S.r.l.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account_commission',
        'decimal_precision',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        'wizard/wizard_copy_target.xml',
        'salesagent_precision.xml',
        'salesagent_target.xml',
        'res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
