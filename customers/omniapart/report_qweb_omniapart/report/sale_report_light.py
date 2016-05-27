# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import osv
from openerp import pooler
from openerp.report import report_sxw



class sale_report_light(report_sxw.rml_parse):
    
      def __init__(self, cr, uid, name, context=None):
        super(sale_report_light, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'count_lines': self._count_lines,
            'get_order_line': self._get_order_line,
            'time': time,
            'last':self._last,
            'amount':self._amount,
            'carriage_returns':self._carriage_returns,
            'get_record':self._get_record,
            'get_num_pages':self._get_num_pages,
            'get_order_line_length':self._get_order_line_length,        
            'get_uom': self._get_uom, 
            'discount_presence': self._discount_presence,   
            'uom_presence': self._uom_presence,
        })
        self.context = context

      def _get_uom(self, uom_id):
        context = {'lang':'it_IT',}
        return self.pool.get('product.uom').browse(self.cr, self.uid, uom_id, context).name

      def _get_record(self, order_id):
        order_obj = pooler.get_pool(self.cr.dbname).get('sale.order')
        order_data = order_obj.browse(self.cr, self.uid, order_id)
        return order_data

      def _discount_presence(self, order_id):
          order = self._get_record(order_id)
          for line in order.order_line:
              if line.discount:
                  return True
          return False
      
      def _uom_presence(self,order_id):
          order = self._get_record(order_id)
          for line in order.order_line:
              if line.product_uom:
                  return True
          return False          

      def _count_lines(self, order_id):
        num_lines = 0
        order_obj = pooler.get_pool(self.cr.dbname).get('sale.order')
        order_data = order_obj.browse(self.cr, self.uid, order_id)
        if order_data and order_data.order_line:
            for _ in order_data.order_line:
                num_lines = num_lines +1
        return num_lines
    
      def _get_num_pages(self,order_id,limit_page,limit_page_last):
        res = 0
        lines = self._get_order_line(order_id,0,0)
        if lines and lines.ids:
            res = float(len(lines.ids))
            res = res/limit_page
            res = math.ceil(res)
            if len(lines.ids)%limit_page > limit_page_last:
                res = res + 1
        return int(res)

      def _get_order_line_length(self, order_id, limit_page, offset_page):
        res = 0
        lines = self._get_order_line(order_id, limit_page, offset_page)
        if lines and lines.ids:
            res = len(lines.ids)
        return res

    
      def _get_order_line(self, order_id, limit_page, offset_page):
        order_obj = pooler.get_pool(self.cr.dbname).get('sale.order')
        order_data = order_obj.browse(self.cr, self.uid, order_id)
        order_lines = []
        if order_data and order_data.order_line:
            hrs_list = []
            hrs = pooler.get_pool(self.cr.dbname).get('sale.order.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('order_id', '=', order_id), ],
                                  limit=limit_page,
                                  offset=offset_page)

            order_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return order_lines
    

      def _last(self,order_line,len):
          return order_line[len-1]
      
      def _amount(self,text):
              if text:
                 text.replace('-', '&#8209;')
              return text   
          
      def _carriage_returns(self, text):
              if text:
                 text.replace('\n', '<br />')
              return text
    

class report_saleorder_makeover(osv.AbstractModel):
    _name = 'report.report_qweb_omniapart.report_saleorder_light'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_omniapart.report_saleorder_light'
    _wrapped_report_class = sale_report_light
    
    