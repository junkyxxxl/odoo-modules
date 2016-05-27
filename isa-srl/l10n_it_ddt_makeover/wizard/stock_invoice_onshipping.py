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
from openerp.exceptions import Warning


class stock_invoice_onshipping_ddt(orm.TransientModel):

    _inherit = "stock.invoice.onshipping"

    def create_invoice(self, cr, uid, ids, context=None):
        
        context = dict(context or {})
        picking_pool = self.pool.get('stock.picking')
        data = self.browse(cr, uid, ids[0], context=context)
        context['date_reg'] = data.invoice_date         
        journal2type = {'sale':'out_invoice', 'purchase':'in_invoice', 'sale_refund':'out_refund', 'purchase_refund':'in_refund'}
        context['date_inv'] = data.invoice_date
        acc_journal = self.pool.get("account.journal")
        inv_type = journal2type.get(data.journal_type) or 'out_invoice'
        context['inv_type'] = inv_type

        t_picking_dict = {} # raggruppamento per fatture
        t_picking_return_dict = {}

        invoice_list = []

        picking_ids = picking_pool.browse(cr, uid, context['active_ids'], context=context)

        for picking in picking_ids:

            # controllo fatturabilità
            for move in picking.move_lines:
                if move.invoice_state != "2binvoiced":
                    raise Warning(
                        _("Move %s is not invoiceable") % move.name)
            
            picking_pool.write(cr, uid, picking.id, {'use_shipping_invoice':True})
            
            # struttura dati per raggruppamento
            t_partner_id = picking.partner_id and picking.partner_id.id or 0
            t_company_id = (picking.company_id and picking.company_id.id) or 0
            t_transportation_method = (picking.delivery_methods and picking.delivery_methods.name) or ''
            t_carrier_id = (picking.carrier_id and picking.carrier_id.id) or 0
            t_incoterm_id = (picking.incoterm_id and picking.incoterm_id.id) or 0
            t_picking_type = (picking.picking_type_id and picking.picking_type_id.name) or ''
            t_goods_description_id = (picking.sale_id and picking.sale_id.goods_description_id and picking.sale_id.goods_description_id.id) or 0
            key = (t_partner_id, t_company_id, t_transportation_method, t_carrier_id, t_incoterm_id, t_picking_type, t_goods_description_id)

            if key not in t_picking_dict:
                t_picking_dict[key] = []
            t_picking_dict[key].append(picking.id)
            for ret_picking in picking.inv_picking_ids:
                if ret_picking.invoice_state == "2binvoiced":
                    t_picking_dict[key].append(ret_picking.id)                   
                
    
            if key not in t_picking_return_dict:
                t_picking_return_dict[key] = []          
            for ret_picking in picking.inv_picking_ids:
                if ret_picking.invoice_state == "2binvoiced":
                    t_picking_return_dict[key].append(ret_picking.id) 

        for t_key in t_picking_dict:
            pick_list = []
            for pick_id in t_picking_dict[t_key]:
                pick_list.append(pick_id)

            pick_return_list = []
            for pick_id in t_picking_return_dict[t_key]:
                pick_return_list.append(pick_id)
                    
            # creazione fatture
            
            ctx = {}
            if context:
                for item in context.items():
                    ctx[item[0]] = item[1]
            ctx.update({'picking_return': pick_return_list})
            
            invoices = picking_pool.action_invoice_create(cr, uid, pick_list, journal_id = data.journal_id.id, group = data.group, type = inv_type, context=ctx)
            vals = {
                    'shipping_invoice_delivery_methods': key[2],
                    'shipping_invoice_carrier_id': key[3],
                    'shipping_invoice_incoterm_id': key[4],
                    'shipping_invoice_picking_type_id': key[5],
                    'shipping_invoice_goods_description': key[6],
            }
            account_obj = self.pool.get('account.invoice')
            account_obj.write(cr, uid, invoices, vals, context=context)
            
            #SCRITTURA shipping_invoice_id SU TUTTI I PICKING
            for id in pick_list:
                if len(invoices) == 1:
                    self.pool.get('stock.picking').write(cr, uid, id, {'shipping_invoice_id':invoices[0]})
                else:
                    check = False
                    for invoice in self.pool.get('account.invoice').browse(cr, uid, invoices, context):
                        for line in invoice.invoice_line:
                            if line.document_reference_id and line.document_reference_id.id == id:
                                self.pool.get('stock.picking').write(cr, uid, id, {'shipping_invoice_id':invoice.id})
                                check = True
                                break
                            if check:
                                break

            invoice_list += invoices
        
        return invoice_list
