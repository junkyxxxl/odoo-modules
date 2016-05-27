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


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(SaleOrder, self).write(cr, uid, ids, vals, context=context)
        if 'document_type_id' in vals:
            sale_line_obj = self.pool.get('sale.order.line')
            for id in ids:
                sale_obj = self.browse(cr,uid,ids,context=context)
                if sale_obj.document_type_id:
                    for line in sale_obj.order_line:
                        sale_line_obj.write(cr, uid, line.id, {'route_id':sale_obj.document_type_id.route_id.id})
                else:
                    for line in sale_obj.order_line:
                        sale_line_obj.write(cr, uid, line.id, {'route_id':None})

        else:
            sale_line_obj = self.pool.get('sale.order.line')
            for id in ids:
                sale_obj = self.browse(cr,uid,ids,context=context)
                for line in sale_obj.order_line:
                    sale_line_obj.write(cr, uid, line.id, {'route_id':sale_obj.document_type_id.route_id.id})

        return res

    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}
        new_id = super(SaleOrder, self).create(cr, uid, vals, context=context)

        if vals.get('document_type_id', False):
            sale_obj = self.browse(cr,uid,new_id,context=context)
            sale_line_obj = self.pool.get('sale.order.line')
            for line in sale_obj.order_line:
                sale_line_obj.write(cr, uid, line.id, {'route_id':sale_obj.document_type_id.route_id.id}, context=context)
        return new_id
