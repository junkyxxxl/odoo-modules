# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api, _, tools


class product_pricelist_item_custom(models.Model):
    
    _inherit = "product.pricelist.item"
    
    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_limit_discount(self):
        None            
        
    def run_update_lst_price(self, cr, uid, context=None):
        
        company_ids = self.pool.get('res.company').search(cr, uid, [('id','>',0)], context=context)
        currency_obj = self.pool.get('res.currency')        
        price_type_obj = self.pool.get('product.price.type')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        
        for company_id in company_ids:
            
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            if not company.pricelist_for_recompute:
                continue
            
            partner = company.partner_id
            date = time.strftime('%Y-%m-%d')
            date = date[0:10]
            
            version_id = self.pool.get('product.pricelist.version').search(cr, uid, [('pricelist_id','=',company.pricelist_for_recompute.id),('active','=',True),'|',('date_start','<=',date),('date_start','=',None),'|',('date_end','>=',date),('date_end','=',None)],order='priority desc',limit=1)
            if not version_id:
                continue
            version_id = version_id[0]

            price_types = {}            
            rule_ids = []
            product_ids = []
            
            for rule in self.pool.get('product.pricelist.version').browse(cr, uid, version_id, context=context).items_id:
                if rule.categ_id and not rule.product_tmpl_id and not rule.product_id and rule.base != -2:
                    rule_ids.append(rule.id)
                    pricelist = rule.base_pricelist_id
                    
                    for product_id in self.pool.get('product.product').search(cr, uid, [('categ_id','=',rule.categ_id.id)],context=context):
                        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                        
                        product_ids.append(product.id)
                        
                        qty = rule.min_quantity or 1.0
                        qty_uom_id = product.uom_id.id
                        
                        
                        if rule.base == -1:
                            if rule.base_pricelist_id:
                                price_tmp = pricelist_obj._price_get_multi(cr, uid,
                                        rule.base_pricelist_id, [(product,
                                        qty, partner)], context=context)[product.id]
                                ptype_src = rule.base_pricelist_id.currency_id.id
                                price_uom_id = qty_uom_id
                                price = currency_obj.compute(cr, uid,
                                        ptype_src, pricelist.currency_id.id,
                                        price_tmp, round=False,
                                        context=context)

                        else:
                            if rule.base not in price_types:
                                price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                            price_type = price_types[rule.base]
        
                            price_uom_id = qty_uom_id
                            price = currency_obj.compute(
                                    cr, uid,
                                    price_type.currency_id.id, pricelist.currency_id.id,
                                    product_obj._price_get(cr, uid, [product], price_type.field, context=context)[product.id],
                                    round=False, context=context)                    
                        
                        if price is not False:
                            price_limit = price
                            price = price * (1.0+(rule.price_discount or 0.0))
                            if rule.price_round:
                                price = tools.float_round(price, precision_rounding=rule.price_round)
        
                            convert_to_price_uom = (lambda price: product_uom_obj._compute_price(
                                                        cr, uid, product.uom_id.id,
                                                        price, price_uom_id))
                            if rule.price_surcharge:
                                price_surcharge = convert_to_price_uom(rule.price_surcharge)
                                price += price_surcharge
        
                            if rule.price_min_margin:
                                price_min_margin = convert_to_price_uom(rule.price_min_margin)
                                price = max(price, price_limit + price_min_margin)
        
                            if rule.price_max_margin:
                                price_max_margin = convert_to_price_uom(rule.price_max_margin)
                                price = min(price, price_limit + price_max_margin)
        
                            self.pool.get('product.product').write(cr, uid, product.id, {'lst_price':price}, context=context)
            
        return True        
    