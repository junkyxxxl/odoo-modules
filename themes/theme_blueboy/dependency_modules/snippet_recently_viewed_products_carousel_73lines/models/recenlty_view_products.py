# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp import fields, models,tools

class ProductTemplateRecentView(models.Model):
    _name = 'product.template.recent.view'
    _inherit = ["object.carousel.data"]
    _order = 'id DESC'

    sessionid = fields.Char('Session ID', index=True)
    product_id = fields.Many2one('product.template', 'Product')
    user_id = fields.Many2one("res.users","User ID")
    
    def get_objects_for_carousel(self,cr,uid,filter_id,limit,context=None):
        res = super(ProductTemplateRecentView,self).get_objects_for_carousel(cr,uid,filter_id,limit,context=context)
        res['objects'] = [object.product_id for object in res['objects']]
        return res