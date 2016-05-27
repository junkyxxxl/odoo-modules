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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError

class product_family_discount(models.Model):
    
    _name = 'product.family.discount'
    _description = 'Product Family Discount'
    _order = 'family_code'
  
    @api.model
    def _get_family_type_domain(self):
        
        type = self.env['res.users'].browse(self._uid).company_id.family_type_filter
        if type:
            return [('type', '=', type)]
        return             
   
    discount = fields.Float(string="Discount [%]", digits_compute= dp.get_precision('Discount'), )
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    family_id = fields.Many2one('product.family', string="Family", domain=_get_family_type_domain) 
    family_name = fields.Char(related="family_id.name", store=True)
    family_code = fields.Char(related="family_id.code", store=True)
     

    @api.one
    @api.constrains('discount')
    def _check_discount(self):
        if self.discount < 0.0 or self.discount > 100.0:          
            raise ValidationError(_("The discount defined is greater than 100%, which is not allowed!"))       


class res_partner_family_discount(models.Model):

    _inherit = 'res.partner'

    family_discount_ids = fields.One2many('product.family.discount', 'partner_id', string="Classifier Discounts")

    @api.one
    @api.constrains('family_discount_ids',)
    def _check_family_discount_duplicated(self):
        error = []
        error_string = ''
        fam_list = {}
        if self.family_discount_ids:
            for id in self.family_discount_ids:
                if id.family_id.id not in fam_list:
                    fam_list[id.family_id.id] = 0
                fam_list[id.family_id.id] += 1
            for item in fam_list:
                if fam_list[item] > 1:
                    error.append(item)
            if error:
                error_string += '('
                for err_id in error:
                    temp = self.env['product.family'].browse(err_id)
                    error_string = error_string + '[' + temp.code + '] ' + temp.name + '; '
                error_string += ')'
                raise ValidationError(_("It's not possible to set more than one discount for each classifier; Duplicated classifier on this customer is: "+error_string))                    
                         
                          

    def action_duplicate_discounts_on(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid, 'product_family_discount','wizard_duplicate_discounts_on_view')
        view_id = result and result[1] or False

        return {
                'name': _("Duplicate Discounts"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.duplicate.discounts.on',
                'type': 'ir.actions.act_window',
                'context': {'default_source_partner_id':ids[0]},
                'target': 'new',
                'views': [(view_id,'form'),(False,'tree')],
                }
        
    def action_duplicate_discounts_from(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid, 'product_family_discount','wizard_duplicate_discounts_from_view')
        view_id = result and result[1] or False

        return {
                'name': _("Duplicate Discounts"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.duplicate.discounts.from',
                'type': 'ir.actions.act_window',
                'context': {'default_receiver_partner_id':ids[0]},
                'target': 'new',
                'views': [(view_id,'form'),(False,'tree')],
                }        