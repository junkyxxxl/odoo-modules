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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from datetime import datetime

class stock_picking_type(models.Model):
    _inherit = "stock.picking.type"
    
    @api.cr_uid_context
    def search_read(self, cr, uid, domain=None, fields=None, offset=0, limit=None, order=None, context=None):
        if context and 't_check' in context and context['t_check']:
            
            if domain and isinstance(domain,list):
                new_domain = []
                for it in domain:
                    new_it = it
                    if isinstance(it,list):
                        if len(it) == 3:
                            if it[2]:
                                if isinstance(it[2],list):
                                    if it[2][0]:
                                        if isinstance(it[2][0],list):
                                            if len(it[2][0]) == 3:
                        
                                                new_list = []
                                                for id in it[2][0][2]:
                                                    new_list.append(id)
                                                new_it = (it[0],it[1],new_list)
                        
                    new_domain.append(new_it)
                domain = new_domain
        return super(stock_picking_type,self).search_read(cr, uid, domain, fields, offset, limit, order, context=context)

class stockOnhandProductsReport(models.Model):
    
    _name = 'stock.onhand.products.report'
    _description = "Stampa Articoli Sottoscorta"

    @api.one
    @api.constrains('stock_ids')
    def _check_stock_count(self):
        if self.stock_ids and len(self.stock_ids.ids) > 3:
                raise ValidationError(_("It's not possible to select more than 3 stock locations."))      

    name = fields.Char(string="Name", )
    picking_type_ids = fields.Many2many('stock.picking.type',string="Picking Types", )
    stock_ids = fields.Many2many('stock.location',string="Stock Locations (Limit: 3)", )
    family_ids = fields.Many2many('product.family',string="Families",domain=[('type','=','family')], )
    company_id = fields.Many2one('res.company', 'Company Reference', required=True, ondelete="cascade", default=lambda self: self.env.user.company_id)
    