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


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    _columns = {'exclude_from_print': fields.boolean('Exclude From Printings'),
                'exclude_from_invoice': fields.boolean('Escludi dalla Fatturazione'),
                'invoiced_related': fields.related('invoiced', type="boolean", string="Invoiced")
                }

    _defaults = {'exclude_from_print': False,
                 'exclude_from_invoice': False,
                 }

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):

        res = {}
        if not line.exclude_from_invoice:
            return super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)

        return res
