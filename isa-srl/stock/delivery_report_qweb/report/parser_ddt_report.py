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

import math
import time
from openerp.osv import osv
from openerp.report import report_sxw


class ddt_report(report_sxw.rml_parse):


     def __init__(self, cr, uid, name, context=None):
        super(ddt_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'time': time,
            'get_qty':self._get_qty,
            'get_weight':self._get_weight,
            'get_order_ddt_line': self._get_order_ddt_line,
            'count_lines': self._count_lines,
            'getDict':self._getDict,
            'carriage_returns':self._carriage_returns,
            'get_record':self._get_record,
            'get_num_pages':self._get_num_pages,
            'get_order_ddt_line_length':self._get_order_ddt_line_length,            
        })
        self.context = context

     def _get_record(self, pick_id):
        pick_obj = self.pool.get('stock.picking.ddt')
        pick_data = pick_obj.browse(self.cr, self.uid, pick_id)
        return pick_data

     def _get_num_pages(self,pick_id,limit_page,limit_page_last):
        res = 0
        lines = self._get_order_ddt_line(pick_id,0,0)
        if lines and lines.ids:
            res = float(len(lines.ids))
            res = res/limit_page
            res = math.ceil(res)
            if len(lines.ids)%limit_page > limit_page_last:
                res = res + 1
        return int(res)

     def _get_order_ddt_line_length(self, pick_id, limit_page, offset_page):
        res = 0
        lines = self._get_order_ddt_line(pick_id, limit_page, offset_page)
        if lines and lines.ids:
            res = len(lines.ids)
        return res


     def _get_order_ddt_line(self, pick_id, limit_page, offset_page):
        pick_obj = self.pool.get('stock.picking.ddt')
        pick_data = pick_obj.browse(self.cr, self.uid, pick_id)
        ddt_lines = []
        if pick_data and pick_data.move_lines:
            hrs_list = []
            hrs = self.pool.get('stock.move')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('picking_id', '=', pick_data.picking_id.id), ],
                                  limit=limit_page,
                                  offset=offset_page)

            ddt_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return ddt_lines

     def _count_lines(self, pick_id):
        num_lines = 0
        pick_obj = self.pool.get('stock.picking.ddt')
        pick_data = pick_obj.browse(self.cr, self.uid, pick_id)
        if pick_data and pick_data.move_lines:
            for _ in pick_data.move_lines:
                num_lines = num_lines +1
        return num_lines

     def _get_qty(self, pick_id):
        pick_obj = self.pool.get('stock.picking.ddt')
        pick_data = pick_obj.browse(self.cr, self.uid, pick_id)
        t_qty_count = 0
        if pick_data and pick_data.move_lines:
            hrs_list = []
            hrs = self.pool.get('stock.move')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('picking_id', '=', pick_data.picking_id.id), ])
            for move_line in hrs.browse(self.cr, self.uid, hrs_list):
                t_qty_count = t_qty_count + move_line.product_qty
        return t_qty_count

     def _get_weight(self, pick_id):
        t_weight_count = 0
        pick_obj = self.pool.get('stock.picking.ddt')
        pick_data = pick_obj.browse(self.cr, self.uid, pick_id)
        if pick_data and pick_data.move_lines:
            hrs_list = []
            hrs = self.pool.get('stock.move')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('picking_id', '=', pick_data.picking_id.id), ])
            for move_line in hrs.browse(self.cr, self.uid, hrs_list):
                if move_line.product_id and move_line.product_id.weight:
                    t_weight_count = t_weight_count + move_line.product_qty * move_line.product_id.weight
        return t_weight_count

     def _getDict(self,obj):
          t_dict = dict([('sender', 'Mittente'), ('receiver', 'Destinatario'), ('carrier', 'Vettore')])
          d_method = str(t_dict[obj.delivery_methods])   
          
          return d_method
      
     def _carriage_returns(self, text):
          if text:
             text.replace('\n', '<br />')
             return text 

class report_ddt_makeover(osv.AbstractModel):
    _name = 'report.delivery_report_qweb.report_ddt_makeover'
    _inherit = 'report.abstract_report'
    _template = 'delivery_report_qweb.report_ddt_makeover'
    _wrapped_report_class = ddt_report
    

