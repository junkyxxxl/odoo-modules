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


class report_purchase_order_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_purchase_order_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_templates': self._get_templates,
            'get_lines': self._get_lines,
            'get_colors':self._get_colors,
            'get_sizes':self._get_sizes,
            'get_line':self._get_line,
            'get_records':self._get_records,
            'get_num_pages':self._get_num_pages,
            'get_record_slice':self._get_record_slice,
            'get_move_line': self._get_move_line,
            'get_tot_pcs': self._get_tot_pcs,
            'get_customer_code': self._get_customer_code,
            'get_abi': self._get_abi,
            'get_cab': self._get_cab,
            'get_iban': self._get_iban,
            'format_delivery_date': self._format_delivery_date,
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
            customer_code = customer_code.replace(master_account.code,'')
        
        return customer_code

    def _format_delivery_date(self,date):
        return datetime.strptime(date, '%Y-%m-%d').strftime('%b').upper() + ' ' + time.strftime('%Y')

    def _get_abi(self,doc):
        if  doc.partner_id.bank_ids:
            if len(doc.partner_id.bank_ids[0].acc_number) == 27:
                return doc.partner_id.bank_ids[0].acc_number[5:10]
        return ''

    def _get_cab(self,doc):
        if  doc.partner_id.bank_ids:
            if len(doc.partner_id.bank_ids[0].acc_number) == 27:            
                return doc.partner_id.bank_ids[0].acc_number[10:15]
        return ''

    def _get_iban(self,doc):
        if  doc.partner_id.bank_ids:
            return doc.partner_id.bank_ids[0].acc_number
        return ''        

    def _get_tot_pcs(self,doc):
        res = 0
        for line in self._get_lines(doc):
            if line.product_id:
                res+= line.product_qty
        return int(res)    

    def _get_num_pages(self,doc,limit_page):
        res = 0.0
        for template_id in self._get_templates(doc):
            if not template_id.is_shipping:            
                res = res + 1
                for price in self._get_prices(doc, template_id.id):
                    for tax in self._get_tax(doc,template_id.id,price):
                        for color in self._get_colors(doc,template_id.id, price,tax):    
                            res = res + 1

        if len(self._get_templates(doc, False)) > 0:
            res = res + 1
        
        for line_id in self._get_templates(doc, False):
            if not line_id.product_id.is_shipping:            
                res = res + 1       
        
        for line in self._get_lines(doc):
            if not line.product_id and line.price_unit:
                res = res + 2
            if not line.product_id and not line.price_unit:
                res = res + 1                                
                                
        res = math.ceil(res/limit_page)
        return int(res)
        
    def _get_records(self,doc):
        res = []
        #ELABORAZIONE DEI PRODOTTI A 2 DIMENSIONI
        #PRENDO I TEMPLATE
        for template_id in self._get_templates(doc, True):
            if not template_id.is_shipping:
                sizes = self._get_sizes(template_id.id)
                
                tmp = []
                tmp.append(0)
                tmp.append('')
                tmp.append('')
                tmp.append('')
                for i in range(0,10):
                    if len(sizes)>=i+1:
                        tmp.append(sizes[i].name)
                    else:
                        tmp.append('')
                tmp.append('')
                tmp.append('')
                tmp.append('')
                tmp.append('')
                tmp.append('')        
                res.append(tmp)        
                
                #PRENDO I PREZZI
                for price in self._get_prices(doc,template_id.id):
                    #PRENDO LA TASSA
                    for tax in self._get_tax(doc,template_id.id,price):                       
                        #PRENDO I COLORI                
                        for color in self._get_colors(doc,template_id.id,price,tax):    
                            tmp = []
                            total = 0
                            tmp.append(1)
                            tmp.append(template_id.tmpl_default_code)
                            tmp.append(color.name)
                            tmp.append(template_id.name)
                            #VALORIZZO LE TAGLIE
                            for i in range(0,10):
                                if len(sizes)>=i+1:
                                    order_line = self._get_line(doc,template_id,color,sizes[i],price,tax)
                                    if order_line:
                                        tmp.append(int(order_line.product_qty))
                                        total += int(order_line.product_qty)
                                    else:
                                        tmp.append('')
                                else:
                                    tmp.append('')
                            tmp.append(total)
                            tmp.append('')
                            tmp.append(price)
                            tmp.append(total*price)

                            if tax:
                                tmp.append(tax[0].tax_code_id.code)
                            else:
                                tmp.append('')
                            res.append(tmp)

        #ELABORAZIONE DEI PRODOTTI NON A 2 DIMENSIONI

        if len(self._get_templates(doc, False)) > 0:
            tmp = []
            tmp.append(4)
            for i in range(1,19):
                tmp.append('') 
            res.append(tmp)                      
        
        for line_id in self._get_templates(doc, False):
            if not line_id.product_id.is_shipping:        
                tmp = []
                tmp.append(4)
                tmp.append(line_id.product_id.tmpl_default_code)
                tmp.append('')
                tmp.append(line_id.product_id.name)
                for i in range(0,10):
                        tmp.append('')
                tmp.append(int(line_id.product_qty))
                tmp.append('')
                tmp.append(line_id.price_unit)
                tmp.append(line_id.price_subtotal)
                
                if line_id.taxes_id:
                    tmp.append(line_id.taxes_id[0].tax_code_id.code)
                else:
                    tmp.append('')        
                res.append(tmp)                                     

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
                tmp.append(int(line.product_qty))
                tmp.append('')
                tmp.append(line.price_unit)
                tmp.append(line.price_subtotal)
                if line.taxes_id:
                    tmp.append(line.taxes_id[0].tax_code_id.code)
                else:
                    tmp.append('')    
                res.append(tmp)  

        #ELABORAZIONE DELLE RIGHE PURAMENTE DESCRITTIVE
        for line in self._get_lines(doc):
            if not line.product_id and not line.price_unit:
                tmp = []
                tmp.append(2)
                tmp.append(line.name)
                for i in range(2,19):
                    tmp.append('') 
                res.append(tmp)  
                                                                    
        return res

    def _get_record_slice(self,records,offset,limit):
        if limit>len(records)+1:
            for i in range(limit - len(records)+1):
                tmp = []
                tmp.append(3)
                for j in range(1,19):  
                    tmp.append('')
                records.append(tmp)
        res = records[offset:limit]
        
        for i in range(len(res)):
            if res[i][0] == 2 and res[len(res)-1][0] == 3:
                res.append(res[i])
                del res[i]
                i = i - 1
                        
        return res
        
    def _get_lines(self, doc):
        order_obj = self.pool.get('purchase.order')
        line_obj = self.pool.get('purchase.order.line')
        line_ids = line_obj.search(self.cr, self.uid, [('id','in',order_obj.browse(self.cr, self.uid, doc.id).order_line.ids)], order = 'name')
        return line_obj.browse(self.cr, self.uid, line_ids)

    def _get_templates(self, doc, proper=True):
        res = []
        for line in self._get_lines(doc):
            if line.product_id:
                if proper and line.product_id.product_tmpl_id.attribute_line_ids and len(line.product_id.product_tmpl_id.attribute_line_ids.ids) == 2:
                    res.append(line.product_id.product_tmpl_id)
                if not proper and (not line.product_id.product_tmpl_id.attribute_line_ids or  len(line.product_id.product_tmpl_id.attribute_line_ids.ids) != 2):
                    res.append(line)
        return list(set(res))

    def _get_prices(self, doc, template):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template:
                price = line.price_unit
                if price not in res:
                    res.append(price)
        return res
    
    def _get_tax(self, doc, template, price):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template and line.price_unit == price:
                tax = line.taxes_id
                if tax not in res:
                    res.append(tax)
        return res

    def _get_colors(self, doc, template, price, tax):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template and line.price_unit == price and line.taxes_id == tax:
                for value in line.product_id.attribute_value_ids:
                    if value.attribute_id.position == 'row' and value not in res:
                        res.append(value)
                        break
        return res
        
    def _get_sizes(self, template):
        res = []
        tmpl_obj = self.pool.get('product.template')
        for attribute in tmpl_obj.browse(self.cr,self.uid,template).attribute_line_ids:
            if attribute.attribute_id.position == 'column':
                for size in attribute.value_ids:
                    res.append(size)
                break
        return res

    def _get_line(self,doc,template,color,size, price, tax):
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template.id and (line.product_id.attribute_value_ids[0].id == color.id or line.product_id.attribute_value_ids[1].id == color.id) and (line.product_id.attribute_value_ids[1].id == size.id or line.product_id.attribute_value_ids[0].id == size.id) and line.price_unit == price and line.taxes_id == tax:
                return line
        return False
    
    def _get_move_line(self, move_id):
        hrs = self.pool.get('account.move.line')
        hrs_list = hrs.search(self.cr, self.uid,
                              [('move_id', '=', move_id),
                               ('date_maturity', '!=', False), ],
                              order='date_maturity')
        move_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return move_lines    
    
class report_purchase_order(osv.AbstractModel):
    _name = 'report.report_qweb_montecristo.report_purchase_order'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_montecristo.report_purchase_order'
    _wrapped_report_class = report_purchase_order_parser
