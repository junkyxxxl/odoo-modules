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


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    def _find_parent_locations(self, cr, uid, procurement, context=None):
        res = super(ProcurementOrder,self)._find_parent_locations(cr,uid,procurement,context=context)
        
        if procurement.sale_line_id and procurement.sale_line_id.order_id and procurement.sale_line_id.order_id.document_type_id and procurement.sale_line_id.order_id.document_type_id.location_id:
           res.append(procurement.sale_line_id.order_id.document_type_id.location_id.id)       
        return res

    def _run_move_create(self, cr, uid, procurement, context=None):
        res = super(ProcurementOrder,self)._run_move_create(cr,uid,procurement,context=context)

        if res and procurement.sale_line_id and procurement.sale_line_id.order_id.document_type_id:
            res.update({'location_dest_id': procurement.rule_id.location_id.id})        
        return res
