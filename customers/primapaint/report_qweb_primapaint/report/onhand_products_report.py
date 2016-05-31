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


class report_onhand_products_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_onhand_products_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_records': self._get_records,
            'get_stocks': self._get_stocks,
            'get_families': self._get_families,
            'get_picking_types': self._get_picking_types,
            'get_date_today': self._get_date_today,
            'get_months': self._get_months,
        })
        self.context = context

    def _get_stocks(self, doc):
        records = [('',''),('',''),('','')]
        
        t_records = []
        for stock in doc.stock_ids:
            t_records.append((stock.complete_name,stock.location_id.name+'/'+stock.name))
            
        t_records = list(reversed(t_records))
            
        if len(t_records) > 3:
            records[2] = ('...','...')
            for i in range(2):
                records[i] = t_records[i]        
        else:
            for i in range(len(t_records)):
                records[i] = t_records[i]        
        return records
    
    def _get_families(self, doc):
        records = ['','','','']
        
        t_records = []
        for family in doc.family_ids:
            t_records.append(family.name)
            
        if len(t_records) > 4:
            records[3] = '...'
            for i in range(3):
                records[i] = t_records[i]        
        else:
            for i in range(len(t_records)):
                records[i] = t_records[i]        
        return records    
    
    def _get_picking_types(self, doc):
        records = ['','','','','']
        
        t_records = []
        for type in doc.picking_type_ids:
            t_records.append(type.name)
            
        if len(t_records) > 5:
            records[4] = '...'
            for i in range(4):
                records[i] = t_records[i]        
        else:
            for i in range(len(t_records)):
                records[i] = t_records[i]        
        return records        

    def _get_date_today(self):
        date_today= datetime.strftime( datetime.today(), '%d/%m/%Y')
        return date_today

    def _get_months(self):
        months = []
        date_today = datetime.today().replace(day=15)
        for i in range(12):
            td = timedelta(days=(-30*i))
            t_date = date_today+td
            months.append(datetime.strftime( t_date, '%m-%Y'))
        return months

    def _get_stock_ids(self, doc):
        stock_ids = doc.stock_ids.ids
        stock_ids = list(reversed(stock_ids))        
        if len(stock_ids) < 2:
            for i in range(2-len(stock_ids)):
                stock_ids.append(0)
        elif len(stock_ids) > 2:
            stock_ids = stock_ids[0:2] 

        return stock_ids        
        
    def _get_month_limits(self):
        months = []
        date_reference = datetime.today().replace(day=1,hour=0,minute=0,second=0)
        reference_month = date_reference.month
        reference_year = date_reference.year
        td = timedelta(days=(-1))        
        for i in range(12):
            start_date = date_reference
            
            if reference_month == 12:
                next_month = 1
                next_year = reference_year + 1
            else:
                next_month = reference_month +1
                next_year = reference_year
            
            end_date = start_date.replace(month=next_month, year=next_year, hour=23, minute=59, second=59) + td            
            months.append((datetime.strftime(start_date,'%Y-%m-%d'),datetime.strftime(end_date,'%Y-%m-%d')))            
            
            if reference_month == 1:
                reference_month = 12
                reference_year -= 1
            else:
                reference_month -= 1
                reference_year = reference_year
            
            date_reference = date_reference.replace(month=reference_month, year=reference_year)
            
        return months

    def _get_records(self, doc):
        records = []        
        
        product_obj = self.pool.get('product.product')
        quant_obj = self.pool.get('stock.quant')
        mov_obj = self.pool.get('stock.move')
        
        prod_ids = product_obj.search(self.cr, self.uid, [('family','in',doc.family_ids.ids),('active','=',True)], context=self.context)        
        month_limits = self._get_month_limits()        
        stock_ids = self._get_stock_ids(doc)
        ptype_ids = doc.picking_type_ids.ids
        
        pair = True
        
        for product_id in prod_ids:
            product = product_obj.browse(self.cr, self.uid, product_id, context=self.context)            
            
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
            
            #[2,3,4]
            for id in stock_ids:                
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
            item.append('')
            #/[2,3,4]
            
            #[5]
            tot = product.incoming_qty
            if tot != 0.0:
                item.append(str(tot))
            else:
                item.append('')
            #/[5]
            
            #[6,7,8,9,10,11,12,13,14,15,16,17]
            tot_months = {}
            for month in month_limits:
                tot_months[month[0][0:7]] = 0.0
            
            move_ids = mov_obj.search(self.cr,self.uid,[('product_id','=',product_id),('picking_type_id','in',ptype_ids),('state','=','done'),'|',('location_dest_id','in',stock_ids),('location_id','in',stock_ids)])            
            for move_id in move_ids:
                move = mov_obj.browse(self.cr, self.uid, move_id, context=self.context)
                date = move.date.split(' ')[0] 
                for month in month_limits:
                    if date >= month[0] and date <= month[1]:
                        if move.location_dest_id.id in stock_ids:
                            tot_months[month[0][0:7]] += move.product_uom_qty
                        elif move.location_id.id in stock_ids:
                            tot_months[month[0][0:7]] -= move.product_uom_qty
                        break
            
            for month in month_limits:
                if tot_months[month[0][0:7]] != 0:
                    item.append(str(tot_months[month[0][0:7]]))
                else:
                    item.append('')
            #/[6,7,8,9,10,11,12,13,14,15,16,17]
            
            #[18]
            if pair: item.append('#FFFFFF')
            else: item.append('#EEEEEE')
            #/[18]
            
            pair = not pair
            records.append(item)

        return records
    
class report_onhand_products(osv.AbstractModel):
    _name = 'report.report_qweb_primapaint.report_onhand_products'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_primapaint.report_onhand_products'
    _wrapped_report_class = report_onhand_products_parser
