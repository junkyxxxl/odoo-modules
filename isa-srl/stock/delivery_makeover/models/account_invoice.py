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

from openerp.osv import fields, orm
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def _is_shipping_invoice(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = False
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.use_shipping_invoice:
                    res[t_invoice_data.id] = True
                    break
        return res

    def _is_ddt_invoice(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = False
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.use_ddt:
                    res[t_invoice_data.id] = True
                    break
        return res

    def _get_shipping_invoice_number_of_packages(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = 0
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.use_shipping_invoice:
                    res[t_invoice_data.id] = t_line_data.document_reference_id.number_of_packages
                    break
        return res

    def _get_shipping_invoice_min_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = None
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.use_shipping_invoice:
                    res[t_invoice_data.id] = t_line_data.document_reference_id.min_date
                    break
        return res

    def _get_shipping_invoice_delivery_methods(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = ''
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.use_shipping_invoice:
                    t_delivery_method = t_line_data.document_reference_id.delivery_methods
                    t_string = ''
                    if t_delivery_method == 'sender':
                        t_string = 'Mittente'
                    if t_delivery_method == 'receiver':
                        t_string = 'Destinatario'
                    if t_delivery_method == 'carrier':
                        t_string = 'Vettore'
                    res[t_invoice_data.id] = t_string
                    break
        return res

    def _get_shipping_invoice_carrier(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = None
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.use_shipping_invoice:
                    res[t_invoice_data.id] = t_line_data.document_reference_id.carrier_id and t_line_data.document_reference_id.carrier_id.id or None
                    break
        return res

    def _get_shipping_invoice_weight(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = 0.0
            t_weight = 0.0
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.weight:
                    t_weight = t_weight + t_line_data.document_reference_id.weight
            res[t_invoice_data.id] = t_weight
        return res

    def _get_shipping_invoice_weight_net(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = 0.0
            t_weight = 0.0
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.weight_net:
                    t_weight = t_weight + t_line_data.document_reference_id.weight_net
            res[t_invoice_data.id] = t_weight
        return res

    def _get_shipping_invoice_incoterm(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = None
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.use_shipping_invoice:
                    res[t_invoice_data.id] = t_line_data.document_reference_id.incoterm_id and t_line_data.document_reference_id.incoterm_id.id or None
                    break
        return res

    def _get_shipping_invoice_picking_type(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_invoice_data in self.browse(cr, uid, ids, context):
            res[t_invoice_data.id] = ''
            for t_line_data in t_invoice_data.invoice_line:
                if t_line_data.document_reference_id and t_line_data.document_reference_id.picking_type_id:
                    res[t_invoice_data.id] = t_line_data.document_reference_id.picking_type_id.name
                    break
        return res

    _columns = {
        'is_shipping_invoice': fields.function(_is_shipping_invoice,
                                   type="boolean",
                                   string="E' Fattura Accompagnatoria"),
        'is_ddt_invoice': fields.function(_is_ddt_invoice,
                                   type="boolean",
                                   string="E' Fattura Differita"),                
        # recupera i dati della fattura accompagnatoria se presenti
        'shipping_invoice_number_of_packages': fields.function(_get_shipping_invoice_number_of_packages,
                                   type="integer",
                                   string="Numero Colli"),
        'shipping_invoice_min_date': fields.function(_get_shipping_invoice_min_date,
                                   type="date",
                                   string="Inizio Trasferimento"),
        'shipping_invoice_delivery_methods': fields.function(_get_shipping_invoice_delivery_methods,
                                   type="char",
                                   string="Trasporto a Cura"),
        'shipping_invoice_carrier_id': fields.function(_get_shipping_invoice_carrier,
                                   type="many2one",
                                   relation='delivery.carrier',
                                   string="Trasportatore"),
        'shipping_invoice_weight': fields.function(_get_shipping_invoice_weight,
                                   type="float",
                                   string="Peso"),
        'shipping_invoice_weight_net': fields.function(_get_shipping_invoice_weight_net,
                                   type="float",
                                   string="Peso Netto"),
        'shipping_invoice_incoterm_id': fields.function(_get_shipping_invoice_incoterm,
                                   type="many2one",
                                   relation='stock.incoterms',
                                   string="Condizioni di Consegna"),
        'shipping_invoice_picking_type_id': fields.function(_get_shipping_invoice_picking_type,
                                   type="char",
                                   string="Causale Trasporto"),
    }
