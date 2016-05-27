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


class report_sale_order_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_sale_order_parser,
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
            'get_discount_line': self._get_discount_line,
            'delivery_lines': self._delivery_lines
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
        return datetime.strptime(date, '%Y-%m-%d').strftime('%b').upper() + ' ' + datetime.strptime(date, '%Y-%m-%d').strftime('%Y')

    def _get_discount_line(self,doc):
        res = ''
        if  doc.global_discount_lines:
            for line in doc.global_discount_lines:
                if res:
                    res = res + ' + '
                res = res+str(line.value).replace('.',',')
        return res

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
                res+= line.product_uom_qty
        return int(res)    

    def _get_num_pages(self,doc,limit_page):
        res = 0.0
        for template_id in self._get_templates(doc, True):
            if not template_id.is_shipping:            
                res = res + 1
                for price in self._get_prices(doc, template_id.id):
                    for discount in self._get_discount(doc,template_id.id,price):
                        for tax in self._get_tax(doc,template_id.id,price,discount):
                            for free in self._get_free(doc,template_id.id,price,discount,tax):
                                for color in self._get_colors(doc,template_id.id, price,discount,tax,free):    
                                    res = res + 1
                                    if free:
                                        res = res + 1

        if len(self._get_templates(doc, False)) > 0:
            res = res + 1
        
        for line_id in self._get_templates(doc, False):
            if not line_id.product_id.is_shipping:            
                res = res + 1                   
                if line_id.free:
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
                    #PRENDO GLI SCONTI
                    for discount in self._get_discount(doc,template_id.id,price):
                        #PRENDO LA TASSA
                        for tax in self._get_tax(doc,template_id.id,price,discount):
                            #PRENDO GLI OMAGGI
                            for free in self._get_free(doc,template_id.id,price,discount,tax):                                
                                #PRENDO I COLORI                
                                for color in self._get_colors(doc,template_id.id,price,discount,tax,free):    
                                    tmp = []
                                    total = 0
                                    tmp.append(1)
                                    tmp.append(template_id.tmpl_default_code)
                                    tmp.append(color.name)
                                    tmp.append(template_id.name)
                                    #VALORIZZO LE TAGLIE
                                    for i in range(0,10):
                                        if len(sizes)>=i+1:
                                            order_line = self._get_line(doc,template_id,color,sizes[i],price,discount,tax,free)
                                            if order_line:
                                                tmp.append(int(order_line.product_uom_qty))
                                                total += int(order_line.product_uom_qty)
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
                                    res.append(tmp)
                                    if free == 1:
                                        tmp = []
                                        tmp.append(1)
                                        tmp.append('')
                                        tmp.append('')
                                        tmp.append('Omaggio ai sensi ex art.15 DPR 633/72')
                                        for i in range(4,19):
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
                tmp.append(int(line_id.product_uom_qty))
                if line_id.discount:
                    tmp.append(str(line_id.discount)+'%')
                else:
                    tmp.append('')
                tmp.append(line_id.price_unit)
                tmp.append(line_id.price_subtotal)
                
                if line_id.tax_id:
                    tmp.append(line_id.tax_id[0].tax_code_id.code)
                else:
                    tmp.append('')        
                res.append(tmp) 
                if line_id.free:
                    tmp = []
                    tmp.append(1)
                    tmp.append('')
                    tmp.append('')
                    tmp.append('Omaggio ai sensi ex art.15 DPR 633/72')
                    for i in range(4,19):
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
                tmp.append(int(line.product_uom_qty))
                if line.discount:
                    tmp.append(str(line.discount)+'%')
                else:
                    tmp.append('')
                tmp.append(line.price_unit)
                tmp.append(line.price_subtotal)
                if line.tax_id:
                    tmp.append(line.tax_id[0].tax_code_id.code)
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
        order_obj = self.pool.get('sale.order')
        line_obj = self.pool.get('sale.order.line')
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

    def _get_discount(self, doc, template, price):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template and line.price_unit == price:
                discount = line.discount
                if discount not in res:
                    res.append(discount)
        return res
    
    def _get_tax(self, doc, template, price, discount):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template and line.price_unit == price and line.discount == discount:
                tax = line.tax_id
                if tax not in res:
                    res.append(tax)
        return res

    def _get_free(self, doc, template, price, discount, tax):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template and line.price_unit == price and line.discount == discount  and line.tax_id == tax:
                if line.free in ['gift','base_gift']:
                    free = 1
                else:
                    free = 0
                if free not in res:
                    res.append(free)
        return res

    def _get_colors(self, doc, template, price, discount, tax, free):
        res = []
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template and line.price_unit == price and line.discount == discount and line.tax_id == tax and ((line.free and free) or (not line.free and not free)):
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

    def _get_line(self,doc,template,color,size, price, discount, tax, free):
        for line in self._get_lines(doc):
            if line.product_id.product_tmpl_id.id == template.id and (line.product_id.attribute_value_ids[0].id == color.id or line.product_id.attribute_value_ids[1].id == color.id) and (line.product_id.attribute_value_ids[1].id == size.id or line.product_id.attribute_value_ids[0].id == size.id) and line.price_unit == price and line.discount == discount and line.tax_id == tax and ((line.free and free) or (not line.free and not free)):
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

    def _delivery_lines(self,doc):

        sale_data = doc

        categories_ids = []
        res = []
        miss = []

        if not doc.season.category_dates_id and not doc.date_per_category_ids:
            res.append(['All',self._format_delivery_date(doc.delivery_date)])
            return res
               
        for line in sale_data.order_line:
            
            if line.product_id and line.product_id.categ_id:
                if line.product_id.categ_id.parent_id:
                    tmp = line.product_id.categ_id.parent_id.id
                else:
                    tmp = line.product_id.categ_id.id
                    
                categories_ids.append(tmp)
                    
        categories_ids = list(set(categories_ids))
        
        for category_id in categories_ids:
            find = False
            if doc.date_per_category_ids:
                for dc_line in doc.date_per_category_ids:
                    if dc_line.category_id.id == category_id:
                        find = True
                        t_name = dc_line.category_id.name
                        t_inf = self._format_delivery_date(dc_line.delivery_date)
                        res.append([t_name,t_inf])

            if not find:            
                line_id = self.pool.get('res.family.category.date').search(self.cr, self.uid, [('family_id','=',doc.season.id),('category_id','=',category_id)])
                if line_id:
                    t_name = self.pool.get('product.category').browse(self.cr, self.uid, category_id).name
                    t_inf = self.pool.get('res.family.category.date').browse(self.cr, self.uid, line_id[0]).information                
                    res.append([t_name, t_inf])
                else:
                    miss.append(category_id)
        
        if len(miss) > 0:
            t_name = 'OTHERS'
            t_inf = self._format_delivery_date(doc.delivery_date)
            res.append([t_name,t_inf])
            
        return res
    
class report_product_barcode(osv.AbstractModel):
    _name = 'report.report_qweb_montecristo.report_sale_order'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_montecristo.report_sale_order'
    _wrapped_report_class = report_sale_order_parser
