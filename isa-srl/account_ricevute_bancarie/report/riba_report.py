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


class riba_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(riba_report_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_records': self._get_records,
        })
        self.context = context

    def _get_records(self, doc):
        res = []
        count = 0
        total = 0.0
        riba = doc
        riba_line_ids = self.pool.get('riba.distinta.line').search(self.cr, self.uid, [('id','in',riba.line_ids.ids)],order='due_date, partner_name_id',context=self.context)
        riba_line_ids = self.pool.get('riba.distinta.line').browse(self.cr, self.uid, riba_line_ids, context=self.context)
        for line in riba_line_ids:
            tmp = []
            tmp.append(0)
            if count % 2 == 0:
                tmp.append('#FFFFFF')
            else:
                tmp.append('#CCCCCC')
            tmp.append(line.invoice_number)        
            tmp.append(line.invoice_date)
            tmp.append(line.partner_id.name)
            tmp.append(line.iban)
            tmp.append(line.amount)
            tmp.append(line.due_date)    
            tmp.append(line.sequence)                        
            res.append(tmp)
            
            count+= 1
            total+=line.amount
        
        tmp = []
        tmp.append(1)
        if count % 2 == 0:
            tmp.append('#FFFFFF')
        else:
            tmp.append('#CCCCCC')
        tmp.append(' ')
        tmp.append(' ')
        tmp.append(' ')
        tmp.append('TOT:')
        tmp.append(total)
        tmp.append(' ')
        tmp.append(' ')
        res.append(tmp)        
        
        return res

class report_invoice(osv.AbstractModel):
    _name = 'report.account_ricevute_bancarie.report_riba'
    _inherit = 'report.abstract_report'
    _template = 'account_ricevute_bancarie.report_riba'
    _wrapped_report_class = riba_report_parser
