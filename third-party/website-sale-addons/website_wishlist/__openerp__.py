# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
{
    "name": "Website: Product Wishlist",
    "category": 'Website',
    "summary": """Add products to your wishlist for later purchase. """,
    "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: website_wishlist/static/src/img/icon-features.png
.. |icon_support| image:: website_wishlist/static/src/img/icon-support.png
.. |icon_help| image:: website_wishlist/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "sequence": 1,
    "images":['static/description/wishlist.png'],
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '1.1',
    "depends": ['base','website_sale', 'website_stock'],
    "data": [
        'views/templates.xml',
        'views/wk_wishlist.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 39,
    "currency": 'EUR',
}