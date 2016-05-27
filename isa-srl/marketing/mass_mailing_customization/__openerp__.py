# -*- coding: utf-8 -*-
{
    'name': "mass_mailing_customization",

    'summary': """
        Aggiunge delle personalizzazioni al modulo mass_mailing""",

    'description': """
        1) Aggiunto link per visualizzare la risorsa all'interno
        delle statistiche del messaggio email.
    """,

    'author': "isa s.r.l.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check
    # https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Mass Mailing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mass_mailing',
    ],

    # always loaded
    'data': [
        'views/mail_mail_statistics.xml',
    ],
}
