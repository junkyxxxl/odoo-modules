# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
{
    "name": "Website: Stock Notify",
    "category": 'Website',
    "summary": """
        Send e-mail notifications to your customers, when product is in-stock.""",
    "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: website_customer_email/static/src/img/icon-features.png
.. |icon_support| image:: website_customer_email/static/src/img/icon-support.png
.. |icon_help| image:: website_customer_email/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '1.0',
    "depends": ['website_stock', 'email_template'],
    "data": [

        'data/stock_notify_cron.xml',
        'edi/website_notify_edi.xml',
        'data/stock_action_server.xml',
        'wizard/stock_notify_wizard.xml',
        'views/website_stock_notification_template.xml',
        'views/website_stock_notification_view.xml',
        'views/stock_notify_config_view.xml',
        'views/webkul_addons_config_inherit_view.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "images":['static/description/main.png'],
    "price": 15,
    "currency": 'EUR',
}