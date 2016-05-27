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

from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import datetime
import os

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0)
                  and ((year % 100 != 0)
                  or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


class parser_attendances(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    def __init__(self, cr, uid, name, context):
        self.total_attendance = {}
        self.total_att = 0
        self.context = context
        super(parser_attendances, self).__init__(cr, uid, name, context)

        self.localcontext.update({
            'get_total_attendance': self.get_total_attendance,
            'get_day_attendance': self.get_day_attendance,
            'get_days': self.get_days,
            'get_date': self.get_date,
            'get_wizard_params': self.get_wizard_params,
            'get_emps': self.get_employees,
            'get_total': self.get_total,
        })

    def get_employees(self):
        sql_string = '''
            select emp.id,res.name
            from hr_employee emp
            inner join resource_resource res on emp.resource_id=res.id
            where res.active=true and emp.department_id is not null

            order by res.name
        '''
        # id_string = ','.join(str(n) for n in self.context['active_ids'])
        # sql = sql_string % (id_string)
        self.cr.execute(sql_string)
        emps = self.cr.dictfetchall()
        return emps

    def get_day_attendance(self):
        day_attendance = []
        last_day = lengthmonth(self.year, self.month)
        for i in range(1, last_day + 1, 1):
            if(i in self.total_attendance):
                temp = '%.1f' % self.total_attendance[i]
            else:
                temp = '0'

            day_attendance.append(temp)
            self.total_att = self.total_att + float(temp)
        return day_attendance

    def get_wizard_params(self, month, year):
        self.month = month
        self.year = year

    def get_total_attendance(self, emp_id):
        self.total_att = 0
        # fisso il mese che poi verra recuperate/calcolate con un wizard
        # last_day_month = lengthmonth(self.year, self.month)
        # first_date = datetime(self.year, self.month, 1)
        # last_date = datetime(self.year, self.month, last_day_month)
        # emp_id=21
        # esclusi gli di uscita/rientro per servizio
        sql = '''
            select action, att.name
            from hr_employee as emp
            inner join hr_attendance as att on emp.id = att.employee_id
            inner join hr_action_reason as act_reas
                on act_reas.id=att.action_desc
            where (act_reas.considered_in_att='true'
                or att.action_desc is null)
            and EXTRACT(YEAR FROM (att.name))=%s
            and EXTRACT(MONTH FROM (att.name))=%s
            and emp.id = %s
            order by att.name
            '''

        self.cr.execute(sql, (self.year, self.month, emp_id))
        attendances = self.cr.dictfetchall()
        total_attendances = {}
        # sum up the attendances' durations
        ldt = None
        for att in attendances:
            dt = datetime.strptime(att['name'], DTF)
            if ldt and att['action'] == 'sign_out':
                total_attendances[ldt.date().day] = total_attendances.get(
                                            ldt.date().day, 0) + (
                                            float((dt - ldt).seconds) / 3600)
            else:
                ldt = dt
        self.total_attendance = total_attendances
        # return total_attendances

    def get_days(self):
        last_day = lengthmonth(self.year, self.month)
        days = []
        for i in range(1, last_day + 1, 1):
            days.append(i)
        return days

    def get_date(self):
        date = datetime(self.year, self.month, 1)
        return date.strftime("%B %Y")

    def get_total(self):
        return self.total_att

HeaderFooterTextWebKitParser('report.attendance',
                             'hr.employee',
                             os.path.dirname(os.path.realpath(__file__)) + '/attendances.mako',
                             parser=parser_attendances)
