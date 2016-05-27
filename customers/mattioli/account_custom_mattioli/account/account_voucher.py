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

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.osv.orm import browse_record


class account_voucher_makeover(orm.Model):
    _inherit = 'account.voucher'

    def _get_untaxed_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            res[voucher.id] = voucher.amount - voucher.tax_amount
        return res
    
    _columns = {
                'untaxed_amount': fields.function(_get_untaxed_amount, string='Totale Imponibile', store= True, type="float"),
    }

class account_voucher_line_makeover(orm.Model):
    _inherit = 'account.voucher.line'

    def _get_document_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        acc_obj = self.pool.get('account.invoice')
        for voucher_line in self.browse(cr, uid, ids, context):
            res[voucher_line.id] = None
            name = voucher_line.move_line_id.move_id.ref
            if name:
                acc_id = acc_obj.search(cr, uid, [('number','=',name)], context=context)
                if acc_id:
                    acc_data = acc_obj.browse(cr, uid, acc_id[0], context=context)
                    res[voucher_line.id] = acc_data.date_invoice
        return res    

    _columns = {
                'date_document_origin': fields.function(_get_document_date, string='Data Documento', type='date', store = True),
    }
