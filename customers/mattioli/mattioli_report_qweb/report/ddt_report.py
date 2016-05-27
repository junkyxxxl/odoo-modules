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


class ddt_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(ddt_report_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_records': self._get_records,
            'get_customer_code': self._get_customer_code,
            'get_shipping_costs': self._get_shipping_costs,
            'get_num_pieces': self._get_num_pieces,
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

    def _get_size(self, prod_id, field):
        res = 0
        self.cr.execute("""
                    SELECT 
                        val.name
                    FROM
                        product_attribute_value_product_product_rel AS vp_rel,
                        product_attribute_line_product_attribute_value_rel AS lv_rel,
                        product_attribute AS att,
                        product_attribute_value AS val,
                        product_attribute_line AS lin,
                        product_product AS prd
                    WHERE
                        prd.id = %s AND
                        vp_rel.prod_id = prd.id AND
                        vp_rel.att_id = lv_rel.val_id AND
                        lv_rel.line_id = lin.id AND
                        lin.attribute_id = att.id AND
                        lin.product_tmpl_id = prd.product_tmpl_id AND
                        lv_rel.val_id = val.id AND
                        att.name = %s
                """,
                (prod_id, field))
        qry = self.cr.fetchall()
        if qry and qry[0] and qry[0][0]:
            try:
                res = float(qry[0][0])
            except:
                None
        else:
            self.cr.execute("""
                        SELECT
                            val.name
                        FROM
                            product_attribute_line_product_attribute_value_rel AS lv_rel,
                            product_attribute AS att,
                            product_attribute_line AS lin,
                            product_product AS prd,
                            product_template AS tmpl,
                            product_attribute_value AS val
                        WHERE
                            prd.id = %s AND
                            prd.product_tmpl_id = tmpl.id AND
                            lin.product_tmpl_id = tmpl.id AND
                            lin.attribute_id = att.id AND    
                            lv_rel.line_id = lin.id AND
                            lv_rel.val_id = val.id AND
                            att.name = %s
                    """,
                    (prod_id, field))
            qry = self.cr.fetchall()
            if qry and qry[0] and qry[0][0]:
                try:
                    res = float(qry[0][0])
                except:
                    None                    
        return res

    def _get_num_pieces(self, doc):
        res = 0
        for line in doc.move_lines:
            if line.product_id and line.product_id.is_shipping:
                continue
            
            res+=line.product_uom_qty
        return res

    def _get_records(self, doc):
        res = []
        inv_data = doc
        for line in inv_data.move_lines:
            
            if line.product_id and line.product_id.is_shipping:
                continue
            
            tmp = []
            
            if line.product_id:
                tmp.append(line.product_id.default_code)
            else:
                tmp.append('')
            
            
            description = ''
            if line.product_id:
                description+=line.name + ' '
                
                if '(' in description and ')' in description:
                    i_start = description.index('(')
                    i_end = description.index(')')                    
                    description = description.replace(description[i_start:i_end+1],'')                
                
                if line.product_id.essence:
                    description+=line.product_id.essence.name + ' '
                if line.product_id.wood_quality:                
                    description+=line.product_id.wood_quality.code + ' '
                if line.product_id.finiture:
                    description+=line.product_id.finiture.code + ' '
                if line.product_id.seasoning:
                    description+=line.product_id.seasoning.code + ' '
            else:
                description+=line.name
            
                
            tmp.append(description)
            tmp.append(line.product_uom_qty)
               
            '''CALCOLO DIMENSIONI'''                
            if line.product_id:
                
                if line.procurement_id and line.procurement_id.sale_line_id:
                    if line.product_id.thickness == line.procurement_id.sale_line_id.thickness:                           
                        temp_thickness = line.product_id.thickness
                    elif line.product_uom_qty:
                        temp_thickness = line.procurement_id.sale_line_id.thickness * line.product_uom_qty
                    else:
                        temp_thickness = 0.0    
                else:
                    temp_thickness = line.product_id.thickness
                         
                if line.product_id.increment_thickness:
                    if line.product_id.increment_uom_thickness == 'cm':
                        temp_thickness += line.product_id.increment_thickness
                    else:
                        temp_thickness *= 1+(line.product_id.increment_thickness/100) 
                                
                    
                
                if line.procurement_id and line.procurement_id.sale_line_id:            
                    if line.procurement_id.sale_line_id.width == 1 and line.procurement_id.sale_line_id.length == 1:
                        temp_width = 0.0
                    elif self._get_size(line.product_id.id,"Larghezza") == line.procurement_id.sale_line_id.width:                                 
                        temp_width = self._get_size(line.product_id.id,"Larghezza")
                    elif line.product_uom_qty:
                        temp_width = line.procurement_id.sale_line_id.width * line.product_uom_qty
                    else:
                        temp_width = 0.0   
                else:
                    temp_width = self._get_size(line.product_id.id,"Larghezza")
                                          
                if line.product_id.increment_width:
                    if line.product_id.increment_uom_width == 'cm':
                        temp_width += line.product_id.increment_width
                    else:
                        temp_width *= 1+(line.product_id.increment_width/100) 
              

                if line.procurement_id and line.procurement_id.sale_line_id: 
                    if line.procurement_id.sale_line_id.width == 1 and line.procurement_id.sale_line_id.length == 1:
                        temp_length = 0.0                    
                    elif self._get_size(line.product_id.id,"Lunghezza") == line.procurement_id.sale_line_id.length:                          
                        temp_length = self._get_size(line.product_id.id,"Lunghezza")
                    elif line.product_uom_qty:
                        temp_length = line.procurement_id.sale_line_id.length * line.product_uom_qty
                    else:
                        temp_length = 0.0
                else:
                    temp_length = self._get_size(line.product_id.id,"Lunghezza")                                
                                         
                if line.product_id.increment_length:
                    if line.product_id.increment_uom_length == 'cm':
                        temp_length += line.product_id.increment_length
                    else:
                        temp_length *= 1+(line.product_id.increment_length/100)            

            else:
                temp_width = 0.0
                temp_length = 0.0
                temp_thickness = 0.0
            '''FINE CALCOLO DIMENSIONI''' 
            
            tmp.append(temp_width)            
            tmp.append(temp_length)
            tmp.append(temp_thickness)
            
            if line.product_uos and line.product_uos.is_cubic_meter:
                tmp.append('MC')
                tmp.append(line.product_uos_qty)                
            elif line.product_uos and line.product_uos.is_square_meter:
                tmp.append('MQ')
                tmp.append(line.product_uos_qty)              
            else:
                tmp.append('')
                tmp.append('')
                        
            res.append(tmp)
            
        return res

    def _get_shipping_costs(self, doc):
        res = 0.0
        for line in doc.move_lines:
            if line.product_id and line.product_id.is_shipping:
                res += line.price_unit * line.quantity
        return res

class report_invoice(osv.AbstractModel):
    _name = 'report.mattioli_report_qweb.mattioli_report_ddt'
    _inherit = 'report.abstract_report'
    _template = 'mattioli_report_qweb.mattioli_report_ddt'
    _wrapped_report_class = ddt_report_parser
