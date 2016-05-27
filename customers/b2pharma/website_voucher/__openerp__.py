# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
{
    'name': 'Website Coupons & Vouchers',
    'summary': 'Create vouchers with unique codes to provide special discounts.',
    'version': '0.1',
    'category': 'Website',
    'description': """


Features:
---------
    * Gives an option to create Coupons/Vouchers.
    * Gives an option to use Coupons/Vouchers which makes some discount in Current Order in Website.
    * Manage Coupons`s validity, Disount Values, etc.

""",
    'author': 'Webkul Software Pvt. Ltd.',
    'website': 'http://www.webkul.com',
	'data': [
            'report/report.xml',
            "views/voucher_view.xml",
            "wizard/wizard_message_view.xml",
            "views/voucher_web_view.xml",
            'report/report_template.xml',
            'security/ir.model.access.csv',
            'coupon_data.xml'
            ],
    'depends' : ['website_sale','product','sale'],
    "images":['static/description/Banner.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 69,
    "currency": 'EUR',
}
