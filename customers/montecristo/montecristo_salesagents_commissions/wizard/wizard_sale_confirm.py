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

class sale_order_approve(osv.osv_memory):
    _name = "sale.order.approve"
    _description = "Sale Orders Approve"

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        order = self.pool.get('sale.order').browse(cr, uid, record_id, context=context)
        if order.state != 'draft' and order.state != 'sent':
            raise osv.except_osv(_('Warning!'), _('You can approve only sale orders in draft or sent state.'))
        return False

    def approve_order(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        for sale_order in order_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
            if sale_order.state != 'draft' and sale_order.state != 'sent':
                raise osv.except_osv(_('Warning!'), _("You can't approve the following order: %s") % (sale_order.name))
        
        for sale_order in order_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
            order_obj.write(cr, uid, [sale_order.id], {'confirmed':True})

class sale_order_confirm(osv.osv_memory):
    _name = "sale.order.confirm"
    _description = "Sale Orders Confirm"

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        order = self.pool.get('sale.order').browse(cr, uid, record_id, context=context)
        if order.state != 'draft' and order.state != 'sent':
            raise osv.except_osv(_('Warning!'), _('You can confirm only sale orders in draft or sent state.'))
        return False

    def confirm_order(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        for sale_order in order_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
            if sale_order.state != 'draft' and sale_order.state != 'sent':
                raise osv.except_osv(_('Warning!'), _("You can't confirm the following order: %s") % (sale_order.name))
        
        for sale_order in order_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
            order_obj.action_button_confirm(cr, uid, [sale_order.id], [])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
