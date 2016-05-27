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

import time
from openerp.report import report_sxw
from openerp.osv import osv


class report_divisione_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_divisione_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_docs': self._get_docs,
            'get_sizes': self._get_sizes,
            'get_lines': self._get_lines,
        })
        self.context = context

    def _get_docs(self, ids):
        keys = {}
        for doc in ids:
            key = (doc.product_tmpl_id, doc.color, doc.location_id)
            if key not in keys:
                keys.setdefault(key, [])
            keys[key].append(doc.id)
        res = []
        for item in keys:
            res.append({'product_tmpl_id':item[0], 'color':item[1], 'location_id':item[2], 'docs':keys[item]})
        return res

    def _get_sizes(self, tmpl):
        res = []        
        for val in tmpl.attribute_line_ids:
            if val.attribute_id.position == 'column':
                for id in val.value_ids:
                    res.append(id)        
        return res

    def _get_lines(self, group):
        res = []
        f_tot = []      
        t_tot = {}
        
        sizes = self._get_sizes(group['product_tmpl_id'])
        
        product_ids = []
        for size in sizes:
            for product in group['product_tmpl_id'].product_variant_ids:
                if group['color'] in product.attribute_value_ids and size in product.attribute_value_ids:
                    product_ids.append(product.id)

        last_id = None
        if group['docs']:
            last_id = group['docs'][0]
        for id in group['docs']:      
            if id > last_id:
                last_id = id
        
        for id in product_ids:
          t_tot[id] = 0.0
        t_tot['total'] = 0.0
        t_tot['residual'] = 0.0
        t_tot['available'] = 0.0
        
        qry = ''
        for id in group['docs']:
            qry += str(id)+','
        qry_ids = qry[0:len(qry)-1]
        qry='SELECT DISTINCT o.id, o.stock_number_txt FROM stock_reservation_product AS r, sale_order AS o WHERE r.order_id = o.id AND difference != 0 AND r.reservation_id IN ('+qry_ids+') ORDER BY o.stock_number_txt' 
            
        self.cr.execute(qry,())
        qry_res = self.cr.fetchall()
        order_ids = []
        for item in qry_res:
            order_ids.append(item[0])
            
        pair = 0        
        for order_id in order_ids:
            order_obj = self.pool.get('sale.order').browse(self.cr, self.uid, order_id)
            tot = 0.0
            tmp = []
            if pair%2 == 0:
                tmp.append('#FFFFFF')
            else:
                tmp.append('CCCCCC')
            tmp.append(order_obj.name)
            sizes = []
            for id in product_ids:
                self.cr.execute('''
                    SELECT SUM(difference)
                    FROM stock_reservation_product
                    WHERE product_id = %s AND order_id = %s and reservation_id IN ('''+qry_ids+')'              
                ,(id, order_id))
                qry_res = self.cr.fetchone()
                if qry_res and qry_res[0]:
                    sizes.append(qry_res[0])
                    tot += qry_res[0]
                    t_tot[id] += qry_res[0]
                    t_tot['total'] += qry_res[0]
                else:
                    sizes.append(0.0)
            tmp.append(sizes)
            tmp.append(tot)
            tmp.append(order_obj.partner_id.name)
            tmp.append(order_obj.stock_number_txt)            
            res.append(tmp)
            pair += 1
            
        # AGGIUNGO I TOTALI EVASI
        tmp = []
        if pair%2 == 0:
            tmp.append('#FFFFFF')
        else:
            tmp.append('CCCCCC')
        tmp.append('')
        sizes = []        
        for id in product_ids:
            sizes.append(t_tot[id])
        tmp.append(sizes)
        tmp.append(t_tot['total'])
        tmp.append('')
        tmp.append('Totals:')
        res.append(tmp)
        
        # AGGIUNGO I TOTALI GIACENTI
        tmp = []
        if pair%2 == 0:
            tmp.append('#FFFFFF')
        else:
            tmp.append('CCCCCC')
        tmp.append('')
        sizes = []        
        for id in product_ids:
            self.cr.execute('''
                SELECT available_qty
                FROM stock_reservation_availability
                WHERE product_id = %s and reservation_id = %s'''              
            ,(id, last_id))
            qry_res = self.cr.fetchone()
            if qry_res and qry_res[0]:
                sizes.append(qry_res[0]+t_tot[id])
                t_tot['available'] = t_tot['available'] + qry_res[0] +t_tot[id]                
            else:
                sizes.append(0.0+t_tot[id])
                t_tot['available'] += t_tot[id]                
        tmp.append(sizes)
        tmp.append(t_tot['available'])
        tmp.append('')
        tmp.append('Available:')
        res.append(tmp)  
        # AGGIUNGO I TOTALI RESIDUI
        tmp = []
        if pair%2 == 0:
            tmp.append('#FFFFFF')
        else:
            tmp.append('CCCCCC')
        tmp.append('')
        sizes = []        
        for id in product_ids:
            self.cr.execute('''
                SELECT available_qty
                FROM stock_reservation_availability
                WHERE product_id = %s and reservation_id = %s'''              
            ,(id, last_id))
            qry_res = self.cr.fetchone()
            if qry_res and qry_res[0]:
                sizes.append(qry_res[0])
                t_tot['residual'] += qry_res[0]                 
            else:
                sizes.append(0.0)
        tmp.append(sizes)
        tmp.append(t_tot['residual'])
        tmp.append('')
        tmp.append('Residual:')
        res.append(tmp)               
        
        return res
    
class report_product_barcode(osv.AbstractModel):
    _name = 'report.report_qweb_montecristo.report_divisione'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_montecristo.report_divisione'
    _wrapped_report_class = report_divisione_parser
