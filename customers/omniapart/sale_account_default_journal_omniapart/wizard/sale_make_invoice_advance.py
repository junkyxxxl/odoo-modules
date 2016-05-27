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

from openerp.osv import fields, osv

class sale_advance_payment_inv_omniapart(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"
    
    _columns = {
                'journal_id': fields.many2one('account.journal', 'Sale Journal',),
    }    

    def _get_journal_id(self,cr,uid,context=None):
        jour_obj = self.pool.get('account.journal')
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        cmp_id = company_id.id
        
        if company_id.sale_journal_default:
            return company_id.sale_journal_default
        else:
            jour_ids = jour_obj.search(cr,uid, [('xcash_vat','=',True),('type','=','sale'),('company_id','=', cmp_id)],context=context)
        if jour_ids:
            return jour_ids[-1]
        return None
    
    _defaults = {
        'journal_id': _get_journal_id,
    }