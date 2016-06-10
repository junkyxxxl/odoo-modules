# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

{
    "name": "Website: Product Multi Images",
    "category": 'Website',
    "summary": """
        Add multiple images for the products on your website. """,
    "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: website_multi_image/static/src/img/icon-features.png
.. |icon_support| image:: website_multi_image/static/src/img/icon-support.png
.. |icon_help| image:: website_multi_image/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '1.0',
    "depends": ['website_sale'],
    "data": [
        'view/product_extra_images_view.xml',
        'view/templates.xml',
	'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 49,
    "currency": 'EUR',
    "images":['static/description/main.png']
}