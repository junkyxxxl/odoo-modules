# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.


import openerp
from openerp import tools
from openerp.osv import osv, fields
from openerp import fields, models

class product_public_category(models.Model):
    _name = "product.public.category"
    _inherit = ["product.public.category","object.carousel.data"]