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
# from hr_holidays_isa.hr_holidays_isa import hr_holidays_isa as Holidays
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
# from openerp.tools.translate import _
from datetime import datetime, timedelta
from openerp import pooler
import copy
import os

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0)
                  and ((year % 100 != 0)
                  or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


class parser_holidays(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):

    def __init__(self, cr, uid, name, context):
        self.total_work_hours_4days = {}
        self.total_holidays_4days = {}
        self.total_holidays = {}
        self.totals_by_type = {}
        self.totals = {}
        self.context = context
        self.holidays_Obj = pooler.get_pool(cr.dbname).get('hr.holidays')
        # user=pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
        # lang=user.context_lang
        # locale.setlocale(locale.LC_ALL, str(lang)+".utf8")
        self.hol_type = self._get_holidays_type_by_orm(cr, uid, context)
        super(parser_holidays, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_holidays_by_month': self.get_holidays_by_month,
            'get_days': self.get_days,
            'get_holidays_by_type': self.get_holidays_by_type,
            'get_holiday_type': self.get_holiday_type,
            'get_totals_by_type': self.get_totals_by_type,
            'get_date': self.get_date,
            'get_wizard_params': self.get_wizard_params,
            'get_emps': self.get_employees,
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

    def get_wizard_params(self, month, year):
        self.month = month
        self.year = year

    def get_holidays_by_type(self, hol_type):
        if(hol_type in self.total_holidays):
            return self.total_holidays[hol_type]
        return 0

    def get_totals_by_type(self, hol_type):
        return self.totals[hol_type]

    def _get_holidays_type_by_orm(self, cr, uid, context):
        hrs = pooler.get_pool(cr.dbname).get('hr.holidays.status')
        hrs_list = hrs.search(cr, uid, [("active", "=", True)])
        orm_types = hrs.read(cr, uid, hrs_list, ['id', 'name'], context)
        return orm_types

        # ritorna le tipologie di permesso che comprendono i festivi,
        # per esempio la malattia
        # It returns the holidays types thath allow destivities days,
        # for example, sick leave
    def _type_allow_festivities(self, cr, uid, context):
        hrs = pooler.get_pool(cr.dbname).get('hr.holidays.status')
        hrs_list = hrs.search(cr, uid,
                              [("active", "=", True),
                               ("allow_festivities", "=", True)])
        return hrs_list

        # ritorna le tipologie di permesso che comprendono i giorni di
        # chiusura,per esempio la malattia
        # It returns the holidays types thath allow closed days, for
        # example, sick leave
    def _type_allow_closed_days(self, cr, uid, context):
        hrs = pooler.get_pool(cr.dbname).get('hr.holidays.status')
        hrs_list = hrs.search(cr, uid, [("active", "=", True),
                                        ("allow_closed_days", "=", True)])
        return hrs_list

    def get_holiday_type(self):
        return self.hol_type

    def get_work_hours_by_month(self, emp_id):
        last_day_month = lengthmonth(self.year, self.month)
        first_date = datetime(self.year, self.month, 1)
        last_date = datetime(self.year, self.month, last_day_month, 23, 59, 59)

        hr_contract_obj = pooler.get_pool(self.cr.dbname).get('hr.contract')
        contract_ids = hr_contract_obj.search(self.cr,
                                          self.uid,
                                          [('employee_id', '=', emp_id), ],
                                          order='date_start desc')
        if not contract_ids:
            # raise orm.except_orm(_('Invalid action !'),
            # _('The employee does not have a contract'))
#            raise Exception(_('The employee does not have a contract'))
            return False

        calendar_id = hr_contract_obj.browse(self.cr,
                                             self.uid,
                                             contract_ids[0]).working_hours.id
        if not calendar_id:
            # raise orm.except_orm(_('Invalid action !'),
            # _('The employee does not have a working hours'))
            # raise Exception(_('The employee does not have a working hours'))
            return False

        working_range_date = self.holidays_Obj.get_holiday_range_date(self.cr,
                                        self.uid, self.context['active_ids'],
                                        last_date, first_date, calendar_id)

        working_range = self.holidays_Obj.get_working_days(self.cr,
                                                    self.uid,
                                                    working_range_date)
        working_range_final = {}
        for data_key in sorted(working_range_date):
            working_range_final[data_key] = 0
            if data_key in working_range:
                working_range_final[data_key] = working_range[data_key]
        self.total_work_hours_4days = working_range_final

    def get_holidays_by_month(self, emp_id):
        last_day_month = lengthmonth(self.year, self.month)
        first_date = datetime(self.year, self.month, 1)
        last_date = datetime(self.year, self.month, last_day_month)

        interval = self._get_interval_days(first_date, last_date)

        ref_range = {}
        for i in interval:
            ref_range[i] = 0

        tot_range = {}
        for k in self._build_totals_dict():
            tot_range[k] = copy.copy(ref_range)

        sql = '''
            select hol.number_of_days_temp,
                   hol.holiday_status_id,
                   hol_status.name,
                   hol.holiday_type,
                   date_from,
                   date_to
            from hr_employee as emp
              inner join hr_holidays as hol
                        on emp.id = hol.employee_id
              inner join hr_holidays_status as hol_status
                        on hol_status.id = hol.holiday_status_id
            where hol.type<>'add'
              and
              (
                (EXTRACT(YEAR FROM (hol.date_from))=%s and
                EXTRACT(MONTH FROM (hol.date_from))=%s)
               or
                (EXTRACT(YEAR FROM (hol.date_to))=%s and
                EXTRACT(MONTH FROM (hol.date_to))=%s)
              )
              and emp.id = %s
              and hol_status.active is true
              and state='validate'
            order by hol.date_from, hol.holiday_status_id
            '''

        # self.cr.execute(sql, (first_date.strftime(DTF),
        # last_date.strftime(DTF), emp_id))
        self.cr.execute(sql, (self.year,
                              self.month,
                              self.year,
                              self.month,
                              emp_id))
        # variabile da tornare: lista bidimensionale
        # con tutti gli utenti e tutti i giorni.
        # managed_holidays = []

        holidays = self.cr.dictfetchall()
        calculate_delta_obj = self.pool.get('hr.holidays')

        for hol in holidays:

            date_to = calculate_delta_obj.get_current_delta(self.cr, self.uid, [], hol['date_to'])
            date_from = calculate_delta_obj.get_current_delta(self.cr, self.uid, [], hol['date_from'])
            """
            hol_interval=self._get_interval_days(datetime.date(date_from),datetime.date(date_to))

            hol_range={}
            for i in hol_interval:
                hol_range[i]=0
            """

            hr_contract_obj = self.pool.get('hr.contract')

            contract_ids = hr_contract_obj.search(self.cr, self.uid,
                                            [('employee_id', '=', emp_id), ],
                                            order='date_start desc')
            if not contract_ids:
                # raise orm.except_orm(_('Invalid action !'),
                # _('The employee does not have a contract'))
                # raise Exception(_('The employee does not have a contract'))
                return False

            calendar_id = hr_contract_obj.browse(self.cr,
                                             self.uid,
                                             contract_ids[0]).working_hours.id
            if not calendar_id:
                # raise orm.except_orm(_('Invalid action !'),
                # _('The employee does not have a working hours'))
                # raise Exception(_('The employee does not have a working hours'))
                return False

            hol_range = self.holidays_Obj.get_holiday_range_date(self.cr,
                                            self.uid,
                                            self.context['active_ids'],
                                            date_to, date_from, calendar_id)

            # hol_working_range=self._get_working_days(hol_range,
            #    hol['holiday_status_id'])
            hol_working_range = self.holidays_Obj.get_working_days(self.cr,
                                    self.uid, hol_range,
                                    hol['holiday_status_id'])

            # emp_hol_hours4days = self._get_emp_hol_hours4days(emp_id,
            # float(hol['number_of_days_temp']),hol_working_range)
            emp_hol_hours4days = hol_working_range
            for k, v in emp_hol_hours4days.items():
                if (k in tot_range[hol['holiday_status_id']]):
                    tot_range[hol['holiday_status_id']][k] += v

        totals = self._build_totals_dict()

        total_holidays = {}
        for k in tot_range:
            keys_days = sorted(tot_range[k].keys())
            total_holidays[k] = []
            for day in keys_days:
                total_holidays[k].append(tot_range[k][day])
                totals[k] += tot_range[k][day]

        self.total_holidays_4days = tot_range
        self.total_holidays = total_holidays
        self.totals = totals

    def get_days(self):
        last_day = lengthmonth(self.year, self.month)
        days = []
        for i in range(1, last_day + 1, 1):
            days.append(i)
        return days

    def _build_totals_dict(self):
        totals = {}
        holiday_type = self.get_holiday_type()
        for t_type in holiday_type:
            totals[t_type['id']] = 0
        return totals

    def get_date(self):
        date = datetime(self.year, self.month, 1)
        return date.strftime("%B %Y")

    def _get_interval_days(self, date_from, date_to):
        days = (date_to - date_from).days + 1
        interval = []
        for i in range(days):
            date_act = date_from + timedelta(days=i)
            interval.append(date_act.strftime(DF))
        return interval

HeaderFooterTextWebKitParser('report.reportemployee',
                             'hr.employee',
                             os.path.dirname(os.path.realpath(__file__)) + '/template_holidays.mako',
                             parser=parser_holidays)
