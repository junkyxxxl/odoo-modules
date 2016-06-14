# -*- coding: utf-8 -*-
from itertools import chain
from openerp import models, fields
import time


class product_pricelist_custom(models.Model):
    _inherit = "product.pricelist"    

    def pricelist_item_get(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        context = context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')
        date = date[0:10]

        products = map(lambda x: x[0], products_by_qty_by_partner)

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i, product_pricelist_version AS v '
            'WHERE (i.product_tmpl_id IS NULL OR i.product_tmpl_id = any(%s)) '
                'AND (i.product_id IS NULL OR (i.product_id = any(%s))) '
                'AND ((i.categ_id IS NULL) OR (i.categ_id = any(%s))) '
                'AND (i.price_version_id = v.id) '
                'AND (v.pricelist_id = %s) '
                'AND (v.active) '
                'AND ((v.date_start IS NULL) OR (v.date_start <= %s) ) '
                'AND ((v.date_end IS NULL) OR (v.date_end >= %s)) '                               
            'ORDER BY v.priority desc, i.sequence, i.min_quantity desc ',
            (prod_tmpl_ids, prod_ids, categ_ids, pricelist.id, date, date))
        
        item_ids = [x[0] for x in cr.fetchall()]
        items = self.pool.get('product.pricelist.item').browse(cr, uid, item_ids, context=context)

        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            results[product.id] = None
            rule_id = False
            
            for rule in items:
                if rule.min_quantity and qty < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and \
                            (product.product_variant_count > 1 or product.product_variant_ids[0].id != rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                results[product.id] = (rule)
                break
        return results       
    
class product_pricelist_item_custom(models.Model):
    
    _inherit = "product.pricelist.item"
    
    is_net_price = fields.Boolean(string="Net Price", default=False)