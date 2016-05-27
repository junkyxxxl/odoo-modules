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

from openerp import api
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.exceptions import except_orm


class stock_picking_delivery_makeover(orm.Model):
    _name = "stock.picking"
    _inherit = 'stock.picking'
    _description = "Incoming Shipments ISA"

    def onchange_use_ddt(self, cr, uid, ids, use_ddt, context=None):
        if use_ddt:
            return {'value': {'use_shipping_invoice': False}
                    }
        return {}

    def onchange_use_shipping_invoice(self, cr, uid, ids, use_shipping_invoice, context=None):
        if use_shipping_invoice:
            return {'value': {'use_ddt': False}
                    }
        return {}

    _columns = {
        'use_ddt': fields.boolean('DDT',
                                  readonly=False,
                                  states={'cancel': [('readonly', True)],
                                          'done': [('readonly', True)]},),
        'use_shipping_invoice': fields.boolean('Fattura Accompagnatoria',
                                               readonly=False,
                                               states={'cancel': [('readonly', True)],
                                                       'done': [('readonly', True)]},),
        'ddt_id': fields.many2one('stock.picking.ddt',
                                  'Documento di Trasporto'),
        'incoterm_id': fields.many2one('stock.incoterms',
                                       'Condizione di Consegna',
                                       help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
        'delivery_methods': fields.selection([('sender', 'Sender '),
                                              ('receiver', 'Receiver'),
                                              ('carrier', 'Carrier')],
                                             'Trasporto a cura',
                                             select=True,
                                             translate=True),
        'supplier_ddt_number':  fields.char('DDT', size=64,
                                            help="DDT number",
                                            states={'cancel':[('readonly', True)]}),
        'supplier_ddt_date':  fields.date('DDT date',
                                          help="DDT date",
                                          states={'cancel':[('readonly', True)]}),
    }

    _defaults = {
        'delivery_methods': 'sender',
    }

    @api.cr_uid_ids_context
    def do_transfer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        picking_data = self.browse(cr, uid, ids)

        for obj_browse in picking_data:
            if obj_browse.use_shipping_invoice and obj_browse.picking_type_code == 'outgoing':
                self.write(cr, uid, obj_browse.id, {'invoice_state': '2binvoiced'}, context=context)

        res = super(stock_picking_delivery_makeover, self).do_transfer(cr, uid, [obj_browse.id], context)

        for obj_browse in picking_data:
            if obj_browse.use_ddt and obj_browse.picking_type_code in ['outgoing','internal']:
                tmp_picking_type = obj_browse.picking_type_id.id
                self.create_ddt(cr, uid, ids, context)
                self.write(cr, uid, obj_browse.id,{'picking_type_id':tmp_picking_type})

        return res

    def create_ddt(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        for picking_data in self.browse(cr, uid, ids):
            if picking_data.picking_type_id and picking_data.picking_type_id.code in ['outgoing','internal']:                
                if picking_data.state != 'done' and picking_data.backorder_id:
                    t_delivered_pick_id = picking_data.backorder_id.id
                    picking_data = self.browse(cr, uid, t_delivered_pick_id)

                if picking_data.picking_type_id:
                    obj_ir_seq = self.pool.get('ir.sequence')
                    if not picking_data.picking_type_id.ddt_sequence_id:
                        raise except_orm(_('Error !'), _('The sequence in stock picking type is not defined'))
                    t_cause_seq_id = picking_data.picking_type_id.ddt_sequence_id.id
                    number_next = obj_ir_seq.next_by_id(cr, uid, t_cause_seq_id, context)

                    ddt_obj = self.pool.get('stock.picking.ddt')
                    if not picking_data.ddt_id:
                        # TODO campi
                        new_ddt_id = ddt_obj.create(cr, uid,
                                                    {'ddt_number': number_next,
                                                     'picking_id': picking_data.id,
                                                     }, context=context)
                        self.write(cr, uid,
                                   picking_data.id,
                                   {'ddt_id': new_ddt_id},
                                   context=context)
                    else:
                        # TODO campi
                        ddt_obj.write(cr, uid, [picking_data.ddt_id.id],
                                              {'ddt_number':number_next}, context=context)

    def _write_invoice_lines_picking(self, cr, uid, ids, invoice_ids, context=None):
        if context is None:
            context = {}

        inv_line_obj = self.pool.get('account.invoice.line')
        picking_obj = self.pool.get('stock.picking')

        picking_ids = context.get('active_ids', [])
        picking_data = picking_obj.browse(cr, uid, picking_ids)
        for t_picking in picking_data:
            line_ids = inv_line_obj.search(cr, uid,
                               [('invoice_id', 'in', invoice_ids),
                                ('origin', 'like', t_picking.name)])
            for invoice_id in invoice_ids:
                line_ids = self.pool.get('account.invoice').browse(cr,uid,invoice_id).invoice_line

                for t_line in line_ids:
                    if t_line.origin == t_picking.name:
                        inv_line_obj.write(cr, uid, t_line.id,
                                           {'document_reference_id': t_picking.id})

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        if context is None:
            context = {}
        res = super(stock_picking_delivery_makeover, self)._get_invoice_vals(cr,uid,key,inv_type,journal_id,move,context=context)
        if res:
            res.update({'registration_date': context.get('date_reg', False)})
        return res

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        
        invoice_ids = super(stock_picking_delivery_makeover,
                            self).action_invoice_create(cr, uid,
                                                        ids, journal_id=journal_id,
                                                        group=group,
                                                        type=type, context=context)

        self._write_invoice_lines_picking(cr, uid, ids, invoice_ids, context=context)
        return invoice_ids
