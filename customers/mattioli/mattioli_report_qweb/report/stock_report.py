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
from datetime import date
import locale


class stock_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(stock_report_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_record': self._get_record,
            'get_pack': self._get_pack,
            'get_essence': self._get_essence,
            'get_seasoning': self._get_seasoning,
            'get_wood_quality': self._get_wood_quality,
            'get_wood_type': self._get_wood_type,
            'get_thickness': self._get_thickness,
            'get_num_pieces': self._get_num_pieces,
            'get_length': self._get_length,
            'get_width': self._get_width,
            'get_surface': self._get_surface,
            'get_volume': self._get_volume,
            'get_supplier': self._get_supplier,
        })
        self.context = context

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

    def _get_length(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        res = ''
        lst = []
        for quant in mov_id[0]:
            move_data = move_obj.browse(self.cr, self.uid, quant.id)
            temp_id = move_data.product_id.id
            temp_length = self._get_size(temp_id,"Lunghezza")
            if temp_length != 0 and temp_length not in lst:
                if temp_length - int(temp_length) == 0:
                    lst.append(int(temp_length))
                else:
                    lst.append(temp_length)

        lst.sort()
        if len(lst)>0:
            if len(lst) == 1:
                return str(lst[0])
            else:
                res = res + str(lst[0])
                for i in range(1, len(lst)):
                    res = res + ' - ' + str(lst[i])
        return res

    def _get_width(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        res = ''
        lst = []
        for quant in mov_id[0]:
            move_data = move_obj.browse(self.cr, self.uid, quant.id)
            temp_id = move_data.product_id.id
            temp_width = self._get_size(temp_id,"Larghezza")
            if temp_width != 0 and temp_width not in lst:
                if temp_width - int(temp_width) == 0:
                    lst.append(int(temp_width))
                else:
                    lst.append(temp_width)

        lst.sort()
        if len(lst)>0:
            if len(lst) == 1:
                return str(lst[0])
            else:
                res = res + str(lst[0])
                for i in range(1,len(lst)):
                    res = res + ' - ' + str(lst[i])
        return res 

    def _get_thickness(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        prod_obj = self.pool.get('product.product')

        move_data = move_obj.browse(self.cr, self.uid, mov_id[0][0].id)
        prod_data = prod_obj.browse(self.cr, self.uid, move_data.product_id.id)
        if prod_data.thickness and prod_data.thickness > 0:
            thck = int(prod_data.thickness)
            if (thck - prod_data.thickness) == 0:
                return str(thck)
            return str(prod_data.thickness)
        return ''

    def _get_surface(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        res = ''
        surface = 0
        for quant in mov_id[0]:
            move_data = move_obj.browse(self.cr, self.uid, quant.id)
            temp_id = move_data.product_id.id
            num_pieces = move_data.qty
            temp_width = self._get_size(temp_id,"Larghezza")
            temp_length = self._get_size(temp_id,"Lunghezza")

            surface = surface + (temp_width*temp_length*num_pieces)

        surface = surface / 10000
        locale.setlocale(locale.LC_NUMERIC, 'it_IT')
        res = locale.format("%.3f", round(surface,3), grouping=True)
        return res

    def _get_volume(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        prod_obj = self.pool.get('product.product')
        res = ''
        volume = 0
        for quant in mov_id[0]:
            move_data = move_obj.browse(self.cr, self.uid, quant.id)
            temp_id = move_data.product_id.id
            prod_data = prod_obj.browse(self.cr, self.uid, temp_id)

            num_pieces = move_data.qty
            temp_thickness = prod_data.thickness
            temp_width = self._get_size(temp_id,"Larghezza")
            temp_length = self._get_size(temp_id,"Lunghezza")

            volume = volume + (temp_width*temp_length*temp_thickness*num_pieces)

        volume = volume/1000000
        locale.setlocale(locale.LC_NUMERIC, 'it_IT')
        res = locale.format("%.3f", round(volume,3), grouping=True)
        return res

    def _get_essence(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        prod_obj = self.pool.get('product.product')
        esnc_obj = self.pool.get('res.essence')

        move_data = move_obj.browse(self.cr, self.uid, mov_id[0][0].id)
        prod_data = prod_obj.browse(self.cr, self.uid, move_data.product_id.id)
        if prod_data.essence:
            esnc_data = esnc_obj.browse(self.cr, self.uid, prod_data.essence.id) 
            return esnc_data.name
        return ''

    def _get_seasoning(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        prod_obj = self.pool.get('product.product')
        seas_obj = self.pool.get('res.seasoning')

        move_data = move_obj.browse(self.cr, self.uid, mov_id[0][0].id)
        prod_data = prod_obj.browse(self.cr, self.uid, move_data.product_id.id)
        if prod_data.seasoning:
            seas_data = seas_obj.browse(self.cr, self.uid, prod_data.seasoning.id) 
            return seas_data.name
        return ''

    def _get_wood_quality(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        prod_obj = self.pool.get('product.product')
        qual_obj = self.pool.get('res.wood.quality')
        fini_obj = self.pool.get('res.finiture')
        res = ''
        move_data = move_obj.browse(self.cr, self.uid, mov_id[0][0].id)
        prod_data = prod_obj.browse(self.cr, self.uid, move_data.product_id.id)
        if prod_data.wood_quality:
            qual_data = qual_obj.browse(self.cr, self.uid, prod_data.wood_quality.id)
            res = qual_data.name
        if prod_data.finiture:
            fini_data = fini_obj.browse(self.cr, self.uid, prod_data.finiture.id)
            res = res + ' - ' + fini_data.name
        return res

    def _get_wood_type(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        prod_obj = self.pool.get('product.product')
        type_obj = self.pool.get('res.wood.type')

        move_data = move_obj.browse(self.cr, self.uid, mov_id[0][0].id)
        prod_data = prod_obj.browse(self.cr, self.uid, move_data.product_id.id)
        if prod_data.wood_type:
            type_data = type_obj.browse(self.cr, self.uid, prod_data.wood_type.id) 
            return type_data.name
        return ''

    def _get_num_pieces(self, mov_id):
        move_obj = self.pool.get('stock.quant')
        res = 0
        for quant in mov_id[0]:
            move_data = move_obj.browse(self.cr, self.uid, quant.id)
            res = res + move_data.qty
        return str(int(res))

    def _get_pack(self, mov_id):
        res = mov_id[0][1]
        return res

    def _get_supplier(self, mov_id):
        res = ''
        self.cr.execute("""
                        SELECT prt.name
                            FROM
                                stock_quant AS qnt,
                                stock_quant_package AS pck,
                                stock_move AS mov,
                                stock_quant_move_rel AS qm_rel,
                                purchase_order_line AS lin,
                                purchase_order AS ord,
                                res_partner AS prt
                            WHERE
                                pck.id = %s AND
                                qnt.package_id = pck.id AND
                                qm_rel.quant_id = qnt.id AND
                                mov.purchase_line_id = lin.id AND
                                qm_rel.move_id = mov.id AND
                                lin.order_id = ord.id AND
                                ord.partner_id = prt.id
                        """, (mov_id.id,))
        qry = self.cr.fetchall()
        if qry and qry[0] and qry[0][0]:
            res = qry[0][0].upper()
            res = res[:3]
        return res

    def _get_record(self, docs):
        move_obj = self.pool.get('stock.quant.package')
        res = []
        for doc in docs:
            move_data = move_obj.browse(self.cr, self.uid, doc.id)
            t = {}
            t[0] = move_data.quant_ids
            t[1] = move_data.name
            z = move_data.create_date.split('-')
            z2 = z[2].split(' ')
            creationDate = date(int(z[0]), int(z[1]), int(z2[0]))
            t[2] = creationDate.strftime('%d/%m/%Y')
            if 'notes' in move_data:
                t[3] = move_data.notes
            else:
                t[3] = ""
            res.append(t)
        return res


class report_package_barcode(osv.AbstractModel):
    _name = 'report.mattioli_report_qweb.report_package_barcode'
    _inherit = 'report.abstract_report'
    _template = 'mattioli_report_qweb.report_package_barcode'
    _wrapped_report_class = stock_report_parser
