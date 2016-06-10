# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
{
    "name": "Website: Onepage Checkout",
    "category": 'Website',
    "summary": """
       Onepage Checkout for Website""",
    "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: website_onepage_checkout/static/src/img/icon-features.png
.. |icon_support| image:: website_onepage_checkout/static/src/img/icon-support.png
.. |icon_help| image:: website_onepage_checkout/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '1.0',
    "depends": ['base','website_sale_delivery', 'website_webkul_addons'],
    "data": [
        'data/set_onpage_checkout_defaults.xml',
        'views/templetes.xml',
        'views/res_config_view.xml',
        'data/onepage_checkout_data.xml',
        'views/webkul_addons_config_inherit_view.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 99,
    "currency": 'EUR',
    "images":['static/description/panel-1.png']
}