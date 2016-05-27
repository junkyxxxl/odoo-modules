# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class product_pricelist_item_custom(models.Model):
    
    _inherit = "product.pricelist.item"
    
    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_limit_discount(self):
        None            
    