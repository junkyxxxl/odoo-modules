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

class bom_product_price(osv.osv):
    _name = 'bom.product.price'
    
    _columns = {
                'product_id':fields.many2one('product.product',string='Prodotto',required=True, ondelete='cascade',),
                'first_price': fields.float('Costo Primo', digits_compute= dp.get_precision('Product Price')),
                'bom_id':fields.many2one("mrp.bom","Distinta Base"),
    }
    
class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    _columns = {
        'season': fields.related('product_tmpl_id', 'produzione', type = 'many2one', relation = 'res.family', string = 'Season', store = True),
        'family': fields.related('product_tmpl_id', 'famiglia', type = 'many2one', relation = 'res.family', string = 'Family', store = True),
        'price_per_variant_ids': fields.one2many('bom.product.price','bom_id','Prezzi per Variante'), 
    }

    def _compute_variant_price(self, cr, uid, product, bom_data, context=None):
        total = 0.0
    #3 #4
        for bom_line in bom_data.bom_line_ids:
    #5
            to_continue = True
            for attribute_value in bom_line.attribute_value_ids:
                if attribute_value not in product.attribute_value_ids:
                    to_continue = False
                if to_continue:
                    bom_ids = self.search(cr, uid, [('product_tmpl_id','=',bom_line.product_id.product_tmpl_id.id),('product_id','=',bom_line.product_id.id)]) or self.search(cr, uid, [('product_tmpl_id','=',bom_line.product_id.product_tmpl_id.id),('product_id','=',None)])
        #6
                    if bom_ids:
        #7
                        total = total + self._compute_variant_price(cr, uid, product, self.browse(cr, uid, bom_ids[0]), context = context)
        #8
                    else:
        #9 #10
                        total = total + bom_line.product_qty*(2-bom_line.product_efficiency)*bom_line.product_id.standard_price
        return total 
        
    def compute_variant_price(self, cr, uid, ids, context=None):
        bom_data = self.browse(cr,uid,ids[0])
        self.pool.get('bom.product.price').unlink(cr,uid,bom_data.price_per_variant_ids.ids)
        product_obj = self.pool.get('product.product')
        first_prices = []
    #1        
        if bom_data.product_id:
            products = bom_data.product_id
        else:
            products = bom_data.product_tmpl_id.product_variant_ids
    #2    
        for product in products:
    #11
            first_prices.append({'product_id': product.id, 'first_price': self._compute_variant_price(cr, uid, product, bom_data, context = context)})
                        
        for first_price in first_prices:
            self.pool.get('bom.product.price').create(cr,uid, {'bom_id':ids[0],'product_id':first_price['product_id'],'first_price':first_price['first_price']})
        
        return True                                                 
    '''
    def _check_uniq(self, cr, uid, ids, context=None):
        for bom in self.browse(cr, uid, ids, context=context):
            if bom.product_tmpl_id:
                if bom.product_id:
                    check = self.search(cr, uid, [('product_tmpl_id','=',bom.product_tmpl_id.id),('product_id','=',bom.product_id.id),('id','!=',bom.id)])
                else:
                    check = self.search(cr, uid, [('product_tmpl_id','=',bom.product_tmpl_id.id),('product_id','=',None),('id','!=',bom.id)])
                if check:
                    return False
            else:
                return False            
        return True
    
    _constraints = [(_check_uniq, 'There is already a BoM for the selected product', ['product_tmpl_id','product_id'])]    
    '''