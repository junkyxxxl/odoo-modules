# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp.osv import osv
from openerp import SUPERUSER_ID

class website(osv.Model):
    _inherit = 'website'
                
    def get_product_brand(self,cr,uid,ids,category,context=None):
        brand_pool = self.pool.get("product.brand")
        if category is None:
            domain = []
        else:
            domain = [('public_categ_ids','child_of',[category.id])]
        product_ids = self.pool.get("product.template").search(cr,SUPERUSER_ID,domain,context=context)
        domain = [('product_line','in',product_ids or [])]
        brand_ids = brand_pool.search(cr,SUPERUSER_ID,domain,context=context)
        brand_obj = brand_pool.browse(cr,SUPERUSER_ID,brand_ids,context=context)
        return brand_obj