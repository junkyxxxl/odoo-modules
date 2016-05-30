# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.


from openerp import models

class product_brand(models.Model):
    _name = "product.brand"
    _inherit = ["product.brand","object.carousel.data"]