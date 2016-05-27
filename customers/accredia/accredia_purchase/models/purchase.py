# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv


class purchase_order(osv.osv):

    _inherit = "purchase.order"

    def _default_department_id(self, cr, uid, context=None):
        users_obj = self.pool.get('res.users')
        t_user_data = users_obj.browse(cr, uid, uid)
        t_value = None
        if t_user_data.department_id:
            return t_user_data.department_id.id
        for dep in t_user_data.department_ids:
            t_value = dep.id
        return t_value

    _columns = {
        'department_id': fields.many2one('hr.department',
                                         'Dipartimento'),
        'is_confirmed': fields.boolean('Confermato'),
        'task_id': fields.many2one('project.task',
                                   'Riferimento'),
    }

    _defaults = {'department_id': _default_department_id,
                 }

    def _get_analytic_lines(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        cur_obj = self.pool.get('res.currency')
        invoice_obj = self.pool.get('account.invoice')

        inv = invoice_obj.browse(cr, uid, id)

        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        if inv.type in ('out_invoice', 'in_refund'):
            sign = 1
        else:
            sign = -1
        t_list = []
        iml = self.pool.get('account.invoice.line').move_line_get(cr, uid, inv.id, context=context)
        for il in iml:
            if il['account_analytic_id']:
                if inv.type in ('in_invoice', 'in_refund'):
                    ref = inv.reference
                else:
                    ref = self._convert_ref(cr, uid, inv.number)

                to_invoice = None
                try:
                    to_invoice = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_timesheet_invoice', 'timesheet_invoice_factor1')
                except ValueError:
                    pass

                t_list.append( {
                    'name': il['name'],
                    'date': inv['date_invoice'],
                    'account_id': il['account_analytic_id'],
                    'unit_amount': il['quantity'],
                    'amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, il['price'], context={'date': inv.date_invoice}) * sign,
                    'product_id': il['product_id'],
                    'product_uom_id': il['uos_id'],
                    'general_account_id': il['account_id'],
                    'to_invoice': to_invoice[1],
                    'ref': ref,
                })
        return t_list

    def action_invoice_create(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        product_obj = self.pool.get('product.product')
        analytic_line_obj = self.pool.get('account.analytic.line')

        res = super(purchase_order, self).action_invoice_create(
            cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids, context=context):
            invoice_obj.write(
                cr, uid, res,
                {'department_id': order.department_id.id},
                context=context)
            if res:
                iml = self._get_analytic_lines(cr, uid, res, context=context)
                for il in iml:
                    product_data = product_obj.browse(cr, uid, il['product_id'], context=context)
                    if product_data and product_data.hr_expense_ok:
                        analytic_line_obj.create(cr, uid, il, context=context)

        return res
