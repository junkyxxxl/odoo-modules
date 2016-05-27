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


class report_invoice_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_invoice_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_templates': self._get_templates,
            'get_lines': self._get_lines,
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
            'get_discount_line': self._get_discount_line,
        })
        self.context = context

    def _get_discount_line(self,doc):
        res = ''
        if  doc.global_discount_lines:
            for line in doc.global_discount_lines:
                if res:
                    res = res + ' + '
                res = res+str(line.value).replace('.',',')
        return res

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
        if doc.partner_bank_id:
            if len(doc.partner_bank_id.acc_number) == 27:
                return doc.partner_bank_id.acc_number[5:10]
        return ''

    def _get_cab(self, doc):
        if doc.partner_bank_id:
            if len(doc.partner_bank_id.acc_number) == 27:
                return doc.partner_bank_id.acc_number[10:15]
        return ''

    def _get_iban(self, doc):
        if doc.partner_bank_id:
            return doc.partner_bank_id.acc_number
        return ''

    def _get_tot_pcs(self, doc):
        res = 0
        for line in self._get_lines(doc):
            res += line.quantity
        return int(res)

    def _get_num_pages(self, doc, limit_page):
        res = len(self._get_records(doc))
        res = math.ceil(float(res)/limit_page)
        res = int(res)
        if res < 1:
            res = 1
        return res

    def _get_ddt_records(self, doc, ddt):
        res = []
        ddt_obj = self.pool.get('stock.ddt')
        o_print = False
        o_tmp = []
        o_tmp.append(0)
        o_tmp.append('')
        o_tmp.append('')
        ddt_data = ddt_obj.browse(self.cr, self.uid, ddt)
        ddt_print = ddt_data.name + ' - Data: '
        o_tmp.append([ddt_print,ddt_data.date])
        for j in range(4, 19):
            o_tmp.append('')
        #res.append(o_tmp)

        for template_id in self._get_templates(doc, ddt, 0, True, 'DDT'):
            if not template_id.is_shipping:
                sizes = self._get_sizes(template_id.id)

                t_print = False
                t_tmp = []
                t_tmp.append(1)
                t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                for i in range(0, 10):
                    if len(sizes) >= i+1:
                        t_tmp.append(sizes[i].name)
                    else:
                        t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                #res.append(t_tmp)

            for price in self._get_prices(doc, template_id.id, ddt, 0, 'DDT'):
                for discount in self._get_discount(doc, template_id.id, price, ddt, 0, 'DDT'):
                    for tax in self._get_tax(doc, template_id.id, price, discount, ddt, 0, 'DDT'):
                        for free in self._get_free(doc,template_id.id,price,discount,tax, ddt, 0, 'DDT'):                        
                            for color in self._get_colors(doc, template_id.id, price, discount, tax, free, ddt, 0, 'DDT'):
                                tmp = []
                                total = 0
                                tmp.append(2)
                                tmp.append(template_id.tmpl_default_code)
                                tmp.append(color.name)
                                tmp.append(template_id.name)
                                for i in range(0, 10):
                                    if len(sizes) >= i+1:
                                        inv_line = self._get_line(doc, template_id, color, sizes[i], price, discount, tax, free, ddt, 0, 'DDT')
                                        if inv_line:
                                            t_qty = 0
                                            for l in inv_line:
                                                t_qty += l.quantity
                                            if t_qty == 0:
                                                tmp.append('')
                                            else:                                                     
                                                tmp.append(int(t_qty))
                                            total += int(t_qty)                                         
                                        else:
                                            tmp.append('')
                                    else:
                                        tmp.append('')
                                tmp.append(total)
                                if discount:
                                    tmp.append(str(discount)+'%')
                                else:
                                    tmp.append('')
                                tmp.append(price)
                                tmp.append(total*round(price-(price*discount)/100,2))
                                if tax:
                                    tmp.append(tax[0].tax_code_id.code)
                                else:
                                    tmp.append('')
                                if total:
                                    if not o_print and o_tmp:
                                        o_print = True
                                        res.append(o_tmp)
                                    if not t_print and t_tmp:
                                        t_print = True
                                        res.append(t_tmp) 
                                    res.append(tmp)    
                                
                                if free == 1 and total:
                                    tmp = []
                                    tmp.append(2)
                                    tmp.append('')
                                    tmp.append('')
                                    tmp.append('Omaggio ai sensi ex art.15 DPR 633/72')
                                    for i in range(4,19):
                                        tmp.append('')
                                    res.append(tmp)
                              

            #ELABORAZIONE DEI PRODOTTI NON A 2 DIMENSIONI
    
            if len(self._get_templates(doc, ddt, 0, False, 'DDT')) > 0:
                tmp = []
                tmp.append(4)
                for i in range(1,19):
                    tmp.append('') 
                res.append(tmp)                      
            
            for line_id in self._get_templates(doc, ddt, 0, False, 'DDT'):
                if not line_id.product_id.is_shipping:        
                    tmp = []
                    tmp.append(4)
                    tmp.append(line_id.product_id.tmpl_default_code)
                    tmp.append('')
                    tmp.append(line_id.product_id.name)
                    for i in range(0,10):
                            tmp.append('')
                    tmp.append(int(line_id.quantity))
                    if line_id.discount:
                        tmp.append(str(line_id.discount)+'%')
                    else:
                        tmp.append('')
                    tmp.append(line_id.price_unit)
                    tmp.append(line_id.price_subtotal)
                    
                    if line_id.invoice_line_tax_id:
                        tmp.append(line_id.invoice_line_tax_id[0].tax_code_id.code)
                    else:
                        tmp.append('')        
                    res.append(tmp)  
        return res

    def _get_order_records(self, doc, order):
        res = []
        o_print = False
        o_tmp = False
        
        pick_obj = self.pool.get('stock.picking')
        if order and doc.type != 'out_refund':
            pick_data = pick_obj.browse(self.cr, self.uid, order)
            if pick_data.origin:
                o_print = False            
                o_tmp = []
                o_tmp.append(0)
                o_tmp.append('')
                o_tmp.append('')
                pick_data = pick_obj.browse(self.cr, self.uid, order)
                pick_print = ['Rif. Ordine: ' + pick_data.origin,False]
                o_tmp.append(pick_print)
                for j in range(4, 19):
                    o_tmp.append('')
                #res.append(o_tmp)
    
        for template_id in self._get_templates(doc, 0, order, True, 'ORDER'):
            t_print = False
            t_tmp = False
            
            if not template_id.is_shipping:
                sizes = self._get_sizes(template_id.id)

                t_print = False    
                t_tmp = []
                t_tmp.append(1)
                t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                for i in range(0, 10):
                    if len(sizes) >= i+1:
                        t_tmp.append(sizes[i].name)
                    else:
                        t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                t_tmp.append('')
                #res.append(t_tmp)
    
            for price in self._get_prices(doc, template_id.id, 0, order, 'ORDER'):
                for discount in self._get_discount(doc, template_id.id, price, 0, order, 'ORDER'):
                    for tax in self._get_tax(doc, template_id.id, price, discount, 0, order, 'ORDER'):
                        for free in self._get_free(doc, template_id.id, price, discount, tax, 0, order, 'ORDER'):
                            for color in self._get_colors(doc, template_id.id, price, discount, tax, free, 0, order, 'ORDER'):
                                tmp = []
                                total = 0
                                tmp.append(2)
                                tmp.append(template_id.tmpl_default_code)
                                tmp.append(color.name)
                                tmp.append(template_id.name)
                                for i in range(0, 10):
                                    if len(sizes) >= i+1:
                                        inv_line = self._get_line(doc, template_id, color, sizes[i], price, discount, tax, free, 0, order, 'ORDER')
                                        if inv_line:
                                            t_qty = 0
                                            for l in inv_line:
                                                t_qty += l.quantity
                                            if t_qty == 0:
                                                tmp.append('')
                                            else:                                                     
                                                tmp.append(int(t_qty))
                                            total += int(t_qty)                                         
                                        else:
                                            tmp.append('')
                                    else:
                                        tmp.append('')
                                tmp.append(total)
                                if discount:
                                    tmp.append(str(discount)+'%')
                                else:
                                    tmp.append('')
                                tmp.append(price)
                                tmp.append(total*price-(total*price)*discount/100)
                                if tax:
                                    tmp.append(tax[0].tax_code_id.code)
                                else:
                                    tmp.append('')
                                if total:
                                    if not o_print and o_tmp:
                                        o_print = True
                                        res.append(o_tmp)                                    
                                    if not t_print and t_tmp:
                                        t_print = True
                                        res.append(t_tmp) 
                                    res.append(tmp) 
    
                                if t_print and free == 1:
                                    tmp = []
                                    tmp.append(2)
                                    tmp.append('')
                                    tmp.append('')
                                    tmp.append('Omaggio ai sensi ex art.15 DPR 633/72')
                                    for i in range(4,19):
                                        tmp.append('') 
                                    res.append(tmp)
    
            #ELABORAZIONE DEI PRODOTTI NON A 2 DIMENSIONI
    
            if len(self._get_templates(doc, 0, order, False, 'ORDER')) > 0:
                tmp = []
                tmp.append(4)
                for i in range(1,19):
                    tmp.append('') 
                res.append(tmp)                      
            
            for line_id in self._get_templates(doc, 0, order, False, 'ORDER'):
                if not line_id.product_id.is_shipping:        
                    tmp = []
                    tmp.append(4)
                    tmp.append(line_id.product_id.tmpl_default_code)
                    tmp.append('')
                    tmp.append(line_id.product_id.name)
                    for i in range(0,10):
                            tmp.append('')
                    tmp.append(int(line_id.quantity))
                    if line_id.discount:
                        tmp.append(str(line_id.discount)+'%')
                    else:
                        tmp.append('')
                    tmp.append(line_id.price_unit)
                    tmp.append(line_id.price_subtotal)
                    
                    if line_id.invoice_line_tax_id:
                        tmp.append(line_id.invoice_line_tax_id[0].tax_code_id.code)
                    else:
                        tmp.append('')        
                    res.append(tmp)  
        return res

    def _get_records(self, doc):
        res = []
        ddt_origins = self._get_ddts(doc)
        ddt_obj = self.pool.get('stock.ddt')
        for ddt in ddt_origins:
            if ddt:
                ddt_res = self._get_ddt_records(doc, ddt)
                for x in ddt_res:
                    res.append(x)
            else:
                order_origins = self._get_orders(doc)
                for order in order_origins:
                    order_res = self._get_order_records(doc, order)
                    for x in order_res:
                        res.append(x)
            
        #ELABORAZIONE DELLE RIGHE DESCRITTIVE CON IMPORTO   
        for line in self._get_lines(doc):
            if not line.product_id and line.price_unit:
                tmp = []
                tmp.append(4)
                for j in range(1,19):  
                    tmp.append('')
                res.append(tmp)
                
                tmp = []
                tmp.append(1)
                tmp.append('')
                tmp.append('')
                tmp.append(line.name)
                for i in range(0,10):
                    tmp.append('')
                tmp.append(int(line.quantity))
                if line.discount:
                    tmp.append(str(line.discount)+'%')
                else:
                    tmp.append('')
                tmp.append(line.price_unit)
                tmp.append(line.price_subtotal)
                if line.invoice_line_tax_id:
                    tmp.append(line.invoice_line_tax_id[0].tax_code_id.code)
                else:
                    tmp.append('')    
                res.append(tmp)  
                
        #ELABORAZIONE DELLE RIGHE PURAMENTE DESCRITTIVE
        for line in self._get_lines(doc):
            if not line.product_id and not line.price_unit:
                tmp = []
                tmp.append(5)
                tmp.append(line.name)
                for i in range(2,19):
                    tmp.append('') 
                res.append(tmp)  
                                
        return res

    def _get_record_slice(self, records, offset, limit):
        if limit > len(records) + 1:
            for i in range(limit - len(records)+1):
                tmp = []
                tmp.append(3)
                for j in range(1, 19):
                    tmp.append('')
                records.append(tmp)
        res = records[offset:limit]
        
        for i in range(len(res)):
            if res[i][0] == 5 and res[len(res)-1][0] == 3:
                res.append(res[i])
                del res[i]
                i = i - 1        

        return res

    def _get_lines(self, doc):
        invoice_obj = self.pool.get('account.invoice')
        return invoice_obj.browse(self.cr, self.uid, doc.id).invoice_line

    def _get_templates(self, doc, ddt_origin=0, order_origin=0, proper = True, ref = 'DDT'):
        res = []
        for line in self._get_lines(doc):
            if (line.document_reference_id.ddt_id.id == ddt_origin and ref == 'DDT') or (line.document_reference_id.id == order_origin and ref == 'ORDER'):
                if line.product_id:
                    if proper and line.product_id.product_tmpl_id.attribute_line_ids and len(line.product_id.product_tmpl_id.attribute_line_ids.ids) == 2:
                        res.append(line.product_id.product_tmpl_id)
                    if not proper and (not line.product_id.product_tmpl_id.attribute_line_ids or  len(line.product_id.product_tmpl_id.attribute_line_ids.ids) != 2):
                        res.append(line)
        return list(set(res))

    def _get_orders(self, doc):
        res = []
        res.append(0)
        for line in self._get_lines(doc):
            if line.document_reference_id:
                if not line.document_reference_id.ddt_id and line.origin:
                    res.append(line.document_reference_id.id)
        return list(set(res))
    
    def _get_ddts(self, doc):
        res = []
        res.append(0)
        for line in self._get_lines(doc):
            if line.document_reference_id:
                if line.document_reference_id.ddt_id:
                    res.append(line.document_reference_id.ddt_id.id)
        return list(set(res))

    def _get_prices(self, doc, template, ddt_origin=0, order_origin=0, ref = 'DDT'):
        res = []
        for line in self._get_lines(doc):
            if ((line.document_reference_id.ddt_id.id == ddt_origin and ref == 'DDT') or (line.document_reference_id.id == order_origin and ref == 'ORDER')) and line.product_id.product_tmpl_id.id == template:
                price = line.price_unit
                if price not in res:
                    res.append(price)
        return res

    def _get_discount(self, doc, template, price, ddt_origin=0, order_origin=0, ref = 'DDT'):
        res = []
        for line in self._get_lines(doc):
            if ((line.document_reference_id.ddt_id.id == ddt_origin and ref == 'DDT') or (line.document_reference_id.id == order_origin and ref == 'ORDER')) and line.product_id.product_tmpl_id.id == template and line.price_unit == price:
                discount = line.discount
                if discount not in res:
                    res.append(discount)
        return res

    def _get_tax(self, doc, template, price, discount, ddt_origin=0, order_origin=0, ref = 'DDT'):
        res = []
        for line in self._get_lines(doc):
            if ((line.document_reference_id.ddt_id.id == ddt_origin and ref == 'DDT') or (line.document_reference_id.id == order_origin and ref == 'ORDER')) and line.product_id.product_tmpl_id.id == template and line.price_unit == price and line.discount == discount:
                tax = line.invoice_line_tax_id
                if tax not in res:
                    res.append(tax)
        return res

    def _get_free(self, doc, template, price, discount, tax, ddt_origin=0, order_origin=0, ref = 'DDT'):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template and line.price_unit == price and line.discount == discount:
                if (line.document_reference_id.ddt_id.id == ddt_origin and ref == 'DDT') or (line.document_reference_id.id == order_origin and ref == 'ORDER'):                
                    if line.free in ['gift','base_gift']:
                        free = 1
                    else:
                        free = 0
                    if free not in res:
                        res.append(free)
        return res

    def _get_colors(self, doc, template, price, discount, tax, free, ddt_origin=0, order_origin=0, ref='DDT'):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template and line.price_unit == price and line.discount == discount and ((line.free and free) or (not line.free and not free)):
                if (line.document_reference_id.ddt_id.id == ddt_origin and ref == 'DDT') or (line.document_reference_id.id == order_origin and ref == 'ORDER'):
                    for value in line.product_id.attribute_value_ids:
                        if value.attribute_id.position == 'row' and value not in res:
                            res.append(value)
                            break
        return res

    def _get_sizes(self, template):
        res = []
        tmpl_obj = self.pool.get('product.template')
        for attribute in tmpl_obj.browse(self.cr, self.uid,template).attribute_line_ids:
            if attribute.attribute_id.position == 'column':
                for size in attribute.value_ids:
                    res.append(size)
                break
        return res

    def _get_line(self, doc, template, color, size, price, discount, tax, free, ddt_origin=0, order_origin=0, ref = 'DDT'):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template.id and (line.product_id.attribute_value_ids[0].id == color.id or line.product_id.attribute_value_ids[1].id == color.id) and (line.product_id.attribute_value_ids[1].id == size.id or line.product_id.attribute_value_ids[0].id == size.id) and line.price_unit == price and line.discount == discount and line.invoice_line_tax_id == tax and ((line.free and free) or (not line.free and not free)):
                if (line.document_reference_id.ddt_id.id == ddt_origin and ref == 'DDT') or (line.document_reference_id.id == order_origin and ref == 'ORDER'):
                    res.append(line)
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
        for line in self._get_lines(doc):
            if line.product_id.is_shipping:
                res += line.price_unit * line.quantity
        return res


class report_product_barcode(osv.AbstractModel):
    _name = 'report.report_qweb_montecristo.report_invoice'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_montecristo.report_invoice'
    _wrapped_report_class = report_invoice_parser
