# -*- coding: utf-8 -*-
from itertools import chain
from openerp import models, fields, api, _, tools
import time
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
    
class product_pricelist_custom(models.Model):
    _inherit = "product.pricelist"    

    '''
    Questa funzione restituisce i 3 sconti relativi alla voce di listino più appropriata dati partner,prodotto,quantità e listino presi in input.
    '''
    def discounts_get(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
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
            results[product.id] = (0.0,0.0,0.0,0.0)
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

                results[product.id] = (rule.discount1 or 0.0, rule.discount2 or 0.0, rule.discount3 or 0.0, rule.max_discount or 0.0)
                break
        return results    
    
    '''
    Questo metodo rimpiazza quello di base per il reperimento del prezzo unitario dati il prodotto, il partner, la quantità ed il listino.
    La differenza sostanziale col metodo base è che le voci di listino applicabili al caso in esame sono prese tr atutte le versioni attive nel periodo
    (in precedenza esiste una sola versione attiva nel periodo) ed ordinate per priorità. 
    '''    
    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        context = context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')
        date = date[0:10]

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')

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

        ###########################################################################################

        price_types = {}

        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            results[product.id] = 0.0
            rule_id = False
            price = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = product_uom_obj._compute_qty(
                        cr, uid, context['uom'], qty, product.uom_id.id or product.uos_id.id)
                except except_orm:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
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

                if rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._price_get_multi(cr, uid,
                                rule.base_pricelist_id, [(product,
                                qty, partner)], context=context)[product.id]
                        ptype_src = rule.base_pricelist_id.currency_id.id
                        price_uom_id = qty_uom_id
                        price = currency_obj.compute(cr, uid,
                                ptype_src, pricelist.currency_id.id,
                                price_tmp, round=False,
                                context=context)
                elif rule.base == -2:
                    seller = False
                    for seller_id in product.seller_ids:
                        if (not partner) or (seller_id.name.id != partner):
                            continue
                        seller = seller_id
                    if not seller and product.seller_ids:
                        seller = product.seller_ids[0]
                    if seller:
                        qty_in_seller_uom = qty
                        seller_uom = seller.product_uom.id
                        if qty_uom_id != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, qty_uom_id, qty, to_uom_id=seller_uom)
                        price_uom_id = seller_uom
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price

                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                    price_type = price_types[rule.base]

                    # price_get returns the price in the context UoM, i.e. qty_uom_id
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

                    rule_id = rule.id
                break

            # Final price conversion to target UoM
            price = product_uom_obj._compute_price(cr, uid, price_uom_id, price, qty_uom_id)

            results[product.id] = (price, rule_id)
        return results    
    
class product_pricelist_version_custom(models.Model):
    _inherit = "product.pricelist.version"
    
    _order = "priority DESC"
    
    priority = fields.Integer(string="Priority", default=10)
    
    @api.one
    @api.constrains('priority','pricelist_id','active','date_start','date_end')
    def _check_priority(self):
        if self.priority < 0:
            raise ValidationError(_("Priority can't be less than 0!"))            
        if self.active:
            version_ids = self.search([('active','=',True),('priority','=',self.priority),('pricelist_id','=',self.pricelist_id.id),('id','!=',self.id)])
            if version_ids:                
                for version_data in version_ids:
                    t1 = True
                    t2 = True                    
                    if self.date_start:
                        if not version_data.date_end or version_data.date_end >= self.date_start:
                            t1 = True
                        else: 
                            t1 = False
                    if self.date_end:
                        if not version_data.date_start or version_data.date_start <= self.date_end:
                            t2 = True
                        else:
                            t2 = False
                            
                    if t1 and t2:
                            raise ValidationError(_("You cannot have 2 active pricelist versions, with the same priority, that overlap!"))
                            
    def _check_date(self, cursor, user, ids, context=None):
        return True
    
    _constraints = [
        (_check_date, 'You cannot have 2 pricelist versions that overlap!',
            ['date_start', 'date_end'])
    ]    

class product_pricelist_item_custom(models.Model):
    
    _inherit = "product.pricelist.item"
    
    discount1 = fields.Float(string="Sconto1", digits_compute= dp.get_precision('Discount'),)
    discount2 = fields.Float(string="Sconto2", digits_compute= dp.get_precision('Discount'),)
    discount3 = fields.Float(string="Sconto3", digits_compute= dp.get_precision('Discount'),)
    max_discount = fields.Float(string="Sconto Massimo", digits_compute= dp.get_precision('Discount'),)
    
    
    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_discount(self):
        
        if (self.discount1 < 0.0 or self.discount1 > 100.0) or (self.discount2 < 0.0 or self.discount2 > 100.0) or (self.discount3 < 0.0 or self.discount3 > 100.0) or (self.max_discount < 0.0 or self.max_discount > 100.0):          
            raise ValidationError(_("The total discount defined on this pricelist item is greater than 100%, which is not allowed!"))       
            
    @api.one
    @api.constrains('discount1','discount2','discount3','max_discount')
    def _check_limit_discount(self):
        
        total_discount = 100 - (100*((100-self.discount1)/100)*((100-self.discount2)/100)*((100-self.discount3)/100))
        if self.max_discount and total_discount - self.max_discount > 0.0001:            
            raise ValidationError(_("Sum of discounts can't be greater than what setted as maximum discount!"))            
    
    
    @api.model
    def create(self, vals):
        d1 = vals.get('discount1',0.0)
        d2 = vals.get('discount2',0.0)
        d3 = vals.get('discount3',0.0)
        max = vals.get('max_discount',0.0)
        
        if max == 0.0:
            tot = 100.0 - (100.0*((100.0-d1)/100.0)*((100.0-d2)/100.0)*((100.0-d3)/100.0))
            vals.update({'max_discount': tot,})
        return super(product_pricelist_item_custom,self).create(vals)
    
    
    @api.one
    def write(self, vals):        
        d1 = vals.get('discount1',self.discount1)
        d2 = vals.get('discount2',self.discount2)
        d3 = vals.get('discount3',self.discount3)
        max = vals.get('max_discount',self.max_discount)
        
        if max == 0.0:
            tot = 100.0 - (100.0*((100.0-d1)/100.0)*((100.0-d2)/100.0)*((100.0-d3)/100.0))
            vals.update({'max_discount': tot,})
        return super(product_pricelist_item_custom,self).write(vals)
    