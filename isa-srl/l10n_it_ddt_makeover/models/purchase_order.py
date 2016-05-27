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
from operator import attrgetter
from openerp.tools.translate import _


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def _get_picking_ids(self, cr, uid, ids, field_names, args, context=None):
        res = super(PurchaseOrder, self)._get_picking_ids(cr, uid, ids, field_names, args, context=context)
        query = """ SELECT p.id, po.id FROM stock_picking p, purchase_order po, procurement_group gr WHERE po.id in %s and po.name = gr.name and p.group_id = gr.id GROUP BY p.id, po.id             """
        cr.execute(query, (tuple(ids), ))
        picks = cr.fetchall()
        for pick_id, po_id in picks:
            res[po_id].append(pick_id)
        return res

    _columns = {
        'picking_ids': fields.function(_get_picking_ids, method=True, type='one2many', relation='stock.picking', string='Picking List', help="This is the list of receipts that have been generated for this purchase order."),                
    }

    def action_cancel(self, cr, uid, ids, context=None):
        for purchase in self.browse(cr, uid, ids, context=context):
            chk = True
            for pick in purchase.picking_ids:
                if pick.state == 'done':
                    chk = False
            if chk:
                self.pool.get('stock.picking').action_cancel(cr, uid, [x.id for x in purchase.picking_ids if x.state != 'cancel'], context=context)
            for inv in purchase.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise orm.except_orm(
                        _('Unable to cancel this purchase order.'),
                        _('You must first cancel all invoices related to this purchase order.'))
            self.pool.get('account.invoice') \
                .signal_workflow(cr, uid, map(attrgetter('id'), purchase.invoice_ids), 'invoice_cancel')
        self.signal_workflow(cr, uid, ids, 'purchase_cancel')
        self.write(cr, uid, ids, {'state':'cancel'})
        return True
