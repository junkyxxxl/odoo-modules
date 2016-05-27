# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#    Copyright (C) Francesco Apruzzese
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


from openerp import fields
from openerp import models
from openerp import api
from openerp import _
from openerp.exceptions import Warning


class DdTFromPickings(models.TransientModel):

    _inherit = "ddt.from.pickings"

    @api.multi
    def create_ddt(self):

        keys = {}
        for picking in self.picking_ids:
            
            partner = picking.partner_id or None
            if picking.sale_id:
                user_id = picking.sale_id.user_id.id or None
                parcel = picking.sale_id.parcels or picking.number_of_packages or None
                carriage_condition = picking.sale_id.carriage_condition_id or None
                good_description = picking.sale_id.goods_description_id or None
                transportation_reason = picking.sale_id.transportation_reason_id or None
                payment_term = picking.sale_id.payment_term or None
            else:
                user_id = 1
                parcel = None
                carriage_condition = None
                good_description = None
                transportation_reason = None
                payment_term = None
            picking_type = picking.picking_type_id or None
            carrier = picking.carrier_id or None
            incoterm = picking.incoterm_id or None
            
            
            key = (partner, parcel, carriage_condition, good_description, transportation_reason, payment_term, picking_type, carrier, incoterm, user_id)
            if key not in keys:
                keys.setdefault(key, [])
            keys[key].append(picking.id)    
        
        if len(keys) > 1:
            res = []
            for item in keys:        
                vals = (6,0,keys[item])
                tmp = self.pool.get('ddt.from.pickings').create(self._cr, self._uid, {'picking_ids': [(6,0,keys[item])]})
                t_res = self.pool.get('ddt.from.pickings').browse(self._cr, self._uid, tmp, context = self._context).create_ddt()
                res.append(t_res)
                
            return res

            
        
        t_type_list = []
        t_paym_list = []
        t_carr_list = []
        t_inco_list = []
        t_user_list = []
        t_comp_list = []
        transportation_method_id = False
        t_partner_id = None
        t_partner_invoice = None
        t_partner_shipping = None        
                
        for picking in self.picking_ids:
            t_partner_id = picking.partner_id and picking.partner_id.id or None
            if picking.ddt_id:
                raise Warning(
                    _("Picking %s already in ddt") % picking.name)
            if picking.use_shipping_invoice:
                raise Warning(
                    _("Picking %s riservato per fattura Accompagnatoria") % picking.name)


            if picking.sale_id and picking.sale_id.partner_invoice_id:
                if not t_partner_invoice:
                    t_partner_invoice = picking.sale_id.partner_invoice_id.id
                elif t_partner_invoice != picking.sale_id.partner_invoice_id.id:
                    raise Warning(_("Selected Pickings come from sale orders with different invoice address"))         
                           
            if picking.sale_id and picking.sale_id.partner_shipping_id:
                if not t_partner_shipping:
                    t_partner_shipping = picking.sale_id.partner_shipping_id.id
                elif t_partner_shipping != picking.sale_id.partner_shipping_id.id:
                    raise Warning(_("Selected Pickings come from sale orders with different shipping address"))                

            if picking.sale_id and picking.sale_id.user_id and picking.sale_id.user_id:
                t_usr = picking.sale_id.user_id.id
            else: 
                t_usr = 1
                
            if picking.picking_type_id and picking.picking_type_id.id not in t_type_list:
                t_type_list.append(picking.picking_type_id.id)
            if picking.sale_id and picking.sale_id.payment_term and picking.sale_id.payment_term.id not in t_paym_list:
                t_paym_list.append(picking.sale_id.payment_term.id)
            if picking.carrier_id and picking.carrier_id.id not in t_carr_list:
                t_carr_list.append(picking.carrier_id.id)                
            if picking.incoterm_id and picking.incoterm_id.id not in t_inco_list:
                t_inco_list.append(picking.incoterm_id.id)
            if t_usr not in t_user_list:
                t_user_list.append(t_usr)      
            if picking.company_id and picking.company_id.id not in t_comp_list:
                t_comp_list.append(picking.company_id.id)                         
                   
                     

            if picking.delivery_methods:
                if transportation_method_id and transportation_method_id != picking.delivery_methods.id:
                    raise Warning(_("Selected Pickings have different transportation reason"))
                transportation_method_id = picking.delivery_methods.id                  
            elif picking.sale_id and picking.sale_id.transportation_method_id:
                if transportation_method_id and transportation_method_id != picking.sale_id.transportation_method_id.id:
                    raise Warning(_("Selected Pickings have different transportation reason"))
                transportation_method_id = picking.sale_id.transportation_method_id.id

        if len(t_type_list) > 1:
            raise Warning(_("Selected pickings have different type"))
        if len(t_paym_list) > 1:
            raise Warning(_("Selected pickings have different payment terms"))   
        if len(t_carr_list) > 1:
            raise Warning(_("Selected pickings have different carriers"))         
        if len(t_inco_list) > 1:
            raise Warning(_("Selected pickings have different incoterms"))     
        if len(t_user_list) > 1:
            raise Warning(_("Selected pickings have different users"))               
        if len(t_comp_list) > 1:
            raise Warning(_("Selected pickings are from different companies"))               

        res = super(DdTFromPickings, self).create_ddt()
        
        vals = {}
        
        if t_paym_list and 'res_id' in res and res['res_id']:
            vals.update({'payment_term': t_paym_list[0]})
        if t_carr_list and 'res_id' in res and res['res_id']:
            vals.update({'carrier_id': t_carr_list[0]})
        if t_inco_list and 'res_id' in res and res['res_id']:
            vals.update({'incoterm_id': t_inco_list[0]})
        if t_user_list and 'res_id' in res and res['res_id']:
            vals.update({'user_id': t_user_list[0]})        
        if t_comp_list and 'res_id' in res and res['res_id']:
            vals.update({'company_id': t_comp_list[0]})                   
        if transportation_method_id and 'res_id' in res and res['res_id']:
            vals.update({'transportation_method_id': transportation_method_id})

        if t_partner_invoice and t_partner_shipping:
            vals.update({'partner_id': t_partner_invoice, 'delivery_address_id': t_partner_shipping})            
        elif t_partner_id and 'res_id' in res and res['res_id']:
            partner_obj = self.pool['res.partner']
            partner_data = partner_obj.browse(self._cr, self._uid, t_partner_id)
            if partner_data.parent_id:
                vals.update({'partner_id': partner_data.parent_id.id, 'delivery_address_id': partner_data.id})
                
        if vals:
            self.pool.get('stock.ddt').write(self._cr, self._uid, res['res_id'], vals, context=self._context)

        return res
