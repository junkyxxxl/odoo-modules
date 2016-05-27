# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Abstract (http://www.abstract.it)
#    Copyright (C) 2014 Agile Business Group (http://www.agilebg.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import logging
_logger = logging.getLogger(__name__)
import datetime

class MyError(Exception):
    pass

class DdTCreateInvoice(models.TransientModel):

    _inherit = "ddt.create.invoice"
    
    def _get_journal(self):
        journal_type = self._get_journal_type()
        company_id = self.pool.get('res.users').browse(self._cr, self._uid, self._uid, context=self._context).company_id
        cmp_id = company_id.id        
        
        if journal_type == 'sale':
            if company_id.sale_journal_default:
                return company_id.sale_journal_default
            else:
                return self.env['account.journal'].search([('type','=','sale'),('company_id','=', cmp_id)], limit=1)
        
        if journal_type == 'purchase':
            if company_id.purchase_journal_default:
                return company_id.purchase_journal_default
            else:
                return self.env['account.journal'].search([('type','=','purchase'),('company_id','=', cmp_id)], limit=1)

            
        if journal_type == 'sale_refund':
            if company_id.sale_refund_journal_default:
                return company_id.sale_refund_journal_default     
            else:
                return self.env['account.journal'].search([('type','=','sale_refund'),('company_id','=', cmp_id)], limit=1)

            
        if journal_type == 'purchase_refund':
            if company_id.purchase_refund_journal_default:
                return company_id.purchase_refund_journal_default
            else:
                return self.env['account.journal'].search([('type','=','purchase_refund'),('company_id','=', cmp_id)], limit=1)

        return None

    def _get_journal_type(self):
        res_ids = self.env.context['active_ids']
        ddt_obj = self.pool.get('stock.ddt')
        ddts = ddt_obj.browse(self._cr, self._uid, res_ids, context=self._context)
        vals = []
        pick = ddts[0] and ddts[0].picking_ids and ddts[0].picking_ids[0]
        if not pick or not pick.move_lines:
            return 'sale'
        src_usage = pick.move_lines[0].location_id.usage
        dest_usage = pick.move_lines[0].location_dest_id.usage
        type = pick.picking_type_id.code
        if type == 'outgoing' and dest_usage == 'supplier':
            journal_type = 'purchase_refund'
        elif type == 'outgoing' and dest_usage == 'customer':
            journal_type = 'sale'
        elif type == 'incoming' and src_usage == 'supplier':
            journal_type = 'purchase'
        elif type == 'incoming' and src_usage == 'customer':
            journal_type = 'sale_refund'
        else:
            journal_type = 'sale'
        return journal_type

    journal_id = fields.Many2one('account.journal', 'Journal', required=True, default=_get_journal)
    journal_type = fields.Selection([('purchase_refund', 'Refund Purchase'), ('purchase', 'Create Supplier Invoice'), ('sale_refund', 'Refund Sale'), ('sale', 'Create Customer Invoice')], 'Journal Type', default=_get_journal_type, readonly=True)
    group_by_delivery_address = fields.Boolean('Separate By Delivery Address', default=True)

    def check_ddt_data(self, ddts):
        # carriage_condition_id = False
        # goods_description_id = False
        transportation_reason_id = False
        # transportation_method_id = False
        for ddt in ddts:
            '''
            if carriage_condition_id and ddt.carriage_condition_id.id != carriage_condition_id:
                raise Warning(_("Selected DDTs have different Carriage Conditions"))
            if not carriage_condition_id and ddt.carriage_condition_id:
                carriage_condition_id = ddt.carriage_condition_id.id
                
            if goods_description_id and ddt.goods_description_id.id != goods_description_id:
                raise Warning(_("Selected DDTs have different Descriptions of Goods"))
            if not goods_description_id and ddt.goods_description_id:
                goods_description_id = ddt.goods_description_id.id            
            '''
            if transportation_reason_id and ddt.transportation_reason_id.id != transportation_reason_id:
                raise Warning(_("Selected DDTs have different Reasons for Transportation"))
            if not transportation_reason_id and ddt.transportation_reason_id:
                transportation_reason_id = ddt.transportation_reason_id.id              
            '''
            if transportation_method_id and ddt.transportation_method_id.id != transportation_method_id:
                raise Warning(_("Selected DDTs have different Methods of Transportation"))
            if not transportation_method_id and ddt.transportation_method_id:
                transportation_method_id = ddt.transportation_method_id.id   
            '''

    @api.multi
    def create_invoice(self):
        ddt_model = self.env['stock.ddt']
        picking_pool = self.pool['stock.picking']
        ddts = ddt_model.browse(self.env.context['active_ids'])

        t_picking_dict = {} # raggruppamento per fatture
        t_picking_return_dict = {}

        invoice_list = []
        self.check_ddt_data(ddts)

        #Concateno alla data del filtro sulla fatturazione l'ora per prendere tutti i ddt di quel giorno
        to_date_time = False
        if self.date:
            to_date_time = datetime.datetime.combine(datetime.datetime.strptime(self.date,'%Y-%m-%d'),datetime.time(23, 59))
        try:
            for ddt in ddts:
                if to_date_time and datetime.datetime.strptime(ddt.date,'%Y-%m-%d %H:%M:%S') >= to_date_time:
                    if ddt.name:
                        raise MyError("La data del DDT n. %s è posteriore alla data di fatturazione!" % ddt.name.encode('utf-8'))
                    else:
                        raise MyError("La data del DDT è posteriore alla data di fatturazione!")
    
    
                if not ddt.ddt_lines:
                    raise MyError(_("Tutti i DDT selezionati devono avere almeno una riga!"))
    
                if ddt.invoice_id:
                    raise MyError(_("Il DDT %s è stato già fatturato!") % (ddt.name).encode('utf-8'))
                
                self._cr.execute('''    
                                    SELECT COUNT(*)
                                    FROM stock_picking AS pick
                                    WHERE pick.ddt_id = %s AND pick.use_shipping_invoice = TRUE
                                ''',(ddt.id,))
                ship_inv_count = self._cr.fetchall()
                if ship_inv_count and ship_inv_count[0][0] != 0:
                    raise MyError(_("Picking %s riservato per Fattura Accompagnatoria") % picking.name)
    
    
                self._cr.execute('''    
                                    SELECT COUNT (DISTINCT(pick.picking_type_id))
                                    FROM stock_picking AS pick
                                    WHERE pick.ddt_id = %s
                                ''',(ddt.id,))
                pick_type_count = self._cr.fetchall()
                if pick_type_count and pick_type_count[0][0] != 1:
                    raise MyError(_("I DDT selezionati sono di diverso tipo!"))
    
                self._cr.execute('''    
                                    SELECT COUNT(*)
                                    FROM stock_picking AS pick, stock_move AS move
                                    WHERE pick.ddt_id = %s AND move.picking_id = pick.id AND move.invoice_state != '2binvoiced'
                                ''',(ddt.id,))
                tobeinvoiced_count = self._cr.fetchall()
                if tobeinvoiced_count and tobeinvoiced_count[0][0] != 0:
                    raise MyError(_("DDT %s contains at least one move that is not invoiceable") % ddt.name.encode('utf-8'))

    
                self._cr.execute('''    
                                    SELECT COUNT(DISTINCT(move.company_id)), move.company_id
                                    FROM stock_picking AS pick, stock_move AS move
                                    WHERE pick.ddt_id = %s AND move.picking_id = pick.id
                                    GROUP BY move.company_id
                                ''',(ddt.id,))
                company_count = self._cr.fetchall()
                if company_count and company_count[0][0] != 1:
                    raise MyError(_("I DDT selezionati hanno il riferimento a movimenti di magazzino che appartengono a Company diverse!"))
    
    
                # struttura dati per raggruppamento
                t_partner_id = (ddt.partner_id and ddt.partner_id.id) or 0
                t_payment_term = (ddt.payment_term and ddt.payment_term.id) or 0
                t_user_id = (ddt.user_id and ddt.user_id.id) or 0
                t_company_id = company_count[0][1] or 0
                if not self.group_by_delivery_address:
                    key = (t_partner_id, t_payment_term, t_user_id, t_company_id)
                else:
                    t_delivery_address = (ddt.delivery_address_id and ddt.delivery_address_id.id) or 0
                    key = (t_partner_id, t_payment_term, t_user_id, t_company_id, t_delivery_address)
    
                if key not in t_picking_dict:
                    t_picking_dict[key] = {}
                if ddt.id not in t_picking_dict[key]:
                    t_picking_dict[key][ddt.id] = []
                for picking in ddt.picking_ids:
                    t_picking_dict[key][ddt.id].append(picking.id)
                for picking in ddt.picking_ids_return:
                    if picking.invoice_state == "2binvoiced":
                        t_picking_dict[key][ddt.id].append(picking.id)                   
    
                if key not in t_picking_return_dict:
                    t_picking_return_dict[key] = {}
                if ddt.id not in t_picking_return_dict[key]:
                    t_picking_return_dict[key][ddt.id] = []                
                for picking in ddt.picking_ids_return:
                    if picking.invoice_state == "2binvoiced":
                        t_picking_return_dict[key][ddt.id].append(picking.id)    

        except MyError as e:
            raise Warning(e)                        
        finally:
            pass    

        for t_key in t_picking_dict:
            ddt_list = []
            pick_list = []
            parcels = 0
            for ddt_id in t_picking_dict[t_key]:
                ddt_list.append(ddt_id)
                for pick_id in t_picking_dict[t_key][ddt_id]:
                    pick_list.append(pick_id)
                    parcels += self.env['stock.picking'].browse(pick_id).number_of_packages

            ddt_return_list = []
            pick_return_list = []
            for ddt_id in t_picking_return_dict[t_key]:
                ddt_return_list.append(ddt_id)
                for pick_id in t_picking_return_dict[t_key][ddt_id]:
                    pick_return_list.append(pick_id)
                    
            # creazione fatture
            
            ctx = {}
            if self._context:
                for item in self._context.items():
                    ctx[item[0]] = item[1]
            ctx.update({'picking_return': pick_return_list})
            ctx.update({'date_inv' : self.date})
            ctx.update({'inv_type': 'out_invoice'})
            ctx.update({'date_reg': self.date})            
            ctx.update({'carriage_condition_id': ddts[0].carriage_condition_id.id})
            ctx.update({'goods_description_id': ddts[0].goods_description_id.id})
            ctx.update({'transportation_reason_id': ddts[0].transportation_reason_id.id})
            ctx.update({'transportation_method_id': ddts[0].transportation_method_id.id})
            ctx.update({'payment_term':t_key[1]})
            ctx.update({'parcels': parcels})
            
            if self.group_by_delivery_address:
                ctx.update({'shipping_partner_id': t_key[4]})
            else:
                ctx.update({'shipping_partner_id': t_key[0]})
            
            invoices = picking_pool.action_invoice_create(self.env.cr, self.env.uid, pick_list, self.journal_id.id, group=True, context=ctx)
            if len(invoices) != 1:
                raise Warning(_("Errore nel raggruppamento delle fatture!"))

            # nel ddt aggiungo il riferimento alla fattura creata
            ddt_data = self.env['stock.ddt'].browse(ddt_list)
            ddt_data.write({'invoice_id': invoices[0],})


            invoice_list += invoices

        '''
        self.pool.get('account.invoice').write(self.env.cr, self.env.uid, invoice_list, {
            'carriage_condition_id': ddts[0].carriage_condition_id.id,
            'goods_description_id': ddts[0].goods_description_id.id,
            'transportation_reason_id': ddts[0].transportation_reason_id.id,
            'transportation_method_id': ddts[0].transportation_method_id.id,
            })
        '''

        mod_obj = self.env['ir.model.data']

        search_view_res = mod_obj.get_object_reference('account', 'view_account_invoice_filter')
        search_view_id = search_view_res and search_view_res[1] or False

        form_view_res = mod_obj.get_object_reference('account', 'invoice_form')
        form_view_id = form_view_res and form_view_res[1] or False

        return  {
            'domain': [('id', 'in', invoice_list)],
            'name': 'Fatture da DDT',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'views': [(False, 'tree'), (form_view_id, 'form')],
            'search_view_id': search_view_id,
        }
