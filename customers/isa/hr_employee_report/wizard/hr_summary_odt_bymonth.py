# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import fields, orm


class hr_summary_odt_bymonth(orm.TransientModel):
    _name = 'hr.employee.report.summary.month'
    _description = 'Print Monthly Holidays Report'
    _columns = {
        'month': fields.selection([(1, 'January'),
                                   (2, 'February'),
                                   (3, 'March'),
                                   (4, 'April'),
                                   (5, 'May'),
                                   (6, 'June'),
                                   (7, 'July'),
                                   (8, 'August'),
                                   (9, 'September'),
                                   (10, 'October'),
                                   (11, 'November'),
                                   (12, 'December')],
                                  'Month', required=True),
        'year': fields.integer('Year', required=True),
        'print_holidays': fields.boolean('Print Holidays'),
        'print_attendances': fields.boolean('Print Attendances'),
        'print_overtime': fields.boolean('Print Overtime'),

    }
    _defaults = {
        'month': lambda *a: time.gmtime()[1],
        'year': lambda *a: time.gmtime()[0],
        'print_holidays': True,
        'print_attendances': True,
        'print_overtime': True,
    }

    def print_report(self, cr, uid, ids, context={}):
        datas = {'ids': [],
                 'model': 'hr.employee',
                 'form': self.read(cr, uid, ids)[0]
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'summary',
            'datas': datas,
            'context': context,
        }
