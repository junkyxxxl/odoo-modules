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

from openerp.osv import fields, orm


class purchase_requisition_line(orm.Model):
    _inherit = 'purchase.requisition.line'

    _columns = {'detailed_description': fields.text('Detailed Description',
                                                    translate=True),
                'short_description': fields.char('Short Description',
                                                 size=120),
                }

    def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id, parent_analytic_account, analytic_account, parent_date, date, context=None):
        if context is None:
            context = {}
        result = super(purchase_requisition_line, self).onchange_product_id(cr, uid, ids, product_id, product_uom_id, parent_analytic_account, analytic_account, parent_date, date, context)
        if 'product_qty' in result['value']:
            del result['value']['product_qty']
        return result
