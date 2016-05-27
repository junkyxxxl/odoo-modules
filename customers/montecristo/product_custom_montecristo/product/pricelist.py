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
    
class product_pricelist_item_montecristo(osv.osv):
    _inherit = "product.pricelist.item"
    
    def _get_default_base(self, cr, uid, fields, context=None):
        product_price_type_obj = self.pool.get('product.price.type')
        if fields.get('type') == 'purchase':
            product_price_type_ids = product_price_type_obj.search(cr, uid, [('field', '=', 'standard_price')], context=context)
        elif fields.get('type') == 'sale':
            product_price_type_ids = product_price_type_obj.search(cr, uid, [('field','=','list_price')], context=context)
        else:
            return 1
        if not product_price_type_ids:
            return False
        else:
            pricetype = product_price_type_obj.browse(cr, uid, product_price_type_ids, context=context)[0]
            return pricetype.id
    
    ''' QUESTO METODO, MOLTO PIU' PULITO, NON FUNZIONA PERCHE' NON PERMETTE DI SELEZIONARE LA VERSIONE DEL 
        LISTINO CHE SI INTENDE VISUALIZZARE, PERTANTO, LE FUNZIONI RICHIAMATE SELEZIONANO (TENDENZIALMENTE)
        IL PRIMO pricelist_item CHE MATCHA I PARAMETRI DI PRODOTTO,TEMPLATE,CATEGORIA,LISTINO ... GENERALMENTE
        CE NE SONO ALMENO 4
    
    
    def _get_price(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rule in self.browse(cr, uid, ids, context=context):
            result[rule.id] = []
            pricelist = rule.price_version_id.pricelist_id
            price_dict = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist.id], rule.product_id.id, rule.min_quantity, context=context)
            if price_dict[pricelist.id]:
                price = price_dict[pricelist.id]
            else:
                res = self.pool.get('product.product').read(cr, uid, [rule.product_id.id])
                price = res[0]['list_price']
            result[rule.id] = price
        return result
    '''
    
    def _get_final_price(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')
        price_types = {}
                    
        
        for rule in self.browse(cr, uid, ids, context=context):
            result[rule.id] = []
            if (not rule.product_id and not context.get('parent_id')) or not rule.price_version_id or not rule.price_version_id.pricelist_id:
                continue
            
            product = rule.product_id or self.pool.get('product.product').browse(cr,uid,context.get('parent_id'))
            pricelist = rule.price_version_id.pricelist_id
            
            if rule.base == -1:
                if rule.base_pricelist_id:
                    price_tmp = self.pool.get('product.pricelist')._price_get_multi(cr, uid,
                            rule.base_pricelist_id, [(product,
                            rule.min_quantity or 1, False)], context=context)[product.id]
                    ptype_src = rule.base_pricelist_id.currency_id.id
                    price_uom_id = product.uom_id.id
                    price = currency_obj.compute(cr, uid,
                            ptype_src, pricelist.currency_id.id,
                            price_tmp, round=False,
                            context=context)
            
            elif rule.base == -2:
                seller = False
                for seller_id in product.seller_ids:
                    seller = seller_id
                if not seller and product.seller_ids:
                    seller = product.seller_ids[0]
                if seller:
                    for line in seller.pricelist_ids:
                        price = line.price

            else:
                if rule.base not in price_types:
                    price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                price_type = price_types[rule.base]

                # price_get returns the price in the context UoM, i.e. qty_uom_id
                price = currency_obj.compute(
                        cr, uid,
                        price_type.currency_id.id, 
                        pricelist.currency_id.id,
                        product_obj._price_get(cr, uid, [product], price_type.field, context=context)[product.id],
                        round=False, context=context)

            if price is not False:
                price_limit = price
                price = price * (1.0+(rule.price_discount or 0.0))
                if rule.price_round:
                    price = tools.float_round(price, precision_rounding=rule.price_round)

                if rule.price_surcharge:
                    price_surcharge = rule.price_surcharge
                    price += price_surcharge

                if rule.price_min_margin:
                    price_min_margin = rule.price_min_margin
                    price = max(price, price_limit + price_min_margin)

                if rule.price_max_margin:
                    price_max_margin = rule.price_max_margin
                    price = min(price, price_limit + price_max_margin)


            result[rule.id] = price
        return result

    
    _columns = {
        'final_price': fields.function(_get_final_price, method=True, type='float', string='Prezzo', store=False),          
        
    }     
    
            
    _defaults = {
        'base': _get_default_base,
        'sequence': -1,    
    }  
    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('sequence') or vals.get('sequence')<0:
            if vals.get('product_id'):
                vals.update({'sequence': 3})
            elif vals.get('product_tmpl_id'):
                vals.update({'sequence': 6})
            elif vals.get('categ_id'):
                vals.update({'sequence': 8})
            else:
                vals.update({'sequence': 10})                                    
        return super(product_pricelist_item_montecristo, self).create(cr, uid, vals, context=context)    