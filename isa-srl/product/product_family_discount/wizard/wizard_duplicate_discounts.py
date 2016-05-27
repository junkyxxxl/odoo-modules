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
from datetime import date, datetime
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class wizard_duplicate_discounts_on(models.TransientModel):

    _name = 'wizard.duplicate.discounts.on'
    _description = 'Duplicate Discounts from a Partner to Another'
    
    source_partner_id = fields.Many2one('res.partner', string="Source Partner")
    receiver_partner_ids = fields.Many2many('res.partner', string="Receiver Partners")             
    family_discount_ids = fields.One2many('product.family.discount', string="Family Discounts", related="source_partner_id.family_discount_ids")
    
    @api.multi
    def duplicate(self):
        if self.source_partner_id and self.receiver_partner_ids:
            
            family_disc_obj = self.env['product.family.discount']
            
            for receiver_id in self.receiver_partner_ids:
                for discount_id in receiver_id.family_discount_ids:
                    discount_id.unlink()
                for discount_id in self.family_discount_ids:
                    family_disc_obj.create({'family_id': discount_id.family_id.id, 'discount': discount_id.discount, 'partner_id': receiver_id.id})
                    
    
class wizard_duplicate_discounts_from(models.TransientModel):

    _name = 'wizard.duplicate.discounts.from'
    _description = 'Duplicate Discounts from a Partner to Another'
    
    source_partner_id = fields.Many2one('res.partner', string="Source Partner")
    receiver_partner_id = fields.Many2one('res.partner', string="Receiver Partner")   
    family_discount_ids = fields.One2many('product.family.discount', string="Family Discounts", related="source_partner_id.family_discount_ids") 
    
    @api.multi
    def duplicate(self):
        if self.source_partner_id and self.receiver_partner_id:            
            family_disc_obj = self.env['product.family.discount']            
            for discount_id in self.receiver_partner_id.family_discount_ids:
                discount_id.unlink()
            for discount_id in self.family_discount_ids:
                family_disc_obj.create({'family_id': discount_id.family_id.id, 'discount': discount_id.discount, 'partner_id': self.receiver_partner_id.id})       