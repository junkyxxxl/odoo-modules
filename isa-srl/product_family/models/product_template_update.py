# -*- coding: utf-8 -*-
from openerp import models, fields


class product_template_update_info(models.Model):

    _inherit = 'product.template'

    family = fields.Many2one('product.family', required=False)
    subfamily = fields.Many2one('product.family', required=False)

    subgroup = fields.Many2one('product.family', string="Sottogruppo", required=False)
    classifier1 = fields.Many2one('product.family', string="Classificatore 1", required=False)
    classifier2 = fields.Many2one('product.family', string="Classificatore 2", required=False)
    classifier3 = fields.Many2one('product.family', string="Classificatore 3", required=False)
