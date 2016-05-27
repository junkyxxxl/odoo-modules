# -*- coding: utf-8 -*-
{
    'name': "website_sale_checkout",

    'summary': """
        Permette di specificare durante il checkout se si tratta di
        un privato oppure di una partita iva.""",

    'description': """
        Richiede se si tratta di un cliente privato o di una partita iva. Richiedendo
        dati aggiuntivi (codice fiscale, nome e cognome, ecc...)
    """,

    'author': "Isa s.r.l.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'website_sale',
        'l10n_it_fiscalcode',
        'base_fiscalcode'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
    ],
}
