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

from openerp.osv import orm
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class hr_expense_line(orm.Model):
    _inherit = 'hr.expense.line'

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if context is None:
            context = {}

        res = super(hr_expense_line, self).onchange_product_id(cr, uid, ids, product_id, context)

        if product_id:
            t_partner = None
            t_employee_id = context.get('employee', False)
            if t_employee_id:
                employee_obj = self.pool.get('hr.employee')
                employee_data = employee_obj.browse(cr, uid, t_employee_id)
                t_partner = employee_data and employee_data.user_id and employee_data.user_id.partner_id.id or None
            t_analytic_account = context.get('analytic_account', False)
            if t_analytic_account:
                analytic_account_obj = self.pool.get('account.analytic.account')
                analytic_account_data = analytic_account_obj.browse(cr, uid, t_analytic_account)

                t_pricelist = analytic_account_data.pricelist_id or None
                if not t_pricelist:
                    raise except_orm(_('Error!'),
                                     _('Nessun listino di vendita definito per il Conto Analitico'))

                pricelist_pool = self.pool.get('product.pricelist')
                unit_price = pricelist_pool.price_get(cr, uid,
                                                      [t_pricelist.id],
                                                      product_id,
                                                      1.0,
                                                      t_partner)[t_pricelist.id]
                res['value']['unit_amount'] = unit_price

        return res

    def onchange_analytic_account_id(self, cr, uid, ids, analytic_account_id, product_id, context=None):
        if context is None:
            context = {}

        res = {'value': {}, }
        if product_id:
            t_partner = None
            t_employee_id = context.get('employee', False)
            if t_employee_id:
                employee_obj = self.pool.get('hr.employee')
                employee_data = employee_obj.browse(cr, uid, t_employee_id)
                t_partner = employee_data and employee_data.user_id and employee_data.user_id.partner_id.id or None

            if analytic_account_id:
                analytic_account_obj = self.pool.get('account.analytic.account')
                analytic_account_data = analytic_account_obj.browse(cr, uid, analytic_account_id)

                t_pricelist = analytic_account_data.pricelist_id or None
                if not t_pricelist:
                    raise except_orm(_('Error!'),
                                     _('Nessun listino di vendita definito per il Conto Analitico'))

                pricelist_pool = self.pool.get('product.pricelist')
                unit_price = pricelist_pool.price_get(cr, uid,
                                                      [t_pricelist.id],
                                                      product_id,
                                                      1.0,
                                                      t_partner)[t_pricelist.id]
                res['value']['unit_amount'] = unit_price

        return res
