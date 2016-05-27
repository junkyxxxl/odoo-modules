# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
import datetime

class working_hour(models.Model):
    _inherit = 'hr.holidays'

    working_hour = fields.Float(default=0)

    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id

    @api.onchange('date_from','employee_id','date_to')
    def onchange_date_from(self):

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + datetime.timedelta(n)

        self.working_hour = 0
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
            hh_start = 0
            hh_end = 0.0

            if not current_contracts:
                continue
            calendar_attendance = current_contracts.working_hours.attendance_ids.filtered(lambda att: att.dayofweek == str(single_date.weekday()))

            #se il permesso è di un solo giorno il day from e il day_to combaciano con il single date
            if single_date.date() == day_from.date():
                hh_start = day_from.time()
            if single_date.date() == day_to.date():
                hh_end = day_to.time()

            #primo gg e 1 gg di ferie
            if hh_start!=0.0 and hh_end!=0.0:
                if not calendar_attendance:
                    return {
                        'warning': {'title': "Warning", 'message': "Il dipendente non ha turni in questa giornata"},
                    }
                hour_from = float(hh_start.hour + 2) + float('0.' + self.converter_cent(float(hh_start.minute)))
                hour_to = float(hh_end.hour + 2) + float('0.' + self.converter_cent(float(hh_end.minute)))

                for c in calendar_attendance:
                    exist_contract = True
                    if hour_from >= c.hour_from and hour_to <= c.hour_to:
                        self.working_hour += float(hour_to - hour_from)
                    elif hour_from >= c.hour_from and hour_to >= c.hour_to and hour_from<=c.hour_to:
                        self.working_hour += float(c.hour_to - hour_from)
                    elif hour_from <= c.hour_from and hour_to <= c.hour_to and hour_to >= c.hour_from:
                        self.working_hour += float(hour_to - c.hour_from)
                    elif hour_from <= c.hour_from and hour_to <= c.hour_to and hour_to <= c.hour_from:
                        self.working_hour += 0
                    elif hour_from <= c.hour_from and hour_to >= c.hour_to:
                        self.working_hour += float(c.hour_to - c.hour_from)

            #devo considerare come start l'ora inserita e come end l'ora di fine turno (primo giorno su più gg di permesso)
            if hh_end == 0.0 and hh_start!= 0.0:
                for c in calendar_attendance:
                    exist_contract = True
                    if hh_start.hour+2 >= c.hour_from and hh_start.hour+2 <= c.hour_to:
                        hour_from = float(hh_start.hour+2) + float('0.'+self.converter_cent(float(hh_start.minute)))
                        self.working_hour += float(c.hour_to - hour_from)
                    else:
                        self.working_hour += float(c.hour_to) - float(c.hour_from)

            #giorni intermedi, si contano l'orario di inzio e fine turno
            if hh_end == 0.0 and hh_start == 0.0:
                for c in calendar_attendance:
                    exist_contract = True
                    self.working_hour += float(c.hour_to - c.hour_from)

            #ultimo giorno : lo start è l'inizio del turno e l'end è la data inserita
            if hh_end!=0.0 and hh_start == 0.0:
                hour_to = float(hh_end.hour + 2) + float('0.' + self.converter_cent(float(hh_end.minute)))
                for c in calendar_attendance:
                    exist_contract = True
                    if hour_to <= c.hour_to and hour_to>= c.hour_from:
                        self.working_hour += float(hour_to-c.hour_from)
                    elif hour_to >= c.hour_to and hour_to>= c.hour_from:
                        self.working_hour += float(c.hour_to - c.hour_from)
                    elif hour_to >= c.hour_to and hour_to>= c.hour_from:
                        self.working_hour += 0

        if not exist_contract:
            return {
                'warning': {'title': "Warning", 'message': "Il dipendente non ha turni nei giorni selezionati"},
            }

        self.number_of_days_temp = self.converter_day(float(self.working_hour % 1) + self.converter_minute(int(self.working_hour)))

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
        return round(min/1440,3)
