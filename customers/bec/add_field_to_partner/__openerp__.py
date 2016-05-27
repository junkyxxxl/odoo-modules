{
    'name': 'BEC s.r.l. - Add Field Partner',
    'description': """Aggiunge campi personalizzati, alla vista partner (ereditari da res.partner) per modificare la vista.

Campi Aggiunti:

- Utente e Data Creazione.
- Utente e Data Modifica.
- Note FM.
- Campi su situazione stato modifica.

                    """,
    'version': '1.0',
    'category': 'BeC Plugins',
    'author': 'BeC',
    'website': 'http://www.bec.it/',
    # 'images': ['images/customer_tree.png','images/customer.png','images/sale_order.png'],
    "depends": ['base',
                'crm',
                'l10n_it_base',
                ],
    "data": ["partner_view.xml"],
    'demo': [],
    "installable": True,
    "certificate": ""
}
