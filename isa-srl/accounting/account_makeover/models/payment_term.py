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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from openerp.osv import orm


class account_payment_term_makeover(orm.Model):
    _inherit = "account.payment.term"
    
    def check_if_holiday(self, t_date):
        t_format_date = datetime.strptime(t_date, '%Y-%m-%d')
        t_day_week = t_format_date.weekday()
        if(t_day_week == 5):
            t_format_date = t_format_date + timedelta(days=2)
        if(t_day_week == 6):
            t_format_date = t_format_date + timedelta(days=1)
        t_date = t_format_date.strftime('%Y-%m-%d')
        return t_date
    
    def compute(self, cr, uid, id, value, date_ref=False, context=None):
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
            result.append((next_date.strftime('%Y-%m-%d'), amt, t_payment_term))
            amount -= amt

        amount = reduce(lambda x, y: x + y[1], result, 0.0)
        dist = round(value - amount, prec)
        if dist:
            result.append((time.strftime('%Y-%m-%d'), dist, None))
        return result
