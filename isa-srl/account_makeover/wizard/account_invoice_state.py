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

from openerp.osv import osv
from openerp.tools.translate import _

class account_invoice_confirm_makeover(osv.osv_memory):

    _inherit = "account.invoice.confirm"

    def invoice_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        
        proxy = self.pool['account.invoice']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.type not in ('out_invoice', 'out_refund'):
                raise osv.except_osv(_('Warning!'), _("You're trying to confirm supplier invoices. Only the massive confirmation of out invoices is allowed"))
            
        return super(account_invoice_confirm_makeover,self).invoice_confirm(cr,uid,ids,context=context)
