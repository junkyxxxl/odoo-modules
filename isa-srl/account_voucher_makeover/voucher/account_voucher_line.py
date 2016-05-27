# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
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

from openerp.osv import fields, orm

class account_voucher_line(orm.Model):
    _inherit = "account.voucher.line"

    def _is_withholding(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for voucher_line in self.browse(cr, uid, ids, context):
            res[voucher_line.id] = True if (voucher_line.move_line_id.is_wht) else False
        return res

    def _get_document_number(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        acc_obj = self.pool.get('account.invoice')
        for voucher_line in self.browse(cr, uid, ids, context):
            res[voucher_line.id] = None
            name = voucher_line.move_line_id.move_id.ref
            if name:
                acc_id = acc_obj.search(cr, uid, [('number','=',name)], context=context)
                if acc_id:
                    acc_data = acc_obj.browse(cr, uid, acc_id[0], context=context)
                    if acc_data.type == 'in_invoice':
                        res[voucher_line.id] = acc_data.supplier_invoice_number
                    elif acc_data.type == 'out_invoice':
                        res[voucher_line.id] = acc_data.number
        return res    

    _columns = {
        'is_wht': fields.function(_is_withholding, string='Is Wht', type='boolean'),
        'ref_name': fields.related('move_line_id','name', type='char', string = 'Doc Name', store = True),
        'document_number': fields.function(_get_document_number, string='Doc Number', type='char', store = True),
        }
