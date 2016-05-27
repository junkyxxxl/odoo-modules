# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ISA s.r.l. (<http://www.isa.it>).
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

from openerp import models, fields, api


class SaleDocumentType(models.Model):

    _inherit = 'sale.document.type'

    warehouse_id = fields.Many2one('stock.warehouse', 'Magazzino')
    location_id = fields.Many2one('stock.location', 'Punto di Stoccaggio Destinazione')
    route_id = fields.Many2one('stock.location.route', 'Route', domain=[('sale_selectable', '=', True)])

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        t_list = []
        t_document_type_id = self.env.context.get('default_warehouse_id', False)
        if t_document_type_id:
            t_list = self.env['sale.document.type'].search([('warehouse_id', '=', t_document_type_id)]).ids

        if t_list:
            args = args + [['id', 'in', t_list]]

        return super(SaleDocumentType, self).name_search(name=name, args=args, operator=operator, limit=limit)
