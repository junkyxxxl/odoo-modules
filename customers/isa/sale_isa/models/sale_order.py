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


class SaleOrder(orm.Model):
    _inherit = 'sale.order'
    _columns = {
        'cancel_reason': fields.text('Cancel Reason', size=256),
        'cancel_state': fields.selection([
            ('replaced', 'Quotation Replaced'),
            ('expired', 'Quotation Expired'),
            ('rejected', 'Quotation Rejected'),
            ], 'Cancel Status',
            help="Gives the reason of the cancellation of the quotation or sales order. \nThe status is automatically set when a cancel operation occurs in the processing of the sales order.", select=True),
    }

    def cancel_replaced(self, cr, uid, ids, context=None):
        res = super(SaleOrder, self).action_cancel(cr, uid, ids, context)
        self.write(cr, uid, ids, {'cancel_state': 'replaced'})
        return res

    def cancel_expired(self, cr, uid, ids, context=None):
        res = super(SaleOrder, self).action_cancel(cr,  uid, ids, context)
        self.write(cr, uid, ids, {'cancel_state': 'expired'})
        return res

    def cancel_rejected(self, cr, uid, ids, context=None):
        res = super(SaleOrder, self).action_cancel(cr, uid, ids, context)
        self.write(cr, uid, ids, {'cancel_state': 'rejected'})
        return res

    def manual_invoice(self, cr, uid, ids, context=None):
        res = super(SaleOrder, self).manual_invoice(cr, uid, ids, context=context)
        inv_obj = self.pool.get('account.invoice')
        if context.get('wiz_date', False) and res.get('res_id', False):
            res_ids = [res['res_id']]
            if isinstance(res['res_id'], list):
                res_ids = res['res_id']

            if res_ids:
                inv_obj.write(cr, uid, res_ids,
                              {'date_invoice': context['wiz_date'],
                               'registration_date': context['wiz_date'],
                               })
        return res
