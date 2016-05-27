# -*- coding: utf-8 -*-
{
    'name': "hr_report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'hr',
                'report',
                'hr_overtime',
                'hr_holidays_working_hour'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'wizard/hr_report_view.xml',
        'report/template.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}