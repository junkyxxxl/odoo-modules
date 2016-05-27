# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
    
class product_product_montecristo(osv.osv):
    _inherit = "product.product"
    
    _columns = {
            'ean13': fields.char('Barcode', size=128, help="International Article Number used for product identification."),
            'pricelist_ids': fields.one2many('product.pricelist.item','product_id','Listini'),
            'template_pricelist_ids': fields.related('product_tmpl_id','pricelist_ids', type='one2many', relation='product.pricelist.item', string='Listini Padre'),
            'standard_price': fields.property(type = 'float', digits_compute=dp.get_precision('Product Price'),  help="Cost price of the product template used for standard stock valuation in accounting and used as a base price on purchase orders.", groups="base.group_user", string="Cost Price"),
            'sale_ok' : fields.boolean('Può essere venduto'), 
    }

    def remove_from_quotation(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        template_obj = self.pool.get('product.template')

        order_ids = order_obj.search(cr, uid, [('state','in',['draft','sent']),('document_type_id','in',[False,None])],context=context)        
        p_ids = product_obj.search(cr, uid, [('active','=',True),('sale_ok','=',False),('id','in',ids)],context=context)            
        line_ids = order_line_obj.search(cr, uid, [('order_id','in',order_ids),('product_id','in',p_ids)],context=context) 
        
        if line_ids:
            order_line_obj.unlink(cr,uid,line_ids,context=context)
          
        return    
        
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        value_obj = self.pool.get('product.attribute.value')
        if 'sale_ok' in context:
            vals.update({'sale_ok':context['sale_ok']})
        
        if 'standard_price' in context:
            vals.update({'standard_price':context['standard_price']})
            
        if 'tmpl_default_code' in context:
            default_code = context['tmpl_default_code']
            ean13 = context['tmpl_default_code']
            if 'attribute_value_ids' in vals and len(vals['attribute_value_ids'][0]) == 3:
                default_code=default_code+'-'
                
                #INSERISCO IL RIFERIMENTO COLORE (POSIZIONE RIGA)
                for value_id in vals['attribute_value_ids'][0][2]:
                    value_data = value_obj.browse(cr,uid,value_id)
                    if value_data.attribute_id.position == 'row':
                        default_code = default_code+value_data.name
                        ean13 = ean13+value_data.name
                #INSERISCO IL RIFERIMENTO TAGLIA (POSIZIONE COLONNA)
                for value_id in vals['attribute_value_ids'][0][2]:
                    value_data = value_obj.browse(cr,uid,value_id)
                    if value_data.attribute_id.position == 'column':
                        default_code = default_code+value_data.name
                        ean13 = ean13+value_data.name
                
                vals.update({'default_code':default_code, 'ean13':ean13})

        return super(product_product_montecristo, self).create(cr, uid, vals, context)

    def _check_ean_key(self, cr, uid, ids, context=None):
        return True
    
    _defaults = {
                 'sale_ok':True,
    }

    _constraints = [(_check_ean_key, 'You provided an invalid "EAN13 Barcode" reference. You may use the "Internal Reference" field instead.', ['ean13'])]
