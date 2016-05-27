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


class report_invoice_payment_term_preview_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(report_invoice_payment_term_preview_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_records':self._get_records,
        })
        self.context = context

    def _get_records(self,doc):
        res = []
        payment_term = doc.payment_term
        if payment_term:
            payment_lines = self.pool.get('account.payment.term').compute(self.cr, self.uid, payment_term.id, doc.amount_total, doc.date_invoice, context=self.context)
        for line in payment_lines:
            tmp = []
            tmp.append(line[0])
            tmp.append(line[1])
            if line[2] == 'D':
                tmp.append('Ricevuta Bancaria')
            elif line[2] == 'B':
                tmp.append('Bonifico')
            elif line[2] == 'C':
                tmp.append('Contanti')
            else:
                tmp.append('')
            res.append(tmp)                                                                      
        return res

class report_invoice_payment_term_preview(osv.AbstractModel):
    _name = 'report.account_payment_term_preview.report_invoice_payment_term_preview'
    _inherit = 'report.abstract_report'
    _template = 'account_payment_term_preview.report_invoice_payment_term_preview'
    _wrapped_report_class = report_invoice_payment_term_preview_parser
