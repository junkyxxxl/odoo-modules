# -*- coding: utf-8 -*-
{
    'name': "hr_holidays_days_contract",

    'summary': """
        Introduce il calcolo dei giorni di permesso in base al contratto dell'impiegato""",

    'description': """
        Introduce il calcolo dei giorni di permesso in base al contratto dell'impiegato
    """,

    'author': "Isa Srl",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'hr_holidays',
                'hr'
                ],

    # always loaded
    'data': [
        'working_hour_view.xml',
        'flag_working_hour_view.xml'
    ],
}