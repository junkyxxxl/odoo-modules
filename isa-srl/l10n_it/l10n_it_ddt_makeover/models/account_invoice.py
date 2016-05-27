# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line.document_reference_id')
    def _is_shipping_invoice(self):
        self.is_shipping_invoice = False
        for t_line_data in self.invoice_line:
            if t_line_data.document_reference_id and t_line_data.document_reference_id.use_shipping_invoice:
                self.is_shipping_invoice = True
                break

    picking_ids = fields.One2many('stock.picking','shipping_invoice_id', 'Origine Picking', readonly=True)
    ddt_ids = fields.One2many('stock.ddt', 'invoice_id', 'Origine DDT', readonly=True)
    is_shipping_invoice = fields.Boolean(compute=_is_shipping_invoice, store=True, string="E' Fattura Accompagnatoria")
    # recupera i dati della fattura accompagnatoria se presenti
    shipping_invoice_number_of_packages = fields.Integer(string="Numero Colli")
    shipping_invoice_min_date = fields.Datetime(string="Inizio Trasferimento")
    shipping_invoice_delivery_methods = fields.Char(string="Trasporto a Cura")
    shipping_invoice_carrier_id = fields.Many2one('delivery.carrier', string="Trasportatore")
    shipping_invoice_weight = fields.Float(string="Peso")
    shipping_invoice_weight_net = fields.Float(string="Peso Netto")
    shipping_invoice_incoterm_id = fields.Many2one('stock.incoterms', string="Condizioni di Consegna")
    shipping_invoice_goods_description = fields.Many2one('stock.picking.goods_description', string="Aspetto dei Beni")
    shipping_partner_id = fields.Many2one('res.partner', string='Delivery Address')
    shipping_invoice_picking_type_id = fields.Char(string="Causale Trasporto")

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        pick_obj = self.pool.get('stock.picking')
        
        invoices = self.browse(cr, uid, ids, context=context)
        for t_invoice in invoices:
            for pick_id in t_invoice.picking_ids:
                if pick_id.invoice_state == 'invoiced':
                    pick_obj.write(cr, uid, pick_id.id, {'invoice_state':'2binvoiced'})                
            for ddt_id in t_invoice.ddt_ids:
                for pick_id in ddt_id.picking_ids:
                    if pick_id.invoice_state == 'invoiced':
                        pick_obj.write(cr, uid, pick_id.id, {'invoice_state':'2binvoiced'})
                for pick_id in ddt_id.picking_ids_return:
                    if pick_id.invoice_state == 'invoiced':
                        pick_obj.write(cr, uid, pick_id.id, {'invoice_state':'2binvoiced'})

        return super(AccountInvoice, self).unlink(cr, uid, ids, context=context)