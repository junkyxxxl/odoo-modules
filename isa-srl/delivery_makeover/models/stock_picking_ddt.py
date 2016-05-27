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
from openerp.exceptions import except_orm
import openerp.addons.decimal_precision as dp


class stock_picking_ddt(orm.Model):

    _name = "stock.picking.ddt"
    _inherit = ['mail.thread']

    # TODO rimuovere
    _inherits = {'stock.picking': 'picking_id'}

    _description = "DDT"
    _rec_name = 'ddt_number'

    def _default_picking_type_id(self, cr, uid, context=None):
        context = context or {}
        # TODO spostarlo nella create?
        t_picking_type_ids = self.pool.get('stock.picking.type').search(cr, uid, [('code', '=', 'outgoing')])
        if t_picking_type_ids:
            return t_picking_type_ids[0]
        return False

    def _get_picking_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        # TODO rimuovere
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = self.pool.get('stock.picking').search(cr, uid, [('ddt_id', '=', data.id)], context=context)
        return res

    def _get_picking_back_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = self.pool.get('stock.picking').search(cr, uid, ['&',('ddt_id', '=', data.id),('id', '!=', data.picking_id.id)], context=context)
        return res

    def _has_picking_back(self, cr, uid, ids, name, args, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            pick_ids = self.pool.get('stock.picking').search(cr, uid, ['&',('ddt_id', '=', data.id),('id', '!=', data.picking_id.id)], context=context)
            res[data.id] = False
            if pick_ids:
                res[data.id] = True
        return res

    def _get_flag_partial_transfer(self, cr, uid, ids, name, args, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = 'N'
            if len(data.picking_ids.ids) == 2:
                t_count0 = 0
                t_count1 = 0
                for t_line in data.picking_ids[0].move_lines:
                    t_count0 += t_line.product_uom_qty
                for t_line in data.picking_ids[1].move_lines:
                    t_count1 += t_line.product_uom_qty
                res[data.id] = 'P'
                if t_count0 == t_count1:
                    res[data.id] = 'S'
        return res

    def _get_partial_transfer_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = []
            if data.flag_partial_transfer == 'P':
                t_id0 = data.picking_ids.ids[0]
                t_id1 = data.picking_ids.ids[1]
                t_num = 0
                if t_id1 > t_id0:
                    t_num = 1
                res[data.id] = data.picking_ids[t_num].move_lines.ids
        return res


    def _get_move_ddt(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            if line.picking_id.ddt_id:
                result[line.picking_id.ddt_id.id] = True
        return result.keys()

    def _get_picking_ddt(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.picking').browse(cr, uid, ids, context=context):
            if line.ddt_id:
                result[line.ddt_id.id] = True
        return result.keys()

    def _get_total_value(self, cr, uid, ids, field_name, arg, context=None):
        r = {}
        for id in ids:
            tot = 0.0
            ddt = self.browse(cr, uid, id)
            for ddt_line in ddt.move_lines:
                if ddt_line.procurement_id and ddt_line.procurement_id.sale_line_id:
                    line = ddt_line.procurement_id.sale_line_id
                    tot += line.price_subtotal * (ddt_line.product_uom_qty / line.product_uom_qty)                 
            for ddt_line in ddt.partial_transfer_ids:
                if ddt_line.procurement_id and ddt_line.procurement_id.sale_line_id:
                    line = ddt_line.procurement_id.sale_line_id
                    tot -= line.price_subtotal * (ddt_line.product_uom_qty / line.product_uom_qty)                                
            r[id] = tot
        return r

    _columns = {
        'goods_appearance_id': fields.many2one('stock.picking.goods.appearance',
                                               'Goods appearance',
                                               help=" Reference to Stock Goods Appearance"),
        'delivery_date': fields.datetime('Delivery Date',
                                         help="Delivery date",
                                         select=True,
                                         states={'cancel':[('readonly', True)]}),
        # TODO rimuovere? convertire in function?
        'picking_id': fields.many2one('stock.picking',
                                      'Ordine di Consegna',
                                      required=True,
                                      ondelete="cascade"),
        # TODO diventa una one2many
        'picking_ids': fields.function(_get_picking_ids,
                                       method=True,
                                       type='one2many',
                                       relation='stock.picking',
                                       string='Picking associated to this ddt'),
        'picking_back_ids': fields.function(_get_picking_back_ids,
                                            method=True,
                                            type='one2many',
                                            relation='stock.picking',
                                            string='Inverse Picking associated to this ddt'),
        'has_picking_back': fields.function(_has_picking_back,
                                            method=True,
                                            type='boolean',
                                            string='Has Inverse Picking associated to this ddt'),
        'flag_partial_transfer': fields.function(_get_flag_partial_transfer,
                                                 type='selection',
                                                 selection=[('N', ''),
                                                            ('P', 'Parzialmente Stornato'),
                                                            ('S', 'Stornato')],
                                                 string='Storno',
                                                 readonly=True,
                                                 method=True,
                                                 select=1),
        'partial_transfer_ids': fields.function(_get_partial_transfer_ids,
                                                type="one2many",
                                                obj='stock.move',
                                                string="Prodotti Stornati"),

        'ddt_number':  fields.char('DDT', size=64,
                                   help="DDT number",
                                   select=True,
                                   states={'cancel':[('readonly', True)]}),
        'ddt_date':  fields.date('DDT date',
                                 help="DDT date",
                                 select=True,
                                 states={'cancel':[('readonly', True)]}),
        'total_value': fields.function(_get_total_value, copy=False, type="float", digits_compute=dp.get_precision('Account'), string='Quantità Totale',
            store= #False
            {
                   'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines','state'], 10),
                   'stock.move': (_get_move_ddt, ['product_uom_qty','picking_id'], 10),
                   'stock.picking': (_get_picking_ddt, ['state','ddt_id'], 10),
            }
            ),    

        # TODO aggiungere
        # company_id
        # partner_id
        # picking_id????
        # invoice_state
        # origin
        # move_lines
        # pack_operation_exist
        # note
        # pack_operation_ids
        # state = fields.Selection( [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
    }

    _defaults = {
        'delivery_date': fields.datetime.now,
        'ddt_date': fields.date.context_today,
        # TODO rimuovere
        'picking_type_id': _default_picking_type_id,
    }

    def onchange_partner_in(self, cr, uid, ids, partner_id=None, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        return {}

    def onchange_ddt_date(self, cr, uid, ids, delivery_date, ddt_date, context=None):
        v = {}
        result = {'value':v}

        v['ddt_date'] = ddt_date
        if ddt_date > delivery_date:
            v['ddt_date'] = delivery_date 

        return result

    def create(self, cr, uid, vals, context=None):
        t_picking_type_obj = self.pool.get('stock.picking.type')
        # TODO non serve più passare il picking_type_id, modificarlo per:
        # 1) controllare il picking_type_id dei picking, se già definiti
        # 2) impostare il default, vedi: _default_picking_type_id dei picking, se creati contestualmente
        t_picking_type_ids = t_picking_type_obj.search(cr, uid, [('code', '=', 'outgoing')])
        if t_picking_type_ids:
            for i in range(0,len(t_picking_type_ids)):
                id = t_picking_type_ids[i]
                temp = t_picking_type_obj.browse(cr, uid, id, context)
                location = self.pool.get('stock.location').browse(cr, uid, temp.default_location_src_id.id, context)
                if 'company_id' in vals and vals['company_id']:
                    if location and location.company_id:
                        if location.company_id.id != vals['company_id']:
                            del t_picking_type_ids[i]
                    else:
                        del t_picking_type_ids[i]
        if t_picking_type_ids:
            vals['picking_type_id'] = t_picking_type_ids[0]
        else:
            raise except_orm(_('Error!'),_('Impossible to retrieve a valid picking type id for this company'))

        # TODO va nel picking
        vals['use_ddt'] = True

        new_id = super(stock_picking_ddt, self).create(cr, uid, vals, context)
        obj_browse = self.browse(cr, uid, new_id)
        if obj_browse.picking_id:
            picking_obj = self.pool.get('stock.picking')
            # TODO passare il flag use_ddt
            picking_obj.write(cr, uid, [obj_browse.picking_id.id], {'ddt_id':new_id}, context=context)
        return new_id

    def action_confirm(self, cr, uid, ids, context=None):
        context = context or {}
        t_picking_id = None
        res = None
        t_picking_ddt_data = self.browse(cr, uid, ids, context)
        if t_picking_ddt_data and t_picking_ddt_data.picking_id:
            t_picking_id = t_picking_ddt_data.picking_id.id
            t_picking_obj = self.pool.get('stock.picking')
            t_picking_data = t_picking_obj.browse(cr, uid, t_picking_id, context)
            if not t_picking_data.move_lines:
                raise orm.except_orm(_('Error'),
                                     _('Mancano i Prodotti!'))
            res = t_picking_obj.action_confirm(cr, uid, [t_picking_id], context)
            if res:
                res = self.force_assign(cr, uid, ids, context)
                if res:
                    res = self.do_transfer_ddt(cr, uid, ids, context)
                    if res:
                        # TODO
                        res = t_picking_obj.write(cr, uid, [t_picking_id], {'invoice_state': '2binvoiced'}, context=context)

        return res

    # TODO rimuovere?
    def action_assign(self, cr, uid, ids, context=None):
        context = context or {}
        t_picking_id = None
        res = None
        t_picking_ddt_data = self.browse(cr, uid, ids, context)
        if t_picking_ddt_data and t_picking_ddt_data.picking_id:
            t_picking_id = t_picking_ddt_data.picking_id.id
            t_picking_obj = self.pool.get('stock.picking')
            res = t_picking_obj.action_assign(cr, uid, [t_picking_id], context)
        return res

    # TODO rimuovere?
    def force_assign(self, cr, uid, ids, context=None):
        context = context or {}
        t_picking_id = None
        res = None
        t_picking_ddt_data = self.browse(cr, uid, ids, context)
        if t_picking_ddt_data and t_picking_ddt_data.picking_id:
            t_picking_id = t_picking_ddt_data.picking_id.id
            t_picking_obj = self.pool.get('stock.picking')
            res = t_picking_obj.force_assign(cr, uid, [t_picking_id], context)
        return res

    # TODO rimuovere?
    def action_cancel(self, cr, uid, ids, context=None):
        context = context or {}
        t_picking_id = None
        res = None
        t_picking_ddt_data = self.browse(cr, uid, ids, context)
        if t_picking_ddt_data and t_picking_ddt_data.picking_id:
            t_picking_id = t_picking_ddt_data.picking_id.id
            t_picking_obj = self.pool.get('stock.picking')
            res = t_picking_obj.action_cancel(cr, uid, [t_picking_id], context)
        return res

    # TODO rimuovere?
    def do_transfer_ddt(self, cr, uid, ids, context=None):
        context = context or {}
        t_picking_id = None
        res = None
        t_picking_ddt_data = self.browse(cr, uid, ids, context)
        if t_picking_ddt_data and t_picking_ddt_data.picking_id:
            t_picking_id = t_picking_ddt_data.picking_id.id
            t_picking_obj = self.pool.get('stock.picking')
            res = t_picking_obj.do_transfer(cr, uid, [t_picking_id], context)
        return res

    # TODO rimuovere?
    def do_unreserve(self, cr, uid, ids, context=None):
        context = context or {}
        t_picking_id = None
        res = None
        t_picking_ddt_data = self.browse(cr, uid, ids, context)
        if t_picking_ddt_data and t_picking_ddt_data.picking_id:
            t_picking_id = t_picking_ddt_data.picking_id.id
            t_picking_obj = self.pool.get('stock.picking')
            res = t_picking_obj.do_unreserve(cr, uid, [t_picking_id], context)
        return res
