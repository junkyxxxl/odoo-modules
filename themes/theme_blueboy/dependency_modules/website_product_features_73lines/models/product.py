# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp import fields, models
from openerp import SUPERUSER_ID

class product_feature(models.Model):
    _name = 'product.feature'
    _description="product.feature.value"
    _order = 'sequence,id'
    
    sequence = fields.Integer('Sort Order')
    name = fields.Char('Feature Name',translate=True, required=True)
    value_ids = fields.One2many('product.feature.value', 'feature_id', 'Values', copy=True)
    feature_line_ids = fields.One2many('product.feature.line', 'feature_id', 'Lines')
    
class product_feature_value(models.Model):
    _name = 'product.feature.value'
    _description="product.feature.value"    
    _order = 'sequence'
    
    sequence =  fields.Integer('Sequence', help="Determine the display order")
    name =  fields.Char('Value', translate=True, required=True)
    feature_id = fields.Many2one('product.feature', 'Feature', required=True, ondelete='cascade')

    _sql_constraints = [
        ('value_company_uniq', 'unique (name,feature_id)', 'This feature value already exists !')
    ]
    
    def name_get(self, cr, uid, ids, context=None):
        if context and not context.get('show_feature', True):
            return super(product_feature_value, self).name_get(cr, uid, ids, context=context)
        res = []
        for value in self.browse(cr, uid, ids, context=context):
            res.append([value.id, "%s: %s" % (value.feature_id.name, value.name)])
        return res

class product_feature_line(models.Model):
    _name = "product.feature.line"
    _rec_name = 'feature_id'
    
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', required=True, ondelete='cascade')
    feature_id =  fields.Many2one('product.feature', 'Feature', required=True, ondelete='restrict')
    value_ids = fields.Many2many('product.feature.value', id1='line_id', id2='val_id', string='Feature Values')
    
    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            new_args = ['|', ('feature_id', operator, name), ('value_ids', operator, name)]
        else:
            new_args = args
        return super(product_feature_line, self).name_search(
            cr, uid, name=name,
            args=new_args,
            operator=operator, context=context, limit=limit)


    
class product_template(models.Model):
    _inherit = 'product.template'
    _description = "Product Template"
    
    feature_line_ids = fields.One2many('product.feature.line', 'product_tmpl_id', 'Product Features')
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if 'search_default_feature_line_ids' in context and context.get('search_default_feature_line_ids'):
            sfl_ids = self.pool.get('product.feature.line').search(cr,SUPERUSER_ID,
                                                                   [['value_ids','in',
                                                                     context.get('search_default_feature_line_ids')]
                                                                    ],context=context)
            args.append(['feature_line_ids','in',sfl_ids])
        return super(product_template, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)