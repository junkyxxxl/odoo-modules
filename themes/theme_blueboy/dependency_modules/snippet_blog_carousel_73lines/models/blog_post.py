# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp import fields, models

class blog_post(models.Model):
    _name = "blog.post"
    _inherit = ["blog.post","object.carousel.data"]