# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):

        self.type_article = []
        self.type_subtotal = []
        self.type_title = []
        self.type_text = []
        self.type_line = []
        self.type_break = []
        self.cr = cr
        self.uid = uid

        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_lines': self._get_move_line,
            'printable': self.printable,
        })

    def _get_move_line(self, invoice_id):
        hrs = self.pool.get('account.invoice.line')
        hrs_list = hrs.search(self.cr, self.uid,
                              [('invoice_id', '=', invoice_id), ])
        move_lines = hrs.browse(self.cr, self.uid, hrs_list)
        return move_lines

    # elimina la quantità per il tipo template
    def printable(self, num):
        if num > 0:
            return True
        return False
