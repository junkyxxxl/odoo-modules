# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from openerp.osv import osv

class product_template(osv.osv):
    _inherit = "product.template"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        new_domain = []
        if context.get('price_range_from'):
              new_domain.append(['list_price','>=',context.get('price_range_from')])
        if context.get('price_range_to'):
            new_domain.append(['list_price','<=',context.get('price_range_to')])
        args.extend(new_domain)
        return super(product_template, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)