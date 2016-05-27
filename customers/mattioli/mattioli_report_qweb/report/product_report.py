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


class mattioli_product_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(mattioli_product_report_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_record': self._get_record,
        })
        self.context = context

    def _get_record(self, docs):
        prod_obj = self.pool.get('product.product')
        res = []
        for doc in docs:
            
            prod_data = prod_obj.browse(self.cr, self.uid, doc.id)
            t = {}
            t[0] = prod_data.name
            t[1] = prod_data.ean13
            t[2] = prod_data.description

            res.append(t)
        return res


class mattioli_report_product_barcode(osv.AbstractModel):
    _name = 'report.mattioli_report_qweb.mattioli_report_product_barcode'
    _inherit = 'report.abstract_report'
    _template = 'mattioli_report_qweb.mattioli_report_product_barcode'
    _wrapped_report_class = mattioli_product_report_parser
