# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.


from openerp import fields, models

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'
    _order = 'name'
    
    name = fields.Char('Name', required=True,translate=True)
    brand_image = fields.Binary("Brand Image",attachment=True)
    product_line = fields.One2many('product.template','brand_id', string='Products')
    
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Brand name already exists !"),
    ]
    

class product_template(models.Model):
    _inherit = "product.template"
        
    brand_id = fields.Many2one('product.brand', string='Brand')
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if 'search_default_brand_id' in context and context.get('search_default_brand_id'):
            args.append(['brand_id','in',context.get('search_default_brand_id')])
        return super(product_template, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)