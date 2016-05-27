# -*- coding: utf-8 -*-
{
    'name': "auth_signup_sale",

    'summary': """
        Permette di copiare i dati di listino e posizione fiscale quando si 
        registra un nuovo utente.""",

    'description': """
        Alla registrazione dell'utente viene creato un nuovo partner sulla base di un utente 
        impostato in configurazione (di solito Template User). Quando viene creato il nuovo utente 
        vengono copiati da Template User anche i campi relativi al listino di vendita e alla posizione 
        fiscale.
    """,

    'author': "Isa s.r.l.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Authentication',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'auth_signup',
                'account',
                'product'],

    # always loaded
    'data': [
    ]
}