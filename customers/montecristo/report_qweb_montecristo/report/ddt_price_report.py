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


class report_ddt_price_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_ddt_price_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_templates': self._get_templates,
            'get_colors': self._get_colors,
            'get_sizes': self._get_sizes,
            'get_line': self._get_line,
            'get_records': self._get_records,
            'get_num_pages': self._get_num_pages,
            'get_record_slice': self._get_record_slice,
            'get_move_line': self._get_move_line,
            'get_tot_pcs': self._get_tot_pcs,
            'get_shipping_costs': self._get_shipping_costs,
            'get_customer_code': self._get_customer_code,
            'get_abi': self._get_abi,
            'get_cab': self._get_cab,
            'get_iban': self._get_iban,
            'get_totals': self._get_totals,
        })
        self.context = context

    def _get_customer_code(self, partner):
        leaf_account = partner.property_account_receivable
        if leaf_account:
            master_account = leaf_account.parent_id
        else:
            return 'N/N'

        customer_code = leaf_account.code
        if master_account:
            customer_code = customer_code.replace(master_account.code, '')

        return customer_code

    def _get_abi(self, doc):
        if doc.partner_id.bank_ids:
            if len(doc.partner_id.bank_ids[0].acc_number) == 27:
                return doc.partner_id.bank_ids[0].acc_number[5:10]
        return ''

    def _get_cab(self, doc):
        if doc.partner_id.bank_ids:
            if len(doc.partner_id.bank_ids[0].acc_number) == 27:
                return doc.partner_id.bank_ids[0].acc_number[10:15]
        return ''

    def _get_iban(self, doc):
        if doc.partner_id.bank_ids:
            return doc.partner_id.bank_ids[0].acc_number
        return ''

    def _get_tot_pcs(self, doc):
        res = 0
        for line in doc.ddt_lines:
            res += line.product_uom_qty        
        return int(res)

    def _get_num_pages(self, doc, limit_page):
        res = len(self._get_records(doc))
        res = math.ceil(float(res)/limit_page)
        res = int(res)
        return res

    def _get_records(self, doc):
        res = []
        for template_id in self._get_templates(doc, True):
            if not template_id.is_shipping:
                sizes = self._get_sizes(template_id.id)

                tmp = []
                tmp.append(True)
                tmp.append('')
                tmp.append('')
                tmp.append('')
                for i in range(0, 10):
                    if len(sizes) >= i+1:
                        tmp.append(sizes[i].name)
                    else:
                        tmp.append('')
                tmp.append('')
                res.append(tmp)

                for color in self._get_colors(doc, template_id.id):
                    tmp = []
                    total = 0
                    tmp.append(False)
                    tmp.append(template_id.tmpl_default_code)
                    tmp.append(color.name)
                    tmp.append(template_id.name)
                    for i in range(0, 10):
                        if len(sizes) >= i+1:
                            inv_line = self._get_line(doc, template_id, color, sizes[i])
                            if inv_line:
                                tmp.append(int(inv_line))
                                total += int(inv_line)
                            else:
                                tmp.append('')
                        else:
                            tmp.append('')
                    tmp.append(total)
                    res.append(tmp)

        #ELABORAZIONE DEI PRODOTTI NON A 2 DIMENSIONI

        if len(self._get_templates(doc, False)) > 0:
            tmp = []
            tmp.append(False)
            for i in range(1,19):
                tmp.append('') 
            res.append(tmp)                      
        
        for line_id in self._get_templates(doc, False):
            if not line_id.product_id.is_shipping:        
                tmp = []
                tmp.append(False)
                tmp.append(line_id.product_id.tmpl_default_code)
                tmp.append('')
                tmp.append(line_id.product_id.name)
                for i in range(0,10):
                        tmp.append('')
                tmp.append(int(line_id.product_uom_qty))
                     
                res.append(tmp)     
                    
        return res

    def _get_totals(self, doc):
        res = [0,0,0]
        for ddt_line in doc.ddt_lines:
            if ddt_line.procurement_id and ddt_line.procurement_id.sale_line_id:
                line = ddt_line.procurement_id.sale_line_id
                if line.free not in ['gift', 'base_gift']:
                    original_tax_value = 0.0
                    for tax in line.tax_id:
                       original_tax_value += (line.price_subtotal * (ddt_line.product_uom_qty / line.product_uom_qty)) *  tax.amount       
                                        
                    original_untaxed_value = line.price_subtotal * (ddt_line.product_uom_qty / line.product_uom_qty)
                    
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
                        original_tax_value += (line.price_subtotal * (ddt_line.product_uom_qty / line.product_uom_qty)) * tax.amount   
                else:
                    original_untaxed_value = 0.0
                    original_tax_value = 0.0
                   
                res[0]+= original_untaxed_value
                res[1]+= original_tax_value
                res[2] = res[2] + original_untaxed_value + original_tax_value
                                             
        return res

    def _get_record_slice(self, records, offset, limit):
        if limit > len(records) + 1:
            for i in range(limit - len(records)+1):
                tmp = []
                tmp.append(False)
                for j in range(1, 19):
                    tmp.append('')
                records.append(tmp)
        res = records[offset:limit]
        return res

    def _get_templates(self, doc, proper=True):
        res = []
        for line in doc.ddt_lines:
            if line.product_id:
                if proper and line.product_id.product_tmpl_id.attribute_line_ids and len(line.product_id.product_tmpl_id.attribute_line_ids.ids) == 2:
                    res.append(line.product_id.product_tmpl_id)
                if not proper and (not line.product_id.product_tmpl_id.attribute_line_ids or  len(line.product_id.product_tmpl_id.attribute_line_ids.ids) != 2):
                    res.append(line)
        return list(set(res))

    def _get_colors(self, doc, template):
        res = []
        for line in doc.ddt_lines:
            if line.product_id.product_tmpl_id.id == template:
                for value in line.product_id.attribute_value_ids:
                    if value.attribute_id.position == 'row' and value not in res:
                        res.append(value)
                        break
        return res

    def _get_sizes(self, template):
        res = []
        tmpl_obj = self.pool.get('product.template')
        for attribute in tmpl_obj.browse(self.cr, self.uid, template).attribute_line_ids:
            if attribute.attribute_id.position == 'column':
                for size in attribute.value_ids:
                    res.append(size)
                break
        return res

    def _get_line(self, doc, template, color, size):
        res = 0.0
        for line in doc.ddt_lines:
            if line.product_id.product_tmpl_id.id == template.id and (line.product_id.attribute_value_ids[0].id == color.id or line.product_id.attribute_value_ids[1].id == color.id) and (line.product_id.attribute_value_ids[1].id == size.id or line.product_id.attribute_value_ids[0].id == size.id):
                res += line.product_uom_qty                
        return res

    def _get_move_line(self, move_id):
        hrs = self.pool.get('account.move.line')
        hrs_list = hrs.search(self.cr, self.uid,
                              [('move_id', '=', move_id),
                               ('date_maturity', '!=', False), ],
                              order='date_maturity')
        move_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return move_lines

    def _get_shipping_costs(self, doc):
        res = 0.0
        for line in doc.ddt_lines:
            if line.product_id.is_shipping:
                res += line.price_unit * line.product_uom_qty
        return res


class report_ddt_price(osv.AbstractModel):
    _name = 'report.report_qweb_montecristo.report_ddt_price'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_montecristo.report_ddt_price'
    _wrapped_report_class = report_ddt_price_parser
