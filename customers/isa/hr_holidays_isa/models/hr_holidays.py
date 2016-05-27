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

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.osv import orm, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta, time
from dateutil.rrule import rrule, DAILY
import decimal

import pytz
from openerp import SUPERUSER_ID


class hr_holidays_isa(orm.Model):

    _inherit = 'hr.holidays'

    _columns = {
        'number_of_days_temp': fields.float('N. Working Hours'),
    }

    def _check_date(self, cr, uid, ids):
        for holiday in self.browse(cr, uid, ids):
            holiday_ids = self.search(cr, uid, [('date_from', '<', holiday.date_to), ('date_to', '>', holiday.date_from), ('employee_id', '=', holiday.employee_id.id), ('id', '<>', holiday.id)])
            if holiday_ids:
                return False
        return True

    _constraints = [
        (_check_date, 'Non puoi inserire due richeste che si sovrappongono nello stesso giorno!', ['date_from','date_to']),
    ]

    _sql_constraints = [
        # ('type_value', "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL))", "You have to select an employee or a category"),
        ('date_check', "CHECK ( number_of_days_temp > 0 )", "The number of days must be greater than 0 !"),
        # ('date_check', "CHECK ( number_of_days_temp > 0 AND type='remove')", "The number of hours must be greater than 0 !"),
        # ('date_check1', "CHECK ( number_of_days_temp <> 0 AND type='add')", "The number of hours must be greater than 0 !"),
        ('date_check2', "CHECK ( (type='add') OR (date_from < date_to))", "The start date must be before the end date !"),
    ]

    def holidays_confirm(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids)[0]
        if record.date_to and record.date_from:

            hr_contract_obj = self.pool.get('hr.contract')

            contract_ids = hr_contract_obj.search(cr, uid,
                                                  [('employee_id', '=',
                                                    record.employee_id.id),
                                                   ],
                                                  order='date_start desc')
            if not contract_ids:
                raise orm.except_orm(_('Invalid action !'),
                                     _('The employee does not have a contract'))

            calendar_id = hr_contract_obj.browse(cr, uid,
                                                 contract_ids[0]).working_hours.id
            if not calendar_id:
                raise orm.except_orm(_('Invalid action !'),
                                     _('The employee does not have a working hours'))

            field_date_to = self.get_current_delta(cr, uid, ids,
                                                   record.date_to)
            field_date_from = self.get_current_delta(cr, uid, ids,
                                                     record.date_from)

            holidays_hours = self._get_holidays_hours(cr, uid, ids,
                                                      field_date_to,
                                                      field_date_from,
                                                      record.holiday_status_id.id,
                                                      calendar_id)
            t_number_of_days_temp = record.number_of_days_temp
            t_difference = abs(t_number_of_days_temp - holidays_hours)
            if t_number_of_days_temp != holidays_hours and t_difference > 0.001:
                raise orm.except_orm(_('Attention !'), _('The number of hours entered manually (%s) are different from those expected (%s)') % (record.number_of_days_temp, holidays_hours))

        res = super(hr_holidays_isa, self).holidays_confirm(cr,
                                                            uid,
                                                            ids,
                                                            context)
        return res

    def onchange_hol_status(self, cr, uid, ids, status,
                            date_to, date_from, employee_id, context=None):

        result = self.onchange_date_from(cr, uid, ids, date_to, date_from,
                                         status, employee_id)
        return result

    def onchange_empl(self, cr, uid, ids, date_to, date_from,
                      holiday_status_id, employee_id):
        result = self.onchange_date_from(cr, uid, ids, date_to, date_from,
                                         holiday_status_id, employee_id)

        result['value'].update({'department_id': False})
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            result['value'].update({'department_id': employee.department_id.id})
        return result

    def get_current_delta(self, cr, uid, ids, current_date):

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        user_pool = self.pool.get('res.users')
        user = user_pool.browse(cr, SUPERUSER_ID, uid)
        tz = pytz.utc
        if user.partner_id and user.partner_id.tz:
            tz = pytz.timezone(user.partner_id.tz)

        t_date = pytz.utc.localize(datetime.strptime(current_date, DATETIME_FORMAT)).astimezone(tz)
        t_date_string = str(t_date)[:19]
        final_date = datetime.strptime(t_date_string, DTF).replace(second=0)

        return final_date

    def onchange_date_from(self, cr, uid, ids, date_to, date_from,
                           holiday_status_id, employee_id):
        holidays_hours = 0
        if date_to and date_from:

            hr_contract_obj = self.pool.get('hr.contract')
            contract_ids = hr_contract_obj.search(cr, uid,
                                                  [('employee_id', '=',
                                                    employee_id),
                                                   ],
                                                  order='date_start desc')
            if not contract_ids:
                raise orm.except_orm(_('Invalid action !'),
                                     _('The employee does not have a contract'))

            calendar_id = hr_contract_obj.browse(cr, uid,
                                                 contract_ids[0]).working_hours.id
            if not calendar_id:
                raise orm.except_orm(_('Invalid action !'),
                                     _('The employee does not have a working hours'))

            field_date_to = self.get_current_delta(cr, uid, ids, date_to)
            field_date_from = self.get_current_delta(cr, uid, ids, date_from)

            holidays_hours = self._get_holidays_hours(cr, uid, ids,
                                                      field_date_to,
                                                      field_date_from,
                                                      holiday_status_id,
                                                      calendar_id)

        result = {}
        result['value'] = {
            'number_of_days_temp': holidays_hours,
        }
        return result

    def get_holiday_range_date(self, cr, uid, ids,
                               datetime_to, datetime_from, calendar_id):
        holiday_range_dates = {}
        for dt in rrule(DAILY,
                        dtstart=datetime_from.date(),
                        until=datetime_to.date()):
            work_time_intervals_of_weekday = self._get_work_time_intervals_of_weekday(cr, uid, ids, calendar_id, dt.weekday())
            daily_hours = self._get_daily_hours(cr, uid, ids, datetime_to, datetime_from, dt, work_time_intervals_of_weekday)
            holiday_range_dates[dt.strftime(DF)] = daily_hours
        return holiday_range_dates

    def _get_holidays_hours(self, cr, uid, ids,
                            datetime_to, datetime_from,
                            hol_type, calendar_id):
        holiday_range_dates = self.get_holiday_range_date(cr, uid, ids,
                                                          datetime_to,
                                                          datetime_from,
                                                          calendar_id)
        # elimina festivita o giorni di chiusura
        holiday_range_dates_get_working_days = self.get_working_days(cr, uid,
                                                                     holiday_range_dates, hol_type)
        holidays_hours = 0
        for daily_hours in holiday_range_dates_get_working_days.values():
            holidays_hours = holidays_hours + daily_hours
        return holidays_hours

    def _get_work_time_intervals_of_weekday(self, cr, uid, ids, calendar_id,
                                            week_day):
        res_cal_att_obj = self.pool.get('resource.calendar.attendance')
        calendar_ids = res_cal_att_obj.search(cr, uid,
                                              [('calendar_id',
                                                '=',
                                                calendar_id),
                                               ('dayofweek', '=', str(week_day))
                                               ])
        day_interval = []
        for i in res_cal_att_obj.browse(cr, uid, calendar_ids):
            day = {'hour_from': i.hour_from, 'hour_to': i.hour_to}
            day_interval.append(day)
        return day_interval

    def _get_daily_hours(self, cr, uid, ids, datetime_to, datetime_from,
                         date_act, work_time_intervals_of_weekday):
        total_time = timedelta(0)
        for interval in work_time_intervals_of_weekday:
            dt_interval_from = datetime.combine(date_act.date(),
                                                self._number_to_time(interval['hour_from']))
            dt_interval_to = datetime.combine(date_act.date(),
                                              self._number_to_time(interval['hour_to']))

            if not (datetime_to < dt_interval_from
                    or dt_interval_to < datetime_from):
                hours_from = max(datetime_from, dt_interval_from)
                hours_to = min(datetime_to, dt_interval_to)
                delta = hours_to - hours_from
                total_time = total_time + delta

        float_time = round((abs(total_time.seconds) / 3600.0), 2)
        return float_time

    def _number_to_time(self, numberTime):
        decimalTime = decimal.Decimal(str(numberTime))
        decimalHour = decimalTime
        decimalMinute = (decimalTime - int(decimalHour)) * 60
        decimalSecond = (decimalMinute - int(decimalMinute)) * 60
        newTime = time(hour=int(decimalHour),
                       minute=int(decimalMinute),
                       second=int(decimalSecond))
        return newTime

    def get_working_days(self, cr, uid, working_range, hol_type=False):
        festivities = self._get_festivities_orm(cr, uid)
        closed_days = self._get_closed_days_orm(cr, uid)
        this_holidays = {}
        this_closed_days = {}

        for festa in festivities:
            day = str(festa['day'])
            month = str(festa['month'])
            year = str(festa['year'])
            if len(day) == 1:
                day = '0' + day
            if len(month) == 1:
                month = '0' + month
            festivities_date = year + '-' + month + '-' + day
            this_holidays[festivities_date] = 1

        for closed in closed_days:
            weekday = str(closed['day'])
            hours = closed['hours']
            this_closed_days[weekday] = hours

        new_range = {}

        for k in working_range.keys():
            # east=self._east(self.year)
            type_allow_festivities = self._type_allow_festivities(cr, uid)
            type_allow_closed_days = self._type_allow_closed_days(cr, uid)
            dt = datetime.strptime(k, DF)
            day_included = True

            # festivities
            if hol_type in type_allow_festivities or hol_type is False:
                if k in this_holidays:
                    day_included = False

            # closed days
            # adds 1 unit to the method "weekday()" to fix the bug of Monday=0
            if hol_type in type_allow_closed_days or hol_type is False:
                if str((dt.weekday() + 1)) in this_closed_days:
                    diff_hours = working_range[k] - this_closed_days[str(dt.weekday()
                                                                         + 1)]
                    if diff_hours > 0:
                        working_range[k] = diff_hours
                    else:
                        working_range[k] = 0

            if day_included is True:
                new_range[k] = working_range[k]
        return new_range

    # ottengo i dati dalla prima company_id derivata dall'utente connesso
    def _get_festivities_orm(self, cr, uid):
        res_tab = self.pool.get('resource.resource')
        resource_ids = res_tab.search(cr, uid, [('user_id', '=', uid)])
        resource = res_tab.browse(cr, uid, resource_ids)
        hrs = self.pool.get('res.company.festivity')

        hrs_list = hrs.search(cr, uid,
                              [("company_id", "=",
                                resource[0].company_id.id)])
        orm_types = hrs.read(cr, uid,
                             hrs_list,
                             ['day', 'month', 'year'])
        return orm_types

    def _get_closed_days_orm(self, cr, uid):
        res_tab = self.pool.get('resource.resource')
        resource_ids = res_tab.search(cr, uid, [('user_id', '=', uid)])
        resource = res_tab.browse(cr, uid, resource_ids)
        hrs = self.pool.get('res.company.closed.day')
        hrs_list = hrs.search(cr, uid, [("company_id", "=",
                                         resource[0].company_id.id)])
        orm_types = hrs.read(cr, uid, hrs_list, ['day', 'hours'])
        return orm_types

    # ritorna le tipologie di permesso che comprendono i giorni di chiusura,per esempio la malattia
    # It returns the holidays types thath allow closed days, for example, sick leave
    def _type_allow_closed_days(self, cr, uid):
        hrs = self.pool.get('hr.holidays.status')
        hrs_list = hrs.search(cr, uid, [("active", "=", True),
                                        ("allow_closed_days", "=", True)])
        return hrs_list

    # ritorna le tipologie di permesso che comprendono i festivi,per esempio la malattia
    # It returns the holidays types thath allow destivities days, for example, sick leave
    def _type_allow_festivities(self, cr, uid):
        hrs = self.pool.get('hr.holidays.status')
        hrs_list = hrs.search(cr, uid, [("active", "=", True),
                                        ("allow_festivities", "=", True)])
        return hrs_list
