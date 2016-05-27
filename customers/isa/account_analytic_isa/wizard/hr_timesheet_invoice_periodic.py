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

from openerp import fields, models
from openerp.tools.translate import _


class hr_timesheet_invoice_periodic(models.TransientModel):
    _name = 'hr.timesheet.invoice.periodic'

    period_id = fields.Many2one('account.period', 'Periodo', required=False)
    is_test = fields.Boolean(string='Crea Fattura in TEST')

    def do_create(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        period = wizard.period_id
        invoice_id_list = []
        account_obj = self.pool.get('account.analytic.account')
        accounts_data = account_obj.browse(cr, uid, context['active_ids'])
        for account_data in accounts_data:
            recurring_next_date = account_data.recurring_next_date
            period_date_start = period.date_start
            period_date_stop = period.date_stop
            if recurring_next_date \
                and recurring_next_date >= period_date_start \
                and recurring_next_date <= period_date_stop:

                if wizard.is_test:
                    invoice_ids = account_obj.recurring_create_test_invoice(cr, uid, [account_data.id])
                else:
                    invoice_ids = account_obj.recurring_create_invoice(cr, uid, [account_data.id])

                invoice_id_list.append(invoice_ids)

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        mod_ids = mod_obj.search(cr, uid, [('name', '=', 'action_invoice_tree1')], context=context)
        res_id = mod_obj.read(cr, uid, mod_ids, ['res_id'], context=context)[0]['res_id']
        act_win = act_obj.read(cr, uid, [res_id], context=context)[0]
        act_win['domain'] = [('id', 'in', invoice_id_list), ('type', '=', 'out_invoice')]
        act_win['name'] = _('Invoices')
        return act_win
