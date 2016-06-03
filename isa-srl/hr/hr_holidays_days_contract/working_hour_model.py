# -*- coding: utf-8 -*-
from openerp import models, api, _
from datetime import datetime
import datetime
from openerp.exceptions import Warning


class working_hour(models.Model):
    _inherit = 'hr.holidays'

    @api.onchange('date_from','employee_id','date_to','name')
    def _onchange_date_from(self):

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + datetime.timedelta(n)

        if (self.date_from and self.date_to) and (self.date_from > self.date_to):
            return {
                'warning': {
                    'title': "Date non congruenti",
                    'message': "Data iniziale maggiore di data finale",
                }
            }

        self.number_of_days_temp = 0
        if not self.date_from or not self.date_to or not self.employee_id:
            return
        contract = self.employee_id.contract_ids
        if not contract:
            return
        day_from = datetime.datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
        day_to = datetime.datetime.strptime(self.date_to, '%Y-%m-%d %H:%M:%S')
        exist_contract = False

        for single_date in daterange(day_from, day_to + datetime.timedelta(days=1)):
            current_contracts = self._get_contract(single_date,contract)

            if not current_contracts:
                continue
            calendar_attendance = current_contracts.working_hours.attendance_ids.filtered(lambda att: att.dayofweek == str(single_date.weekday()))
            if calendar_attendance:
                self.number_of_days_temp+=1

    def _get_contract(self,single_date,contract):
        current_contracts = contract.filtered(lambda c:
                                              datetime.datetime.strptime(c.date_start + ' 00:00:00',
                                                                         '%Y-%m-%d %H:%M:%S') <= single_date
                                              and
                                              (
                                                  (c.date_end and single_date <= datetime.datetime.strptime(
                                                      c.date_end + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
                                                  or
                                                  not c.date_end
                                              )
                                              )
        if current_contracts:
            current_contract = current_contracts[0]
            return current_contract
        return None

    def converter_cent(self, min):
        cent = int((min / 60) * 100)
        cent = str(cent)
        cent = cent.zfill(2)
        return cent

    def converter_minute(self,hour):
        if hour == 0:
            return 0.0
        res = 0;
        for c in range(1,hour+1):
            res+=60
        return res

    def converter_day(self,min):
        return round(min/480,3)
