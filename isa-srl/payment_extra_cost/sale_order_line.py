# -*- coding: utf-8 -*-
from openerp import models, fields


class sale_order_line(models.Model):

    _inherit = ['sale.order.line']

    is_payment = fields.Boolean(string='Is a payment')
