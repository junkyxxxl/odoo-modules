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
from datetime import date, datetime


class report_stockpicking_cumulative_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_stockpicking_cumulative_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_docs': self._get_docs,
            'get_total_prices': self._get_total_prices,
            'total_quantities': self._total_quantities,
        })
        self.context = context

    def _get_total_prices(self, doc):
        res = [0,0,0]
        for move_line in doc['move_lines']:
            line = None
            if doc['picking_type_id'].code=='outgoing':
                if move_line.reserved_availability > 0 or move_line.state == 'done' :                    
                    if move_line.procurement_id and move_line.procurement_id.sale_line_id:
                        line = move_line.procurement_id.sale_line_id
                        if line.free not in ['gift', 'base_gift']:
                            original_tax_value = 0.0
                            if move_line.state == 'done':
                                original_untaxed_value = line.price_subtotal * (move_line.product_uom_qty / line.product_uom_qty)
                            else:
                                original_untaxed_value = line.price_subtotal * (move_line.reserved_availability / line.product_uom_qty)                                                                                         
                            for tax in line.tax_id:
                               original_tax_value += original_untaxed_value * tax.amount       
                                                
                            
                            
                            for discount in line.order_id.global_discount_lines:      
        
                               if discount.type=='fisso':
                                    perc = discount.value / original_untaxed_value                
                               else:
                                    perc = discount.value/100
                
                               sc = original_tax_value*perc 
                               original_tax_value -= sc
                               
                               sc1 = original_untaxed_value*perc
                               original_untaxed_value -= sc1
                        elif line.free == 'base_gift':
                           
                            original_untaxed_value = 0.0
                            original_tax_value = 0.0
                            for tax in line.tax_id:
                                if move_line.state == 'done':
                                    original_tax_value += (line.price_subtotal * (move_line.product_uom_qty / line.product_uom_qty)) * tax.amount                                   
                                else:
                                    original_tax_value += (line.price_subtotal * (move_line.reserved_availability / line.product_uom_qty)) * tax.amount   
                        else:
                            original_untaxed_value = 0.0
                            original_tax_value = 0.0
                           
                        res[0]+= original_untaxed_value
                        res[1]+= original_tax_value
                        res[2] = res[2] + original_untaxed_value + original_tax_value
                        
            elif doc['picking_type_id'].code == 'incoming':
                if move_line.procurement_id and move_line.procurement_id.purchase_line_id:
                    line = move_line.procurement_id.purchase_line_id
                elif move_line.purchase_line_id:
                    line = move_line.purchase_line_id              
                if line:
                    original_tax_value = 0.0
                    original_untaxed_value = line.price_subtotal * (move_line.product_uom_qty / line.product_qty)
                    for tax in line.taxes_id:
                       original_tax_value += original_untaxed_value * tax.amount       
                    res[0]+= original_untaxed_value
                    res[1]+= original_tax_value
                    res[2] = res[2] + original_untaxed_value + original_tax_value     
                else:
                    if move_line.procurement_id and move_line.procurement_id.sale_line_id: 
                        line = move_line.procurement_id.sale_line_id           
                        if line.free not in ['gift', 'base_gift']:
                            original_tax_value = 0.0
                            if move_line.state == 'done':
                                original_untaxed_value = line.price_subtotal * (move_line.product_uom_qty / line.product_uom_qty)
                            else:
                                original_untaxed_value = line.price_subtotal * (move_line.reserved_availability / line.product_uom_qty)                                                                                         
                            for tax in line.tax_id:
                               original_tax_value += original_untaxed_value * tax.amount       
                                                
                            
                            
                            for discount in line.order_id.global_discount_lines:      
        
                               if discount.type=='fisso':
                                    perc = discount.value / original_untaxed_value                
                               else:
                                    perc = discount.value/100
                
                               sc = original_tax_value*perc 
                               original_tax_value -= sc
                               
                               sc1 = original_untaxed_value*perc
                               original_untaxed_value -= sc1
                        elif line.free == 'base_gift':
                           
                            original_untaxed_value = 0.0
                            original_tax_value = 0.0
                            for tax in line.tax_id:
                                if move_line.state == 'done':
                                    original_tax_value += (line.price_subtotal * (move_line.product_uom_qty / line.product_uom_qty)) * tax.amount                                   
                                else:
                                    original_tax_value += (line.price_subtotal * (move_line.reserved_availability / line.product_uom_qty)) * tax.amount   
                        else:
                            original_untaxed_value = 0.0
                            original_tax_value = 0.0
                           
                        res[0]+= original_untaxed_value
                        res[1]+= original_tax_value
                        res[2] = res[2] + original_untaxed_value + original_tax_value                                                                 
        return res

    def _total_quantities(self, doc):
        totals = []
        for line in doc['move_lines']:
            if line.product_uom:
                check = True
                for total in totals:
                    if line.product_uom.id == total[0]:
                        if doc['picking_type_id'].code == 'outgoing':
                            if line.state == 'done':
                                total[2] += line.product_uom_qty
                            else:
                                total[2] += line.reserved_availability
                            check = False
                            break
                        elif doc['picking_type_id'].code == 'incoming':
                            total[2] += line.product_uom_qty
                            check = False
                            break                            
                if check:
                    tmp = []
                    tmp.append(line.product_uom.id)
                    tmp.append(line.product_uom.name)
                    if doc['picking_type_id'].code == 'outgoing':
                        if line.state == 'done':
                            tmp.append(line.product_uom_qty)
                        else:
                            tmp.append(line.reserved_availability)           
                    else:
                        tmp.append(line.product_uom_qty)   
                    totals.append(tmp)
        return totals

    
    def _get_docs(self, ids):
        keys = {}
        moves = {}
        ops = {}
        for doc in ids:
            key = (doc.picking_type_id, doc.partner_id, doc.origin)
            if key not in keys:
                keys.setdefault(key, [])
                moves.setdefault(key, [])
                ops.setdefault(key, [])
            keys[key].append(doc.id)
            for id in doc.move_lines:
                moves[key].append(id)
            for id in doc.pack_operation_ids:
                ops[key].append(id)           
            
        res = []
        for item in keys:
            res.append({'picking_type_id':item[0], 'partner_id':item[1], 'origin':item[2], 'move_lines': moves[item], 'pack_operation_ids': ops[item]})
        return res
    
class report_stockpicking_cumulative(osv.AbstractModel):
    _name = 'report.report_qweb_montecristo.report_stockpicking_cumulative'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_montecristo.report_stockpicking_cumulative'
    _wrapped_report_class = report_stockpicking_cumulative_parser
