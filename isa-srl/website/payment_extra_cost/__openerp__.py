# -*- coding: utf-8 -*-
{
    'name': "Payment extra cost",

    'summary': """
        Permette di aggiungere dei costi extra ai metodi di pagamento.""",

    'description': """
        All'interno dei metodi di pagamento, viene aggiunto un collegamento al prodotto per permettere di
        imputare un costo aggiuntivo durante la creazione dell'ordine di vendita.
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
        'base',
        'payment',
        'website_sale_delivery',
    ],
    # always loaded
    'data': [
        'payment_acquirer.xml',
        'views/website_sale_payment.xml',
    ],
    'qweb': [],
}
