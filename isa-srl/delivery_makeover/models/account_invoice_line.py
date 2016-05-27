# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, orm
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _


class account_invoice_line_ddt(orm.Model):
    _inherit = 'account.invoice.line'

    def _get_ddt_origin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            if (line.document_reference_id
                and line.document_reference_id.ddt_id
                and line.document_reference_id.ddt_id.ddt_number):
                t_ddt_number = line.document_reference_id.ddt_id.ddt_number
                t_ddt_date_ref = line.document_reference_id.ddt_id.ddt_date
                t_ddt_date = datetime.strptime(t_ddt_date_ref,
                                           DF).strftime("%d/%m/%Y")
                res[line.id] = t_ddt_number + _(" of ") + t_ddt_date
        return res

    _columns = {
        # recupera il ddt se presente
        'ddt_origin': fields.function(_get_ddt_origin,
                                   store=True,
                                   type="char",
                                   string="DDT"),
        # contiene il riferimento allo stock picking
        'document_reference_id':fields.many2one('stock.picking',
                                   'Document Reference'),
    }
