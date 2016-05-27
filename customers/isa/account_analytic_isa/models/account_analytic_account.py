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

from dateutil.relativedelta import relativedelta
import datetime
import logging
import time
from openerp import models, fields

_logger = logging.getLogger(__name__)


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    sale_order_id = fields.Many2one('sale.order', 'Sale Order Reference', select=True)
    area_hb_ids = fields.Many2many(comodel_name='account.analytic.areahb',
                                   relation='account_analytic_area_hr_rel',
                                   string='Area HB')
    ticket_number = fields.Integer(string='Ticket Number')  # TODO da eliminare?
    contact_id = fields.Many2one('res.partner', string='Contatto', required=False)

    def _prepare_invoice(self, cr, uid, contract, context=None):
        context = context or {}
        invoice = self._prepare_invoice_data(cr, uid, contract, context=context)
        if context.get('payment_term', False):
            invoice['payment_term'] = context.get('payment_term', False)
        invoice['invoice_line'] = self._prepare_invoice_lines(cr, uid, contract, invoice['fiscal_position'], context=context)
        return invoice

    def recurring_create_test_invoice(self, cr, uid, ids, context=None):
        ctx = context.copy()
        ctx.update({'create_test_invoice': True, })
        return self._recurring_create_invoice(cr, uid, ids, context=ctx)

    def set_recurring_create_invoice_date(self, cr, uid, ids, contract_id, new_date, context=None):
        self.write(cr, uid, [contract_id], {'recurring_next_date': new_date.strftime('%Y-%m-%d')}, context=context)

    def _recurring_create_invoice(self, cr, uid, ids, automatic=False, context=None):
        context = context or {}
        invoice_ids = []
        current_date = time.strftime('%Y-%m-%d')
        if ids:
            contract_ids = ids
        else:
            contract_ids = self.search(cr, uid, [('recurring_next_date', '<=', current_date), ('state', '=', 'open'), ('recurring_invoices', '=', True), ('type', '=', 'contract')])
        if contract_ids:
            cr.execute('SELECT company_id, array_agg(id) as ids FROM account_analytic_account WHERE id IN %s GROUP BY company_id', (tuple(contract_ids),))
            for company_id, ids in cr.fetchall():
                for contract in self.browse(cr, uid, ids, context=dict(context, company_id=company_id, force_company=company_id)):
                    if contract.sale_order_id and contract.sale_order_id.payment_term:
                        context.update({'payment_term': contract.sale_order_id.payment_term.id, })
                    try:
                        invoice_values = self._prepare_invoice(cr, uid, contract, context=context)
                        if 'date_invoice' in invoice_values:
                            invoice_values['registration_date'] = invoice_values['date_invoice']
                        t_invoice_id = self.pool['account.invoice'].create(cr, uid, invoice_values, context=context)
                        if contract.sale_order_id:
                            t_order_id = contract.sale_order_id.id
                            cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (t_order_id, t_invoice_id))
                        invoice_ids.append(t_invoice_id)
                        next_date = datetime.datetime.strptime(contract.recurring_next_date or current_date, "%Y-%m-%d")
                        interval = contract.recurring_interval
                        if contract.recurring_rule_type == 'daily':
                            new_date = next_date+relativedelta(days=+interval)
                        elif contract.recurring_rule_type == 'weekly':
                            new_date = next_date+relativedelta(weeks=+interval)
                        elif contract.recurring_rule_type == 'monthly':
                            new_date = next_date+relativedelta(months=+interval)
                        else:
                            new_date = next_date+relativedelta(years=+interval)
                        if not context.get('create_test_invoice', False):
                            self.set_recurring_create_invoice_date(cr, uid, ids, contract.id, new_date, context=context)
                        if automatic:
                            cr.commit()
                    except Exception:
                        if automatic:
                            cr.rollback()
                            _logger.exception('Fail to create recurring invoice for contract %s', contract.code)
                        else:
                            raise
        return invoice_ids
