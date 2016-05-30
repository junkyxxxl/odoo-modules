# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp.osv import osv
from openerp import SUPERUSER_ID

class website(osv.Model):
    _inherit = 'website'
                
    def get_product_tags(self,cr,uid,ids,context=None):
        tag_pool = self.pool.get("product.tag")
        tag_ids = tag_pool.search(cr,SUPERUSER_ID,[],context=context)
        tag_obj = tag_pool.browse(cr,SUPERUSER_ID,tag_ids,context=context)
        return tag_obj