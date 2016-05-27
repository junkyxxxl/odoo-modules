# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools.translate import _

class stock_invoice_onshipping_makeover(osv.osv_memory):
    
    def _get_journal(self, cr, uid, context=None):

        jour_obj = self.pool.get('account.journal')
        journal_type = self._get_journal_type(cr, uid, context=context)
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        cmp_id = company_id.id
        
        if journal_type == 'sale':
            if company_id.sale_journal_default:
                return company_id.sale_journal_default
            else:
                return self.pool.get('account.journal').search(cr, uid, [('type','=','sale'),('company_id','=', cmp_id)], limit=1, context=context)
                
        if journal_type == 'purchase':
            if company_id.purchase_journal_default:
                return company_id.purchase_journal_default
            else:
                return self.pool.get('account.journal').search(cr, uid, [('type','=','purchase'),('company_id','=', cmp_id)], limit=1, context=context)
                
        if journal_type == 'sale_refund':
            if company_id.sale_refund_journal_default:
                return company_id.sale_refund_journal_default     
            else:
                return self.pool.get('account.journal').search(cr, uid, [('type','=','sale_refund'),('company_id','=', cmp_id)], limit=1, context=context)
                       
        if inv_type == 'purchase_refund':
            if company_id.purchase_refund_journal_default:
                return company_id.purchase_refund_journal_default
            else:
                return self.pool.get('account.journal').search(cr, uid, [('type','=','purchase_refund'),('company_id','=', cmp_id)], limit=1, context=context)
        return None

    _inherit = "stock.invoice.onshipping"
    _columns = {
        'journal_id': fields.many2one('account.journal', 'Destination Journal', required=True),
    }
    _defaults = {
        'journal_id' : _get_journal,
    }

