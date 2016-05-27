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

from openerp.osv import orm
from openerp.tools.translate import _


class stock_return_picking(orm.TransientModel):

    _inherit = "stock.return.picking"

    def create_returns(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ctx = context.copy()
        t_list = []
        t_act_id = None
        active_model = context.get('active_model', 'stock.picking')
        if active_model == 'stock.picking.ddt':
            t_active_ids = context.get('active_ids',[])
            t_active_id = context.get('active_id', None)
            ddt_obj = self.pool.get('stock.picking.ddt')
            for ddt_data in ddt_obj.browse(cr, uid, t_active_ids, context=context):
                if ddt_data.picking_id:
                    t_list.append(ddt_data.picking_id.id)
            if t_active_id:
                t_active_data = ddt_obj.browse(cr, uid, t_active_id, context=context)
                if t_active_data and t_active_data.picking_id:
                    t_act_id = t_active_data.picking_id.id
            ctx.update({'active_ids': t_list,
                        'active_id': t_act_id,
                        'active_model': 'stock.picking',
                        })

        res = super(stock_return_picking, self).create_returns(cr, uid, ids, context=ctx)

        return res

    def default_get(self, cr, uid, fields, context=None):
        context = dict(context or {})
        ctx = context.copy()
        t_list = []
        t_act_id = None
        active_model = context.get('active_model', 'stock.picking')
        if active_model == 'stock.picking.ddt':
            t_active_ids = context.get('active_ids',[])
            t_active_id = context.get('active_id', None)
            ddt_obj = self.pool.get('stock.picking.ddt')
            for ddt_data in ddt_obj.browse(cr, uid, t_active_ids, context=context):
                if ddt_data.picking_id:
                    t_list.append(ddt_data.picking_id.id)
            if t_active_id:
                t_active_data = ddt_obj.browse(cr, uid, t_active_id, context=context)
                if t_active_data and t_active_data.picking_id:
                    t_act_id = t_active_data.picking_id.id
            ctx.update({'active_ids': t_list,
                        'active_id': t_act_id,
                        'active_model': 'stock.picking',
                        })

        res = super(stock_return_picking, self).default_get(cr, uid, fields, context=ctx)

        return res
