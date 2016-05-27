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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class stock_invoice_onshipping_ddt(orm.TransientModel):

    _inherit = "stock.invoice.onshipping"

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}

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

        res = super(stock_invoice_onshipping_ddt, self).view_init(cr, uid, fields_list, context=ctx)

        return res

    def create_invoice(self, cr, uid, ids, context=None):
        context = dict(context or {})
        data = self.browse(cr, uid, ids[0], context=context)
        context['date_reg'] = data.invoice_date                
        ctx = context.copy()
        t_list = []
        t_act_id = None
        active_model = context.get('active_model', 'stock.picking')
        if active_model == 'stock.picking.ddt':
            t_active_ids = context.get('active_ids',[])
            t_active_id = context.get('active_id', None)
            ddt_obj = self.pool.get('stock.picking.ddt')
            for ddt_data in ddt_obj.browse(cr, uid, t_active_ids, context=context):
                if ddt_data.flag_partial_transfer == 'S':
                    raise orm.except_orm(_('Error'),
                                         _('Impossibile fatturare un DDT stornato!'))
                for t_pick_data in ddt_data.picking_ids:
                    t_list.append(t_pick_data.id)
            if t_active_id:
                t_active_data = ddt_obj.browse(cr, uid, t_active_id, context=context)
                if t_active_data and t_active_data.picking_id:
                    t_act_id = t_active_data.picking_id.id
            ctx.update({'active_ids': t_list,
                        'active_id': t_act_id,
                        'active_model': 'stock.picking',
                        'inv_type': 'out_invoice',
                        })

        res = super(stock_invoice_onshipping_ddt, self).create_invoice(cr, uid, ids, context=ctx)

        return res

    def _get_journal_type(self, cr, uid, context=None):
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

        res = super(stock_invoice_onshipping_ddt, self)._get_journal_type(cr, uid, context=ctx)

        return res

    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        context = dict(context or {})
        ctx = context.copy()        
        active_model = context.get('active_model', 'stock.picking')
        if active_model == 'stock.picking.ddt':
            ddt_obj = self.pool.get('stock.picking.ddt')
            ddt_data = ddt_obj.browse(cr, uid, context['active_id'],context=ctx)
            t_act_id = ddt_data.picking_id.id
            ctx.update({'active_id': t_act_id,
                        'active_model': 'stock.picking',
                        })                        
        return super(stock_invoice_onshipping_ddt, self).onchange_journal_id(cr, uid, ids, journal_id, context=ctx)

    _columns = {
        'journal_type': fields.selection([('purchase_refund', 'Refund Purchase'), ('purchase', 'Create Supplier Invoice'), 
                                          ('sale_refund', 'Refund Sale'), ('sale', 'Create Customer Invoice')], 'Journal Type', readonly=True),
    }

    _defaults = {
        'journal_type': _get_journal_type,
    }
