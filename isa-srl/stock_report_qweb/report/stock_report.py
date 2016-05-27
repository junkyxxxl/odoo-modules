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
            'get_record':self._get_record,
            'get_name':self._get_name,
            'get_moves':self._get_moves,
            'get_pack':self._get_pack,
        })
        self.context = context

    def _get_moves(self,mov_id):
        move_obj = self.pool.get('stock.quant')
        res = []
        for quant in mov_id[0]:
            move_data = move_obj.browse(self.cr, self.uid, quant.id)
            t = {}
            t[0]=move_data.product_id.id
            t[1]=move_data.product_id.uom_id.name
            t[2]=move_data.lot_id
            t[3]=move_data.lot_id.name
            t[4]=move_data.qty
            res.append(t)
        return res
    
    def _get_pack(self, mov_id):
        res = mov_id[0][1]
        return res

    def _get_name(self, product_id):
        product_obj = self.pool.get('product.product')
        product_name = product_obj.name_get(self.cr,self.uid,product_id)
        return product_name[0][1]
    
    def _get_record(self, docs):
        move_obj = self.pool.get('stock.quant.package')
        res = []
        for doc in docs:
            move_data = move_obj.browse(self.cr, self.uid, doc.id)
            t = {}
            t[0]=move_data.quant_ids
            t[1]=move_data.name
            res.append(t)
        return res
    
class report_package_barcode(osv.AbstractModel):
    _name = 'report.stock_report_qweb.report_package_barcode'
    _inherit = 'report.abstract_report'
    _template = 'stock_report_qweb.report_package_barcode'
    _wrapped_report_class = stock_report_parser
    
