# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicola Malcontenti Agile Business Group
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


class AddPickingToDdt(models.TransientModel):

    _inherit = "add.pickings.to.ddt"

    @api.multi
    def get_default_ddt(self):
        active_domain = self.env.context.get('active_domain',None)
        if active_domain:
            for list_item in active_domain:
                if len(list_item) == 3:
                    if list_item[0] == 'ddt_id' and list_item[1] == 'not in' and list_item[2]:
                        return list_item[2][0]
        return None

    ddt_id = fields.Many2one('stock.ddt', default=get_default_ddt)

    @api.multi
    def add_to_ddt(self):
        pickings = self.env['stock.picking'].browse(
            self.env.context['active_ids'])
        t_type_list = []        
        t_paym_list = []
        t_carr_list = []
        t_inco_list = [] 
        t_comp_list = []      
        
        for picking in pickings:
            if picking.use_shipping_invoice:
                raise Warning(
                    _("Picking %s riservato per fattura Accompagnatoria") % picking.name)
            if picking.picking_type_id and picking.picking_type_id.id not in t_type_list:
                t_type_list.append(picking.picking_type_id.id)
            if picking.carrier_id and picking.carrier_id.id not in t_carr_list:
                t_carr_list.append(picking.carrier_id.id)                
            if picking.incoterm_id and picking.incoterm_id.id not in t_inco_list:
                t_inco_list.append(picking.incoterm_id.id) 
            if picking.company_id and picking.company_id.id not in t_comp_list:
                t_comp_list.append(picking.company_id.id)                 


            if picking.ddt_id:
                raise Warning(
                    _("Picking %s already in ddt") % picking.name)
            
            if picking.sale_id:
                if picking.sale_id.partner_invoice_id != self.ddt_id.partner_id:
                    raise Warning(
                        _("Selected Picking %s comes from"
                          " a sale order with different invoice address") % picking.name)        
                if picking.sale_id.partner_shipping_id != self.ddt_id.delivery_address_id:
                    raise Warning(
                        _("Selected Picking %s comes from"
                          " a sale order with different shipping address") % picking.name)                                     
                    
            elif picking.partner_id != self.ddt_id.partner_id:
                raise Warning(
                    _("Selected Picking %s have"
                      " different Partner") % picking.name)

            if picking.delivery_methods:
                if picking.delivery_methods != self.ddt_id.transportation_method_id:
                    raise Warning(
                        _("Selected Picking %s have"
                          " different transportation method") % picking.name)                
            elif picking.sale_id and picking.sale_id.transportation_method_id != self.ddt_id.transportation_method_id:
                raise Warning(
                    _("Selected Picking %s have"
                      " different transportation method") % picking.name)

            if picking.sale_id:
                if picking.sale_id.user_id != self.ddt_id.user_id:
                    raise Warning(
                        _("Selected Picking %s belongs"
                          " to different users") % picking.name)                                
                if picking.sale_id.carriage_condition_id != (
                        self.ddt_id.carriage_condition_id):
                    raise Warning(
                        _("Selected Picking %s have"
                          " different carriage condition") % picking.name)
                elif picking.sale_id.goods_description_id != (
                        self.ddt_id.goods_description_id):
                    raise Warning(
                        _("Selected Picking %s have "
                          "different goods description") % picking.name)
                elif picking.sale_id.transportation_reason_id != (
                        self.ddt_id.transportation_reason_id):
                    raise Warning(
                        _("Selected Picking %s have"
                          " different transportation reason") % picking.name)
                elif picking.sale_id.payment_term and self.ddt_id.payment_term and picking.sale_id.payment_term != (
                        self.ddt_id.payment_term):
                    raise Warning(
                        _("Selected Picking %s have"
                          " different payment terms") % picking.name)         
                
                if picking.sale_id.payment_term and picking.sale_id.payment_term.id not in t_paym_list:
                    t_paym_list.append(picking.sale_id.payment_term.id)                    
                               
            picking.ddt_id = self.ddt_id

        # TODO controllare anche i tipi di picking preesistenti nel ddt
        if len(t_type_list) > 1:
            raise Warning(_("Selected pickings have different type"))
        if len(t_paym_list) > 1:
            raise Warning(_("Selected pickings have different payment terms"))  
        if len(t_carr_list) > 1:
            raise Warning(_("Selected pickings have different carriers"))         
        if len(t_inco_list) > 1:
            raise Warning(_("Selected pickings have different incoterms"))      
        if len(t_comp_list) > 1:
            raise Warning(_("Selected pickings are from different companies"))              
        
        vals = {}
        if t_paym_list and not self.ddt_id.payment_term:
            vals.update({'payment_term':t_paym_list[0]}) 
        if t_carr_list and not self.ddt_id.carrier_id:
            vals.update({'carrier_id':t_carr_list[0]})             
        if t_inco_list and not self.ddt_id.incoterm_id:
            vals.update({'incoterm_id':t_inco_list[0]})      
        if t_comp_list and not self.ddt_id.company_id:
            vals.update({'company_id':t_comp_list[0]})                                  
        if picking.parcels:
            vals.update({'parcels':self.ddt_id.parcels+picking.number_of_packages})            
        elif picking.sale_id and picking.sale_id.parcels:
            vals.update({'parcels':self.ddt_id.parcels+picking.sale_id.parcels})              
        self.ddt_id.write(vals)
        
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference('l10n_it_ddt',
                                                      'stock_ddt_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference('l10n_it_ddt',
                                                      'stock_ddt_tree')
        tree_id = tree_res and tree_res[1] or False
        return {
            'name': 'DdT',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'stock.ddt',
            'res_id': self.ddt_id.id,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'type': 'ir.actions.act_window',
        }
