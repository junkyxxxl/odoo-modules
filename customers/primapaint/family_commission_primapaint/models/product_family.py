# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp

class product_family_category_commission(models.Model):
    _name='product.family.category.commission'

    @api.one
    @api.constrains('family_category_commission_perc')
    def _check_commission(self):
        if self.family_category_commission_perc < 0.0 or self.family_category_commission_perc > 100.0:
            raise ValidationError(_("Commission should be between 0 and 100!"))

    family_id = fields.Many2one('product.family', string="Family", )  
    family_category_commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'), )
    special_partner_category_id = fields.Many2one('category.partner', string="Special Partner Category", )    

class product_family_commission_discount(models.Model):
    _name='product.family.commission.discount'
    _order='discount ASC'

    @api.one
    @api.constrains('family_discount_commission_perc','discount')
    def _check_commission_discount(self):
        if self.family_discount_commission_perc < 0.0 or self.family_discount_commission_perc > 100.0:
            raise ValidationError(_("Commission should be between 0 and 100!"))
        if self.discount < 0.0 or self.discount > 100.0:
            raise ValidationError(_("Discount should be between 0 and 100!"))  

    family_id = fields.Many2one('product.family', string="Family", )    
    family_discount_commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'), )        
    discount = fields.Float(string="Max. Discount [%]", digits_compute= dp.get_precision('Account'), )        


class product_family(models.Model):
    
    _inherit="product.family"
        
    family_commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'), )
    net_price_commission_perc = fields.Float(string="Commission [%] for Net Price", digits_compute = dp.get_precision('Account'), )        

    commission_discount_ids = fields.One2many('product.family.commission.discount', 'family_id', string="Discount/Commission Lines", )
    category_commission_ids = fields.One2many('product.family.category.commission', 'family_id', string="Special Commissions for Category", )

    
    @api.model
    def get_commission_perc(self, partner_id, discount=0.0):
        
        max_discount = 0
        partner = self.env['res.partner'].browse(partner_id)
        
        if partner.family_discount_ids:
            for line in partner.family_discount_ids:
                if line.family_id.id == self.id:
                    max_discount = line.discount

        t_discount = 0
        for line in self.commission_discount_ids:
            if line.discount > t_discount:
                t_discount = line.discount

        t_max_discount = 100 - (100 * ((100-max_discount)/100) * ((100-t_discount)/100))        
            
        if discount - t_max_discount <= 0.0001:
            for line in self.category_commission_ids:
                if line.special_partner_category_id == partner.partner_category:
                    if line.family_category_commission_perc:
                        return line.family_category_commission_perc
                    else:
                        return -5.0
            if discount - max_discount <= 0.0001:
                return self.family_commission_perc
            else:
                for line in self.commission_discount_ids:
                    expr = 100 - (100 * ((100-max_discount)/100) * ((100-line.discount)/100))
                    if expr >= discount:
                        return line.family_discount_commission_perc
                
        elif self.commission_discount_ids:
            for line in self.category_commission_ids:
                if line.special_partner_category_id == partner.partner_category:
                    return -10.0            
        else:
            return -10.0

    @api.one
    @api.constrains('family_commission_perc')
    def _check_commission(self):
        if self.family_commission_perc < 0.0 or self.family_commission_perc > 100.0:
            raise ValidationError(_("Commission should be between 0 and 100!"))   
        
    @api.one
    @api.constrains('category_commission_ids',)
    def _check_category_commission_duplicated(self):
        error = []
        error_string = ''
        cat_list = {}
        if self.category_commission_ids:
            for id in self.category_commission_ids:
                if id.special_partner_category_id.id not in cat_list:
                    cat_list[id.special_partner_category_id.id] = 0
                cat_list[id.special_partner_category_id.id] += 1
            for item in cat_list:
                if cat_list[item] > 1:
                    error.append(item)
            if error:
                error_string += '('
                for err_id in error:
                    temp = self.env['category.partner'].browse(err_id)
                    error_string = error_string + '[' + temp.code + '] ' + temp.description + '; '
                error_string += ')'
                raise ValidationError(_("It's not possible to set more than one commission for each category; Duplicated category on this family is: "+error_string))                    
     