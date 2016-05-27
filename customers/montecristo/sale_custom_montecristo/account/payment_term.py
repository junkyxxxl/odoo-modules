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

from openerp.osv import fields, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

class account_payment_term_line_montecristo(orm.Model):
    _inherit = "account.payment.term.line"

    _columns = {
                'fixed_date': fields.date('Fixed Date'),
            }

class account_payment_term_montecristo(orm.Model):
    _inherit = "account.payment.term"
    
    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        if context and 'invoice_id' in context and context['invoice_id']:
            invoice_data = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'], context=context)
            if invoice_data.date_start_payment:
                date_ref = invoice_data.date_start_payment
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        result = []
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        for line in pt.line_ids:
            t_payment_term = line.payment_type
            if line.value == 'fixed':
                amt = round(line.value_amount, prec)
            elif line.value == 'procent':
                amt = round(value * line.value_amount, prec)
            elif line.value == 'balance':
                amt = round(amount, prec)
            if not amt:
                amt = 0.0
            next_date = (datetime.strptime(date_ref, '%Y-%m-%d') + relativedelta(days=line.days))
            if line.days2 < 0:
                q = line.days/30
                r = line.days%30
                next_date = datetime.strptime(date_ref, '%Y-%m-%d')
                next_date += relativedelta(days=r, months=q+1)
                next_date += relativedelta(day=1)
                next_date += relativedelta(days=line.days2)
                
                #next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                #next_date = next_first_date + relativedelta(days=line.days2)
            if line.days2 > 0:
                next_date += relativedelta(day=line.days2, months=1)
            if line.fixed_date:
                next_date = datetime.strptime(line.fixed_date, '%Y-%m-%d')
            result.append((next_date.strftime('%Y-%m-%d'), amt, t_payment_term))
            amount -= amt

        amount = reduce(lambda x, y: x + y[1], result, 0.0)
        dist = round(value - amount, prec)
        if dist:
            result.append((time.strftime('%Y-%m-%d'), dist, None))
        return result
