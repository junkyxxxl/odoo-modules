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

from openerp import fields, models, api
from openerp.tools.translate import _
from openerp.exceptions import except_orm


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = 'stock.picking'
    _description = "Incoming Shipments ISA"

    shipping_invoice_id = fields.Many2one('account.invoice', string='Fattura Accompagnatoria')
    use_shipping_invoice = fields.Boolean('Fattura Accompagnatoria', readonly=False,)
    incoterm_id = fields.Many2one('stock.incoterms',
                                  'Condizione di Consegna',
                                  help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    delivery_methods = fields.Many2one('stock.picking.transportation_method', 
                                       'Trasporto a cura', 
                                       select=True)
    supplier_ddt_number = fields.Char('DDT', size=64,
                                      help="DDT number",
                                      states={'cancel':[('readonly', True)]})
    supplier_ddt_date = fields.Date('DDT date',
                                    help="DDT date",
                                    states={'cancel':[('readonly', True)]})

    @api.one
    def remove_picking_from_ddt(self):
        if self.ddt_id:
            if self.ddt_id.invoice_id:
                raise except_orm(_('Errore!'),
                                 _('Non puoi rimuovere picking da un DDT già fatturato!'))
            if self.number_of_packages:
                self.ddt_id.parcels -= self.number_of_packages               
            self.ddt_id = None

    @api.multi
    def do_transfer(self):
        if self.use_shipping_invoice and self.picking_type_code == 'outgoing':
            self.write({'invoice_state': '2binvoiced'})

        res = super(StockPicking, self).do_transfer()

        return res

    def _write_invoice_lines_picking(self, cr, uid, ids, invoice_ids, context=None):
        if context is None:
            context = {}

        inv_line_obj = self.pool.get('account.invoice.line')
        picking_obj = self.pool.get('stock.picking')

        picking_ids = ids
        if context.get('active_ids', []) and context.get('active_model', '') == 'stock.picking':
            picking_ids = context.get('active_ids', [])
        picking_data = picking_obj.browse(cr, uid, picking_ids)
        
        for t_picking in picking_data:
            # TODO da rivedere
#            line_ids = inv_line_obj.search(cr, uid,
#                               [('invoice_id', 'in', invoice_ids),
#                                ('origin', 'like', t_picking.name)])
            for invoice_id in invoice_ids:
                line_ids = self.pool.get('account.invoice').browse(cr,uid,invoice_id).invoice_line
    
                for t_line in line_ids:                    
                    if t_line.quantity >= 0:
                        if t_line.origin == t_picking.name:
                            inv_line_obj.write(cr, uid, t_line.id, {'document_reference_id': t_picking.id})
                    else:
                        if t_picking.ddt_id:   
                            for r_pick in t_picking.ddt_id.picking_ids_return:
                                if t_line.origin == r_pick.name and r_pick.origin and r_pick.origin == t_picking.name:
                                    inv_line_obj.write(cr, uid, t_line.id, {'document_reference_id': t_picking.id})
                        elif t_picking.inv_picking_ids:
                            for r_pick in t_picking.inv_picking_ids:
                                if t_line.origin == r_pick.name and r_pick.origin and r_pick.origin == t_picking.name:
                                    inv_line_obj.write(cr, uid, t_line.id, {'document_reference_id': t_picking.id})

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        if context is None:
            context = {}
        res = super(StockPicking, self)._get_invoice_vals(cr,uid,key,inv_type,journal_id,move,context=context)
        if res:
            res.update({
                        'registration_date': context.get('date_reg', False),
                        'carriage_condition_id': context.get('carriage_condition_id', False),
                        'goods_description_id': context.get('goods_description_id', False),
                        'transportation_reason_id': context.get('transportation_reason_id', False),
                        'transportation_method_id': context.get('transportation_method_id', False),
                        'parcels': context.get('parcels', 0),
                        'shipping_partner_id': context.get('shipping_partner_id', False),
                        })            
        
        return res

    @api.onchange('min_date')
    def onchange_min_date(self):
        if self.min_date:
            self.date_done = self.min_date

    @api.onchange('invoice_state')
    def onchange_invoice_state(self):
        if self.invoice_state == '2binvoiced':
            self.use_shipping_invoice = False
                                    
    def action_invoice_create(self, cr, uid, ids, journal_id=False, group=False, type='out_invoice', context=None):
        invoice_ids = super(StockPicking, self).action_invoice_create(cr, uid, ids, journal_id, group, type, context)
        self._write_invoice_lines_picking(cr, uid, ids, invoice_ids, context=context)
        return invoice_ids

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update(ddt_id=None)
        return super(StockPicking, self).copy(default)
