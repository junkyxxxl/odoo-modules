# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from openerp.exceptions import ValidationError

class res_users_signature(models.Model):
    _name = "res.users.signature"
    _description = 'User Signature'    
    _order = 'company_id, id'
    
    company_id = fields.Many2one('res.company', string="Company")
    signature = fields.Html(string="Signature")
    user_id = fields.Many2one('res.users', string="User")
    
    @api.one
    @api.constrains('company_id','user_id')
    def _check_unicity(self):
        lst = self.search([('id','!=',self.id),('company_id','=',self.company_id.id),('user_id','=',self.user_id.id)])
        if lst:
            raise ValidationError(_("The user already has a signature for this company"))   


class res_users(models.Model):
    _inherit = "res.users"

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.signature_ids:
            
            for signature_id in self.signature_ids:
                if signature_id.company_id.id == self.company_id.id:
                    self.signature = signature_id.signature
                    break

    signature_ids = fields.One2many('res.users.signature', 'user_id', string="User Signatures")
    