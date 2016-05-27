# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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
from openerp.osv import osv
from openerp.report import report_sxw


class ddt_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(ddt_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'time': time,
            'get_type':self._get_type,
            'get_weight':self._get_weight,
            'get_order_ddt_line': self._get_order_ddt_line,
            'carriage_returns':self._carriage_returns,
            'get_record':self._get_record,
            'get_num_pages':self._get_num_pages,
            'get_order_ddt_line_length':self._get_order_ddt_line_length,
            'get_uom': self._get_uom,
        })
        self.context = context

    def _get_uom(self, uom_id):
        context = {'lang':'it_IT',}
        return self.pool.get('product.uom').browse(self.cr, self.uid, uom_id, context).name

    def _get_record(self, ddt_id):
        ddt_obj = self.pool.get('stock.ddt')
        ddt_data = ddt_obj.browse(self.cr, self.uid, ddt_id)
        return ddt_data

    def _get_num_pages(self, ddt_id, limit_page, limit_page_last):
        res = 0
        lines = self._get_order_ddt_line(ddt_id, 0, 0)
        if lines and lines.ids:
            res = float(len(lines.ids))
            res = res/limit_page
            res = math.ceil(res)
            if len(lines.ids)%limit_page > limit_page_last:
                res = res + 1
        return int(res)

    def _get_order_ddt_line_length(self, pick_id, limit_page, offset_page):
        res = 0
        lines = self._get_order_ddt_line(pick_id, limit_page, offset_page)
        if lines and lines.ids:
            res = len(lines.ids)
        return res

    def _get_order_ddt_line(self, pick_id, limit_page, offset_page):
        ddt_obj = self.pool.get('stock.ddt')
        ddt_data = ddt_obj.browse(self.cr, self.uid, pick_id)

        return ddt_data.ddt_lines

    def _get_type(self, ddt_id):
        ddt_obj = self.pool.get('stock.ddt')
        ddt_data = ddt_obj.browse(self.cr, self.uid, ddt_id)
        t_qty_count = 0
        for pick_data in ddt_data.picking_ids:
            return pick_data.picking_type_id.name
        return ''

    def _get_weight(self, pick_id):
        t_weight_count = 0
        pick_obj = self.pool.get('stock.ddt')
        pick_data = pick_obj.browse(self.cr, self.uid, pick_id)
        for move_data in pick_data.ddt_lines:
            if move_data.product_id and move_data.product_id.weight:
                t_weight_count = t_weight_count + move_data.product_qty * move_data.product_id.weight
        return t_weight_count

    def _carriage_returns(self, text):
        if text:
            text.replace('\n', '<br />')
            return text 


class report_ddt_makeover(osv.AbstractModel):
    _name = 'report.l10n_it_ddt_makeover.report_ddt_makeover'
    _inherit = 'report.abstract_report'
    _template = 'l10n_it_ddt_makeover.report_ddt_makeover'
    _wrapped_report_class = ddt_report
