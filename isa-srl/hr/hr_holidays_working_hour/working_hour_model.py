# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
import datetime
import openerp.addons.decimal_precision as dp


class working_hour(models.Model):
    _inherit = 'hr.holidays'

    working_hour = fields.Float(string = "Ore", default=0, digits=dp.get_precision('Hour holidays'))

    @api.model
    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id

    @api.onchange('date_from','employee_id','date_to')
    def _onchange_date_from(self):
    
        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + datetime.timedelta(n)

        if not self._context.get('no_recompute_days', False):
            super(working_hour, self)._onchange_date_from()

        self.working_hour = 0

        if not self.date_from or not self.date_to or not self.employee_id:
            return
        contract = self.employee_id.contract_ids
        if not contract:
            return
        day_from = datetime.datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
        day_to = datetime.datetime.strptime(self.date_to, '%Y-%m-%d %H:%M:%S')

        for single_date in daterange(day_from.date(), day_to.date() + datetime.timedelta(days=1)):
            single_date = datetime.datetime.strptime(str(single_date)+" 00:00:00" ,'%Y-%m-%d %H:%M:%S')
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
                hour_from = float(hh_start.hour + 2) + float('0.' + self.converter_cent(float(hh_start.minute)))
                hour_to = float(hh_end.hour + 2) + float('0.' + self.converter_cent(float(hh_end.minute)))

                for c in calendar_attendance:
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
                    if hh_start.hour+2 >= c.hour_from and hh_start.hour+2 <= c.hour_to:
                        hour_from = float(hh_start.hour+2) + float('0.'+self.converter_cent(float(hh_start.minute)))
                        self.working_hour += float(c.hour_to - hour_from)
                    elif hh_start.hour +2 >= c.hour_from and hh_start.hour +2 >= c.hour_to:
                        continue
                    else:
                        self.working_hour += float(c.hour_to) - float(c.hour_from)

            #giorni intermedi, si contano l'orario di inzio e fine turno
            if hh_end == 0.0 and hh_start == 0.0:
                for c in calendar_attendance:
                    self.working_hour += float(c.hour_to - c.hour_from)

            #ultimo giorno : lo start è l'inizio del turno e l'end è la data inserita
            if hh_end!=0.0 and hh_start == 0.0:
                hour_to = float(hh_end.hour + 2) + float('0.' + self.converter_cent(float(hh_end.minute)))
                for c in calendar_attendance:
                    if hour_to <= c.hour_to and hour_to>= c.hour_from:
                        self.working_hour += float(hour_to-c.hour_from)
                    elif hour_to >= c.hour_to and hour_to>= c.hour_from:
                        self.working_hour += float(c.hour_to - c.hour_from)
                    elif hour_to >= c.hour_to and hour_to>= c.hour_from:
                        self.working_hour += 0

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

    ''' '''
    @api.model
    def _convert_day_to_hour(self):
        records = self.env['hr.holidays'].search([], order="id DESC")
        for record in records:
            res = record.with_context(no_recompute_days=True)._onchange_date_from()
