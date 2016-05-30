# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.


from openerp import fields, models

class product_tag(models.Model):
    _name = 'product.tag'
    
    name = fields.Char('Name', required=True,translate=True)
    product_ids = fields.Many2many('product.template', string='Products')
    
    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class product_template(models.Model):
    _inherit = "product.template"
    
    tag_ids = fields.Many2many('product.tag', string='Tags')