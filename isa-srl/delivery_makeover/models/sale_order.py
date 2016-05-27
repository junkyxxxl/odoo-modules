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


class sale_order_delivery_makeover(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'delivery_methods': fields.selection([('sender', 'Sender '),
                                              ('receiver', 'Receiver'),
                                              ('carrier', 'Carrier')],
                                             'Trasporto a cura',
                                             select=True,
                                             translate=True),
    }

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order_delivery_makeover,
                    self).onchange_partner_id(cr, uid, ids, part, context)
        if not part:
            return res

        part_data = self.pool.get('res.partner').browse(cr, uid, part, context=context)

        if part_data:
            if part_data.delivery_methods:
                res['value']['delivery_methods'] = part_data.delivery_methods
            if part_data.carrier_id:
                res['value']['carrier_id'] = part_data.carrier_id.id

        return res

    def action_ship_create(self, cr, uid, ids, context=None):
        stock_picking_obj = self.pool.get('stock.picking')
        super(sale_order_delivery_makeover, self).action_ship_create(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            for t_picking in order.picking_ids:
                t_carrier_id = None
                t_incoterm_id = None
                t_delivery_methods = None
                if order.carrier_id:
                    t_carrier_id = order.carrier_id.id
                if order.incoterm:
                    t_incoterm_id = order.incoterm.id
                if order.delivery_methods:
                    t_delivery_methods = order.delivery_methods
                stock_picking_obj.write(cr, uid,
                                        [t_picking.id],
                                        {'carrier_id': t_carrier_id,
                                         'delivery_methods': t_delivery_methods,
                                         'incoterm_id': t_incoterm_id,
                                         }, context=context)
