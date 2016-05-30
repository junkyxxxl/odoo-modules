# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.############################################################################

from openerp.osv import orm

class website(orm.Model):
    _inherit = 'website'
    
    def get_multiple_images(self, cr, uid,product_id=None,context=None):
        product_img_data=False
        
        if product_id:
            pi_pool = self.pool.get("product.images")
            product_ids = pi_pool.search(cr,uid,[('product_tmpl_id','=',product_id)],order="sequence asc")            
            if product_ids:
                product_img_data=self.pool.get('product.images').browse(cr,uid,product_ids,context)
        return product_img_data

