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
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _

class invoice_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(invoice_report_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_move_line':self._get_move_line,
            'get_order_invoice_line': self._get_order_invoice_line,
            'has_picking': self._has_picking,
            'count_lines': self._count_lines,
            'carriage_returns':self._carriage_returns,
            'get_record':self._get_record,
            'get_num_pages':self._get_num_pages,
            'get_order_invoice_line_length':self._get_order_invoice_line_length,
            'get_uom': self._get_uom,
            'get_payment_term':self._get_payment_term,
            'is_there_maturities': self._is_there_maturities,
            'get_vat_amount': self._get_vat_amount,
            'discount_presence': self._discount_presence,
            'is_there_vat': self._is_there_vat,
        })
        self.context = context

    def _get_uom(self, uom_id):
        context = {'lang':'it_IT',}
        return self.pool.get('product.uom').browse(self.cr, self.uid, uom_id, context).name

    def _get_payment_term(self, payment_id):
        context = {'lang':'it_IT',}
        payment_data = self.pool.get('account.payment.term').browse(self.cr, self.uid, payment_id, context)
        return payment_data.name
        

    def _carriage_returns(self, text):
          if text:
             text.replace('\n', '<br />')
             return text 

    def _get_move_line(self, move_id):
        hrs = pooler.get_pool(self.cr.dbname).get('account.move.line')
        hrs_list = hrs.search(self.cr, self.uid,
                              [('move_id', '=', move_id),
                               ('date_maturity', '!=', False), ],
                              order='date_maturity')
        move_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return move_lines

    def _is_there_vat(self, invoice):
        for t_line in invoice.tax_line:
            if (not t_line.tax_code_id) or (t_line.tax_code_id and not t_line.tax_code_id.notprintable):
                return True
        return False

    def _is_there_maturities(self, move_id):
        moves = self._get_move_line(move_id)
        if len(moves) > 0:
            return True
        return False

    def _get_vat_amount(self, amount):
        return int(amount*100)    

    def _get_num_pages(self,invoice_id,limit_page,limit_page_last):
        res = 0
        lines = self._get_order_invoice_line(invoice_id,0,0)
        if lines and lines.ids:
            res = float(len(lines.ids))
            res = res/limit_page
            res = math.ceil(res)
            if len(lines.ids)%limit_page > limit_page_last:
                res = res + 1
        return int(res)

    def _get_order_invoice_line_length(self, invoice_id, limit_page, offset_page):
        res = 0
        lines = self._get_order_invoice_line(invoice_id, limit_page, offset_page)
        if lines and lines.ids:
            res = len(lines.ids)
        return res

    def _discount_presence(self, invoice_id):
          invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
          for line in invoice.invoice_line:
              if line.discount:
                  return True
          return False

    def _get_order_invoice_line(self, invoice_id, limit_page, offset_page):
        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        invoice_data = invoice_obj.browse(self.cr, self.uid, invoice_id)
        invoice_lines = []
        if invoice_data and invoice_data.invoice_line:
            hrs_list = []
            hrs = pooler.get_pool(self.cr.dbname).get('account.invoice.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('invoice_id', '=', invoice_id), ],
                                  limit=limit_page,
                                  offset=offset_page)
            invoice_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return invoice_lines

    def _has_picking(self, invoice_id):
        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        invoice_data = invoice_obj.browse(self.cr, self.uid, invoice_id)
        res = False
        for t_data in invoice_data.invoice_line:
            if hasattr(t_data, 'document_reference_id'):
                t_ddt = t_data.document_reference_id
                if (t_ddt and 'ddt_id' in t_ddt and t_ddt.ddt_id and t_ddt.ddt_id.ddt_number):
                    res = True
        return res

    def _count_lines(self, invoice_id):
        num_lines = 0
        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        invoice_data = invoice_obj.browse(self.cr, self.uid, invoice_id)
        if invoice_data and invoice_data.invoice_line:
            for _ in invoice_data.invoice_line:
                num_lines = num_lines +1
        return num_lines
    
    def _get_record(self, invoice_id):
        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        invoice_data = invoice_obj.browse(self.cr, self.uid, invoice_id)
        return invoice_data
    
class report_invoice_qweb(osv.AbstractModel):
    _name = 'report.report_qweb_omniapart.report_invoice_qweb'
    _inherit = 'report.abstract_report'
    _template = 'report_qweb_omniapart.report_invoice_qweb'
    _wrapped_report_class = invoice_report_parser
    
