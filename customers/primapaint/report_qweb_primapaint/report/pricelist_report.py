# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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

import math
import time
from openerp.report import report_sxw
from openerp.osv import osv
from datetime import date, datetime, timedelta


class report_pricelist_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_pricelist_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_records': self._get_records,
            'get_family': self._get_family,
            'get_subfamily': self._get_subfamily,
            'get_locations': self._get_locations, 
            'get_location_names': self._get_location_names,     
            'get_pricelist': self._get_pricelist,        
            'get_date_today': self._get_date_today,
            'get_show_hand': self._get_show_hand,
        })
        self.context = context

    def _get_locations(self, data):
        records = [0, 0]
        if not data or not 'form' in data or not data['form'] or 'stock_location_ids' not in data['form'] or not data['form']['stock_location_ids']:
            return records
        
        t_records = []
        for stock in self.pool.get('stock.location').browse(self.cr, self.uid, data['form']['stock_location_ids'], context=self.context):
            t_records.append(stock.id)
            
        t_records = list(reversed(t_records))
        
        for i in range(len(t_records)):
            if i < 2:
                records[i] = t_records[i]        
                
        return records
                
    def _get_location_names(self, data):
        records = ['','']
        if not data or not 'form' in data or not data['form'] or 'stock_location_ids' not in data['form'] or not data['form']['stock_location_ids']:
            return records
        
        t_records = []
        for stock in self.pool.get('stock.location').browse(self.cr, self.uid, data['form']['stock_location_ids'], context=self.context):
            t_records.append(stock.location_id.name+'/'+stock.name)
            
        t_records = list(reversed(t_records))
        
        for i in range(len(t_records)):
            if i < 2:
                records[i] = t_records[i]                    
                
        return records
    
    def _get_show_hand(self, data):
        if not data or not 'form' in data or not data['form'] or 'show_onhand' not in data['form']:
            return False
        return data['form']['show_onhand']
    
    def _get_family(self, data):
        if not data or not 'form' in data or not data['form'] or 'family' not in data['form'] or not data['form']['family']:
            return False
        return self.pool.get('product.family').browse(self.cr, self.uid, data['form']['family'][0], context=self.context)
    
    def _get_subfamily(self, data):
        if not data or not 'form' in data or not data['form'] or 'subfamily' not in data['form'] or not data['form']['subfamily']:
            return False
        return self.pool.get('product.family').browse(self.cr, self.uid, data['form']['subfamily'][0], context=self.context)    
    
    def _get_pricelist(self, data):
        if not data or not 'form' in data or not data['form'] or 'pricelist' not in data['form'] or not data['form']['pricelist']:
            if 'active_ids' in self.context and self.context['active_ids']:
                return self.pool.get('product.pricelist').browse(self.cr, self.uid, self.context['active_ids'][0], context=self.context)
            return False
        return self.pool.get('product.pricelist').browse(self.cr, self.uid, data['form']['pricelist'], context=self.context)        

    def _get_date_today(self):
        date_today= datetime.strftime( datetime.today(), '%d/%m/%Y')
        return date_today

    def _get_records(self, pricelist, family, subfamily, location_ids, show_onhand):
        records = []        
        
        product_obj = self.pool.get('product.product')
        quant_obj = self.pool.get('stock.quant')
        pricelist_item_obj = self.pool.get('product.pricelist.item')
                
        #DATA UNA FAMIGLIA ED UNA SOTTOFAMIGLIA, ESTRAGGO TUTTI I PRODOTTI ATTIVI
        domain = []
        domain.append(('active','=',True))        
        if family:
            domain.append(('family','=',family.id))
        if subfamily:
            domain.append(('subfamily','=',subfamily.id))        
        prod_ids = product_obj.search(self.cr, self.uid, domain, context=self.context)     
                        
        
        version_ids = self.pool.get('product.pricelist.version').search(self.cr, self.uid, [('pricelist_id','=',pricelist.id),('active','=',True)], context=self.context)
        version = self.pool.get('product.pricelist.version').browse(self.cr, self.uid, version_ids, context=self.context)

        #RAGGRUPPO I PRODOTTI DIVIDENDOLI PER FAMIGLIA E SOTTOFAMIGLIA
        prod_group = {}
        if family and subfamily:
            key = (family,subfamily)
            prod_group[key] = prod_ids
        else:
            for product_id in prod_ids:
                product = product_obj.browse(self.cr, self.uid, product_id, context=self.context)                 
                key = (product.family,product.subfamily)
                if key not in prod_group:
                    prod_group[key] = []
                prod_group[key].append(product.id)
        
        for key in prod_group.keys():
            
            item = []
            item.append('Family: '+((key[0] and key[0].name) or 'Others'))      #[0]
            item.append('Subamily: '+((key[1] and key[1].name) or 'Others'))    #[1]
            
            for i in range(5):
                item.append(None)                                               #[2,3,4,5,6,7]
            
            item.append('#DDDDDD')
            
            item.append(1)                                                      #[8]
            records.append(item)
            
            pair = True
            for product_id in prod_group[key]:
                product = product_obj.browse(self.cr, self.uid, product_id, context=self.context)            
                
                #PER OGNI PRODOTTO, ESTRAGGO TUTTE LE VOCI DI LISTINO CHE LO RIGUARDANO
                pricelist_items = []            
                t_items = pricelist_item_obj.search(self.cr, self.uid, [('price_version_id','=',version.id),('product_id','=',product.id)],context=self.context)
                if t_items:
                    pricelist_items = pricelist_item_obj.browse(self.cr,self.uid,t_items,context=self.context)
                if not pricelist_items:
                    t_items = pricelist_item_obj.search(self.cr, self.uid, [('price_version_id','=',version.id),('product_tmpl_id','=',product.product_tmpl_id.id),('product_id','in',[None,False])], context=self.context)
                    if t_items:
                        pricelist_items = pricelist_item_obj.browse(self.cr,self.uid,t_items,context=self.context)
                if not pricelist_items:
                    t_items = pricelist_item_obj.search(self.cr, self.uid, [('price_version_id','=',version.id),('categ_id','=',product.categ_id.id),('product_tmpl_id','in',[None,False]),('product_id','in',[None,False])],context=self.context)
                    if t_items:
                        pricelist_items = pricelist_item_obj.browse(self.cr,self.uid,t_items,context=self.context)                
                if not pricelist_items:
                    t_items = pricelist_item_obj.search(self.cr, self.uid, [('price_version_id','=',version.id),('categ_id','in',[False,None]),('product_tmpl_id','in',[None,False]),('product_id','in',[None,False])],context=self.context)
                    if t_items:
                        pricelist_items = pricelist_item_obj.browse(self.cr,self.uid,t_items,context=self.context)                             
                if not pricelist_items:
                    continue
    
                for pricelist_item in pricelist_items:
                    item = []
                    
                    item.append(product.default_code)   #[0]
                    
                    name = product.name
                    if product.attribute_value_ids:
                        name2 = ''
                        for attr_val in product.attribute_value_ids:
                            name2 += attr_val.name + ', '
                        name2 = name2[:len(name2)-2]
                        name = name+' ('+name2+')'
                    
                    item.append(name)           #[1]                    

                    item.append(product.uom_id.name)    #[2]
                    
                    #[3,4]
                    for id in location_ids:                
                        if id == 0:
                            item.append('')
                        else:
                            tot = 0.0
                            quant_ids = quant_obj.search(self.cr,self.uid,[('product_id','=',product_id),('location_id','=',id)])
                            for quant_id in quant_ids:
                                tot += quant_obj.browse(self.cr,self.uid,quant_id,context=self.context).qty
                            if tot != 0:
                                item.append(str(tot))
                            else:
                                item.append('')
                    #/[3,4]
                    
                    #[5]
                    tot = pricelist_item.min_quantity
                    if tot != 0.0:
                        item.append(str(tot))
                    else:
                        tot += 1
                        item.append('')
                    #/[5]
                    
                    #[6]
                    sale_price_digits = self.get_digits(dp='Product Price')
                    price_dict = self.pool.get('product.pricelist').price_get(self.cr, self.uid, [pricelist.id], product.id, tot, context=self.context)
                    if price_dict[pricelist.id]:
                        price = self.formatLang(price_dict[pricelist.id], digits=sale_price_digits, currency_obj=pricelist.currency_id)
                        item.append(price)
                    else:
                        item.append('/')
                    #/[6]
                    
                    #[7]
                    if pair: item.append('#FFFFFF')
                    else: item.append('#DDDDDD')
                    #/[7]

                    item.append(0)      #[8]
                    
                    pair = not pair
                    records.append(item)

        return records
    
class report_pricelist(osv.AbstractModel):
    _name = 'report.report_qweb_primapaint.report_pricelist'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_primapaint.report_pricelist'
    _wrapped_report_class = report_pricelist_parser
