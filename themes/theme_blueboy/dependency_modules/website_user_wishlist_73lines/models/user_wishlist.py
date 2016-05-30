# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp import SUPERUSER_ID
from openerp import fields, models

class user_wishlist(models.Model):
    _name = 'user.wishlist'
    _rec_name = 'product_template_id'
    
    product_template_id = fields.Many2one('product.template','Product')
    qty = fields.Float('Qty')
    user_id = fields.Many2one('res.users','User')

    _defaults = {
                 'qty':lambda *a :1.0,
                 }

class product_template(models.Model):
    _inherit ='product.template'
    
    wishlist_line = fields.One2many('user.wishlist','product_template_id','Wishlist Line')
    
    def is_favorite(self, cr, uid, ids, context=None):
        id = ids[0]        
        if id:
            wishlist_obj=self.pool.get("user.wishlist")
            result_wish=wishlist_obj.search(cr,SUPERUSER_ID,[('product_template_id', '=', id),('user_id','=',uid)],context=context)
            if len(result_wish)>0:
                return True
            else:
                return False
    def add_to_wishlist(self,cr,uid,ids,context=None):
        
        return 