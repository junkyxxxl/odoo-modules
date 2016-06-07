# -*- coding: utf-8 -*-

import time
from openerp import api, models
from openerp.exceptions import Warning
from datetime import datetime
import datetime

class ReportTrialBalance(models.AbstractModel):
    _name = 'report.hr_report.print_attendance'

    def lengthmonth(self, month, year):
        if month == 2 and ((year % 4 == 0)
                           and ((year % 100 != 0)
                                or (year % 400 == 0))):
            return [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]
        if month == 2:
                return [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]
        if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
            return [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
        return [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]

    def get_month(self):
        return {
            1:'Gennaio',
            2:'Febbraio',
            3:'Marzo',
            4:'Aprile',
            5:'Maggio',
            6:'Giugno',
            7:'Luglio',
            8:'Agosto',
            9:'Settembre',
            10:'Ottobre',
            11:'Novembre',
            12:'Dicembre'
        }

    def getWeekday(self,day):
        week = { 0: 'Lun',
                 1: 'Mar',
                 2: 'Mer',
                 3: 'Gio',
                 4: 'Ven',
                 5: 'Sab',
                 6: 'Dom'
        }
        return week.get(day)

    '''Presenze Contrattuali'''

    '''Ritorna una lista delle ore del mese lavorate per chi ha un solo contratto'''
    def get_work_days_contract(self, hours, data, e):
        res = []
        today = datetime.datetime.today()
        m = today.month.__str__()

        '''Se stampo il report del mese corrente, fino al giorno corrente avrò le ore effettive, negli altri giorni avrò zero'''
        if today.month.__int__() == data['form']['month'] and today.year.__int__() == data['form']['year']:
            first = datetime.datetime.strptime(str(data['form']['year']) + '-' + m + '-1','%Y-%m-%d')
            len_month = self.lengthmonth(m, data['form']['year'])
            for cont in range(1, today.day.__int__()+1):
                if first.weekday() != 5 and first.weekday() != 6:
                    res.append(hours.get(str(first.weekday())))
                else:
                    res.append(0.0)
                day = (first.day + 1).__str__()
                if day != str(32):
                    first = datetime.datetime.strptime(str(data['form']['year']) + '-' + m + '-' + day, '%Y-%m-%d')
            for cont2 in range(today.day.__int__(), len_month.__len__()):
                res.append(0.0)
            return res
        else:
            ''' Se il report non è del mese corrente'''
            first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-1','%Y-%m-%d')
            len_month = self.lengthmonth(data['form']['month'], data['form']['year'])
            for cont in range(1, len_month.__len__() + 1):
                if first.weekday() != 5 and first.weekday() != 6:
                    res.append(hours.get(str(first.weekday())))
                else:
                    res.append(0.0)
                day = (first.day + 1).__str__()
                if (len_month != 2 and cont != 29) or (cont == 29):
                    if day != str(self.lengthmonth(data['form']['month'], data['form']['year']).__len__() + 1):
                        first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' + day, '%Y-%m-%d')
            return res

    '''Ritorna una lista delle ore del mese lavorate per chi ha più di un contratto'''
    def get_work_days_more_contract_eff(self, data, e):
        today = datetime.datetime.today()  # giorno attuale
        m = today.month.__str__()
        res = []  # lista delle ore
        if today.month.__int__() == data['form']['month'] and today.year.__int__() == data['form']['year']:
            first = datetime.datetime.strptime(str(data['form']['year']) + '-' + m + '-1','%Y-%m-%d')
            len_month = self.lengthmonth(m, data['form']['year'])
            for cont in range(1, today.day.__int__()+1):
                contract_id = self.get_target_date_contract(first,e)
                hours = self.get_hour(self.env['hr.contract'].search([('id', '=', contract_id)]))
                if first.weekday() != 5 and first.weekday() != 6:
                    res.append(hours.get(str(first.weekday())))
                else:
                    res.append(0.0)
                a = (first.day + 1).__str__()
                if a != str(32):
                    first = datetime.datetime.strptime(str(data['form']['year']) + '-' + m + '-' + a, '%Y-%m-%d')
            for cont2 in range(today.day.__int__(), len_month.__len__()):
                res.append(0.0)
            return res
        else:
            first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-1','%Y-%m-%d')
            len_month = self.lengthmonth(data['form']['month'], data['form']['year'])
            for cont in range(1, len_month.__len__() + 1):
                contract_id = self.get_target_date_contract(first, e)
                hours = self.get_hour(self.env['hr.contract'].search([('id', '=', contract_id)]))
                if first.weekday() != 5 and first.weekday() != 6:
                        res.append(hours.get(str(first.weekday())))
                else:
                    res.append(0.0)
                a = (first.day + 1).__str__()
                if (len_month != 2 and cont != 29) or (cont == 29):
                    if a != str(self.lengthmonth(data['form']['month'], data['form']['year']).__len__() + 1):
                        first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' + a, '%Y-%m-%d')
            return res
        return


    '''Presenze Normalizzate'''

    '''Metodo che ritorna un dizionario in cui ad ogni giorno della settimana viene assegnato un numero di ore da svolgere (usato per
    i dipendenti che hanno un solo contratto'''
    def get_week_hour(self,e):
        contract = self.env['hr.contract'].search([('employee_id','=',e)]) #tipo di contratto del dipendente
        res = self.get_hour(contract)
        return res

    '''Recupero delle ore settimanali'''
    def get_hour(self,contract):
        hours = self.env['resource.calendar.attendance'].search([('calendar_id', '=', contract.working_hours.id)])
        test = {'0': 0,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0}
        for h in hours:
            dayofweek = h.dayofweek
            if test.get(dayofweek) != None:
                b = h.hour_to - h.hour_from
                a = b + test.get(dayofweek)
                test.update({dayofweek: a})
            else:
                test.update({dayofweek: h.hour_to - h.hour_from})
        return test


    def get_working_hour(self,hours,day, number_of_days):
        return hours.get(str(day))*number_of_days

    '''Ritorna una lista delle ore del mese lavorate per chi ha un solo contratto'''
    def get_work_days(self,hours,data,e, type):
        today = datetime.datetime.today()
        m = today.month.__str__()

        if today.month.__int__() == data['form']['month'] and today.year.__int__()==data['form']['year']:
            first = datetime.datetime.strptime(str(data['form']['year'])+'-'+m+'-1','%Y-%m-%d')
            res = []
            len_month = self.lengthmonth(m,data['form']['year'])
            for cont in range(1,today.day.__int__()+1):
                if first.weekday()!= 5 and first.weekday()!= 6:
                    if self.is_holiday(data, first, e) == None:
                        res.append(hours.get(str(first.weekday())))
                    else:
                        start = datetime.datetime.strptime((self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_from).split(" ")[0], '%Y-%m-%d')
                        end = datetime.datetime.strptime((self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_to).split(" ")[0], '%Y-%m-%d')
                        if not type:
                            res.append(hours.get(str(first.weekday())) -
                                   (self.get_working_hour(hours,first.weekday(),float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).number_of_days_temp)))/
                                   float(self.number_of_days(start,end,data)))
                        else:
                            res.append(hours.get(str(first.weekday())) -
                                       (float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).working_hour)) /
                                       float(self.number_of_days(start, end, data)))

                else:
                    res.append(0.0)
                day = (first.day +1).__str__()
                if day != str(32):
                    first = datetime.datetime.strptime(str(data['form']['year'])+'-'+m+'-'+day,'%Y-%m-%d')
            for cont2 in range(today.day.__int__(),len_month.__len__()):
                res.append(0.0)
            return res
        else: #se il report non è del mese corrente
            first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-1', '%Y-%m-%d')  # recupero il primo giorno del mese
            res = []
            len_month = self.lengthmonth(data['form']['month'],data['form']['year'])
            for cont in range(1, len_month.__len__()+1):
                if first.weekday() != 5 and first.weekday() != 6:
                    if self.is_holiday(data, first, e) == None:
                        res.append(hours.get(str(first.weekday())))
                    else:
                        if self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_from == self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_to:
                            if not type:
                                res.append(hours.get(str(first.weekday())) -
                                           (self.get_working_hour(hours, first.weekday(), float(
                                               self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first,e))]).number_of_days_temp))))
                            else:
                                res.append(hours.get(str(first.weekday())) -
                                           (float(self.env['hr.holidays'].search(
                                               [('id', '=', self.is_holiday(data, first, e))]).working_hour)))
                        else:
                            start = datetime.datetime.strptime((self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_from).split(" ")[0],'%Y-%m-%d')
                            end = datetime.datetime.strptime((self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_to).split(" ")[0],'%Y-%m-%d')
                            days = self.number_of_days(start,end,data)
                            if days !=0:
                                if not type:
                                    res.append(hours.get(str(first.weekday())) -
                                               (self.get_working_hour(hours, first.weekday(), float(
                                                   self.env['hr.holidays'].search([('id', '=',
                                                                                    self.is_holiday(data, first,
                                                                                                    e))]).number_of_days_temp)))/
                                           float(self.number_of_days(start,end,data)))
                                else:
                                    res.append(hours.get(str(first.weekday())) -
                                               (float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).working_hour)) /
                                               float(self.number_of_days(start, end, data)))
                            else:
                                if not type:
                                    res.append(hours.get(str(first.weekday())) -
                                               (self.get_working_hour(hours, first.weekday(), float(
                                                   self.env['hr.holidays'].search([('id', '=',
                                                                                    self.is_holiday(data, first,
                                                                                                    e))]).number_of_days_temp))))
                                else:
                                    res.append(hours.get(str(first.weekday())) -
                                               (float(self.env['hr.holidays'].search(
                                                   [('id', '=', self.is_holiday(data, first, e))]).working_hour)))

                else:
                    res.append(0.0)
                day = (first.day + 1).__str__()
                if (len_month!=2 and cont!=29) or (cont==29):
                    if day!=str(self.lengthmonth(data['form']['month'],data['form']['year']).__len__()+1):
                        first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' + day, '%Y-%m-%d')
            return res

    def is_holiday(self, data, date, e):
        first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-1 23:59:59',
                                           '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' + str(
            self.lengthmonth(data['form']['month'], data['form']['year']).__len__())+' 23:59:59', '%Y-%m-%d %H:%M:%S')
        holidays = self.env['hr.holidays'].search([('employee_id', '=', e), ('date_to', '>=', str(first)), ('date_to', '<=', str(end))])
        for h in holidays:
            holi,splitholi = str(h.date_from).split(" ")
            d,splidate = str(date).split(" ")
            if d == holi:
                return h.id

        for h in holidays:
            holi, splitholi = str(h.date_to).split(" ")
            d, splidate = str(date).split(" ")
            if d == holi:
                return h.id

        for h in holidays:
            if date>=datetime.datetime.strptime(h.date_from,'%Y-%m-%d %H:%M:%S') and date<=datetime.datetime.strptime(h.date_to,'%Y-%m-%d %H:%M:%S'):
                return h.id

        '''Se le ferie sono su più giorni la "date" potrebbe essere in un intervallo di ferie e non necessariamente il primo o l'ultimo giorno'''
        for h in holidays:
            day_from = str(h.date_from).split(" ")[0].split("-")[2]
            day_to = str(h.date_to).split(" ")[0].split("-")[2]
            date_target = str(date).split("-")[2]
            if day_from<=date_target and day_to>=date_target:
                return h.id
        return None

    ''' Recupera il contratto relativo alla target date'''
    def get_target_date_contract(self, target_date, e):
        contract = self.env['hr.contract'].search([('employee_id', '=', e)])
        for c in contract:
            start = c.date_start
            ys,ms,ds = start.split("-")
            start = datetime.datetime.strptime(ys + '-' + ms + '-'+ds, '%Y-%m-%d')
            if not c.date_end:
                end = c.date_end
                ye,me,de = end.split("-")
                end = datetime.datetime.strptime(ye + '-' + me + '-'+de, '%Y-%m-%d')
                if target_date >= start:
                    if target_date <= end:
                        return c.id #ritorno l'id della riga del contratto della settimana target
            else:
                if target_date >= start:
                        return c.id  # ritorno l'id della riga del contratto della settimana target
        return 0

    '''Ritorna una lista delle ore del mese lavorate per chi ha più di un contratto'''
    def get_work_days_more_contract(self, data,e, type):
        today = datetime.datetime.today()  # giorno attuale
        m = today.month.__str__()

        if today.month.__int__() == data['form']['month'] and today.year.__int__()==data['form']['year']:  # se il report è del mese corrente
            first = datetime.datetime.strptime(str(data['form']['year']) + '-' + m + '-1', '%Y-%m-%d')  # recupero il primo giorno del mese
            res = [] #lista delle ore
            len_month = self.lengthmonth(m,data['form']['year']) #lunghezza del mese
            for cont in range(1, today.day.__int__()+1):
                contract_id = self.get_target_date_contract(first, e) #mi ritorna il contratto relativo al giorno in esame
                hours = self.get_hour(self.env['hr.contract'].search([('id','=',contract_id)])) #recuper le ore del contratto relativo al giorno
                if first.weekday() != 5 and first.weekday() != 6:
                    if self.is_holiday(data, first, e) == None:
                        res.append(hours.get(str(first.weekday())))
                    else:
                        if self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_from == \
                                self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_to:
                            if not type:

                                res.append(hours.get(str(first.weekday())) -
                                           (self.get_working_hour(hours, first.weekday(), float(
                                               self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first,
                                                                                                           e))]).number_of_days_temp))))
                            else:
                                res.append(hours.get(str(first.weekday())) -
                                   (float(self.env['hr.holidays'].search(
                                       [('id', '=', self.is_holiday(data, first, e))]).working_hour)))

                        else:
                            start = datetime.datetime.strptime((self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_from).split(" ")[0], '%Y-%m-%d')
                            end = datetime.datetime.strptime((self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_to).split(" ")[0], '%Y-%m-%d')
                            days = self.number_of_days(start, end, data)
                            if days != 0:
                                if not type:

                                    res.append(hours.get(str(first.weekday())) -
                                           (self.get_working_hour(hours,first.weekday(),float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).number_of_days_temp)))/
                                           float(self.number_of_days(start, end, data)))
                                else:
                                    res.append(hours.get(str(first.weekday())) -
                                       (float(self.env['hr.holidays'].search(
                                           [('id', '=', self.is_holiday(data, first, e))]).working_hour)) /
                                       float(self.number_of_days(start, end, data)))
                            else:
                                if not type:
                                    res.append(hours.get(str(first.weekday())) -
                                           ((self.get_working_hour(hours,first.weekday(),float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).number_of_days_temp)))))
                                else:
                                    res.append(hours.get(str(first.weekday())) -
                                               (float(self.env['hr.holidays'].search(
                                                   [('id', '=', self.is_holiday(data, first, e))]).working_hour)))
                else:
                    res.append(0.0)
                a = (first.day + 1).__str__()
                if a != str(32):
                    first = datetime.datetime.strptime(str(data['form']['year']) + '-' + m + '-' + a, '%Y-%m-%d')
            for cont2 in range(today.day.__int__(), len_month.__len__()):
                res.append(0.0)
            return res
        else:  # se il report non è del mese corrente
            first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-1','%Y-%m-%d')  # recupero il primo giorno del mese
            res = []
            len_month = self.lengthmonth(data['form']['month'],data['form']['year'])
            for cont in range(1, len_month.__len__() + 1):
                contract_id = self.get_target_date_contract(first, e)  # mi ritorna il contratto relativo al giorno in esame
                hours = self.get_hour(self.env['hr.contract'].search([('id', '=', contract_id)]))  # recuper le ore del contratto relativo al giorno
                if first.weekday() != 5 and first.weekday() != 6:
                    if self.is_holiday(data, first, e) == None:
                        res.append(hours.get(str(first.weekday())))
                    else:
                        if self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_from == self.env[
                            'hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_to:
                            if not type:
                                res.append(hours.get(str(first.weekday())) -
                                           (self.get_working_hour(hours,first.weekday(),float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).number_of_days_temp))))
                            else:
                                res.append(hours.get(str(first.weekday())) -
                                   (float(self.env['hr.holidays'].search(
                                       [('id', '=', self.is_holiday(data, first, e))]).working_hour)))
                        else:
                            start = datetime.datetime.strptime((self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_from).split(" ")[0], '%Y-%m-%d')
                            end = datetime.datetime.strptime((self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).date_to).split(" ")[0], '%Y-%m-%d')
                            days = self.number_of_days(start, end, data)
                            if days != 0:
                                if not type:

                                    res.append(hours.get(str(first.weekday())) -
                                               (self.get_working_hour(hours, first.weekday(), float(
                                                   self.env['hr.holidays'].search([('id', '=',self.is_holiday(data, first,e))]).number_of_days_temp))) /
                                           float(self.number_of_days(start, end, data)))

                                else:
                                    res.append(hours.get(str(first.weekday())) -
                                       (float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).working_hour)) /
                                       float(self.number_of_days(start, end, data)))
                            else:
                                if not type:
                                    res.append(hours.get(str(first.weekday())) -(self.get_working_hour(hours,first.weekday(),float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).number_of_days_temp))))
                                else:
                                    res.append(hours.get(str(first.weekday())) -
                                            (float(self.env['hr.holidays'].search([('id', '=', self.is_holiday(data, first, e))]).working_hour)))
                else:
                    res.append(0.0)
                a = (first.day + 1).__str__()
                if (len_month != 2 and cont != 29) or (cont == 29):
                    if a!=str(self.lengthmonth(data['form']['month'],data['form']['year']).__len__()+1):
                        first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' + a, '%Y-%m-%d')
                #first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' + a, '%Y-%m-%d')
            return res
        return

    ''' Calcola il totale delle ore svolte dal dipendente'''
    def get_total_hour(self,list_hours):
        sum = 0;
        for h in list_hours:
            sum+=float(h)
        return sum

    '''Sezione per il recupero delle ore effettive'''

    'Metodo che calcola le ore effettive svolte dal dipendente'
    def get_real_hour(self,data,e):
        first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-1 00:00:00', '%Y-%m-%d %H:%M:%S')
        last = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']+1) + '-1 00:00:00','%Y-%m-%d %H:%M:%S')
        test = self.env['hr.attendance'].search([('employee_id','=',e),('name','>=',str(first)),('name','<=',str(last))])
        res = {} #tutte le ore mensili svolte
        uscite_per_servizio = {}
        for t in test:
            if t.action_desc.name != 'Uscita per servizio' and t.action_desc.name!='Rientro da servizio':
                date,hour = t.name.split(" ")
                list = res.get(date)
                if list != None:
                    list.append(hour)
                else:
                    list = []
                    list.append(hour)
                res.update({date:list})

        fin = {}
        for r in res:
            a = self.compute_hour(res.get(r))
            if a == -1:
                return [-1,r]
            fin.update({r:a})
        final = []
        for cont in range(1, self.lengthmonth(data['form']['month'],data['form']['year']).__len__()+1):
            day = str(datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-'+str(cont), '%Y-%m-%d')).split(" ")
            if fin.get(day[0])!=None:
                appr = fin.get(day[0]).split(":")
                final.append(appr[0]+'.'+self.converter_cent(float(appr[1])))
            else:
                final.append(float(0.0))
        return final

    '''Ritorno di un dizionario {giorno:ore svolte}'''
    def compute_hour(self,list):
        if list.__len__() %2 !=0:
            return -1

        if list.__len__() == 2:
            hour_to = datetime.datetime.strptime(list[0], '%H:%M:%S')
            hour_from = datetime.datetime.strptime(list[1], '%H:%M:%S')
            return str(hour_to - hour_from)
        else:
            hour_to_pm = datetime.datetime.strptime(list[0], '%H:%M:%S')
            hour_from_pm = datetime.datetime.strptime(list[1], '%H:%M:%S')
            hour_to_am = datetime.datetime.strptime(list[2], '%H:%M:%S')
            hour_from_am = datetime.datetime.strptime(list[3], '%H:%M:%S')
            res = (hour_to_pm - hour_from_pm) + (hour_to_am - hour_from_am)
            if(list.__len__()>4):
                hour_to_pm = datetime.datetime.strptime(list[4], '%H:%M:%S')
                hour_from_pm = datetime.datetime.strptime(list[5], '%H:%M:%S')
                res = res+ (hour_to_pm - hour_from_pm)
            return str(res)

    def converter_cent(self,min):
        cent = int(((min/60)*100))
        cent = str(cent)
        cent = cent.zfill(2)
        return cent

    '''Sezione per il recupero dei permessi'''
    def retrieve_holidays(self,data,e, type):
        first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-1 00:00:00','%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' +str(self.lengthmonth(data['form']['month'],data['form']['year']).__len__())+' 23:59:00','%Y-%m-%d %H:%M:%S')
        holidays = self.env['hr.holidays'].search([('employee_id','=',e),('date_to','>=',str(first)),('date_to','<=',str(end))])

        res = {}
        for h in holidays:
            list = []
            if res.get(h.holiday_status_id)!=None:
                list = res.get(h.holiday_status_id)
                list.append(h)
                res.update({h.holiday_status_id:list})
            else:
                list.append(h)
                res.update({h.holiday_status_id: list})

        for code in res:
            list = res.get(code)
            hour = []
            for cont in range(0,self.lengthmonth(data['form']['month'],data['form']['year']).__len__()):
                hour.append(0.00) #di base metto tutti zero, poi lo modificherò nei giorni di permesso
            for holiday in list:
                start = datetime.datetime.strptime(holiday.date_from,'%Y-%m-%d %H:%M:%S')
                end = datetime.datetime.strptime(holiday.date_to,'%Y-%m-%d %H:%M:%S')
                if start.day != end.day:
                    hour = self.set_hour(hour,start,end,holiday,data, type)
                else:
                    if not type:
                        hour.__setitem__(start.day -1,holiday.number_of_days_temp)
                    else:
                        hour.__setitem__(start.day - 1, holiday.working_hour)

            for l in range(0, hour.__len__()):
                hour[l] = '%.2f' % (hour[l])

            hour.append(self.get_total_hour(hour))
            res.update({code:hour})
        return res

    '''Metodo per contare i giorni tra due date'''
    def number_of_days(self,start,end,data):
        sum = 0
        if start.month == end.month:
            if start.day < end.day:
                for cont in range(start.day,end.day):
                    if start.weekday()!=5 and start.weekday()!=6:
                        sum+=1
                    n = start.day +1
                    start = datetime.datetime.strptime(str(data['form']['year'])+'-'+str(data['form']['month'])+'-'+str(n), '%Y-%m-%d')
                if end.weekday()!=5 and end.weekday()!=6:
                    sum += 1
            else:
                delta = (end-start).days
                sum = delta+1
        elif start.month < end.month:
            delta = end - start
            for day in range(0,delta.days+1):
                if start.weekday() != 5 and start.weekday() != 6:
                    sum +=1
                start = start + datetime.timedelta(days=1)
        return sum

    '''Settaggio delle ore di permesso su più giorni'''
    def set_hour(self,hour,start,end,holiday,data, type):
        days = self.number_of_days(start, end,data)
        if days == 0:
            days = 1
        if not type:
            hour_for_day = holiday.number_of_days_temp/days
        else:
            hour_for_day = holiday.working_hour / days
        if start.month == end.month:
            for cont in range(start.day,end.day):
                if start.weekday() != 5 and start.weekday() != 6:
                    hour[cont-1] = hour_for_day
                n = start.day + 1
                start = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' + str(n),'%Y-%m-%d')
            if end.weekday() != 5 and end.weekday() != 6:
                hour[end.day-1] = hour_for_day

        elif start.month < end.month:
            delta = end - start
            for day in range(0, delta.days + 1):
                if start.weekday() != 5 and start.weekday() != 6 and data['form']['month']==start.month:
                    hour[int(start.day) - 1] = hour_for_day
                start = start + datetime.timedelta(days=1)
            if end.weekday() != 5 and end.weekday() != 6:
                hour[end.day - 1] = hour_for_day
        return hour

    '''Sezione per il recupero degli straordinari'''
    def get_overtime(self,data,e):
        first = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-1 00:00:00','%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(str(data['form']['year']) + '-' + str(data['form']['month']) + '-' + str(
            self.lengthmonth(data['form']['month'], data['form']['year']).__len__()) + ' 00:00:00', '%Y-%m-%d %H:%M:%S')

        overtime = self.env['hr.overtime'].search([('employee_id','=',e),('date_from','>=',str(first)),('date_from','<=',str(end))])
        hour = []
        for cont in range(0,self.lengthmonth(data['form']['month'], data['form']['year']).__len__()):
            hour.append(0.0)

        for o in overtime:
            date,other = o.date_from.split(" ")
            y,m,d = date.split("-")
            hour[int(d)-1] = o.number_of_hours_temp
        hour.append(self.get_total_hour(hour))
        return hour

    def day(self,data,list):
        for x in range(0,list.__len__()):
            day = datetime.datetime.strptime(str(data['form']['year'])+"-"+str(data['form']['month'])+"-"+str(list[x])+" 00:00:00",'%Y-%m-%d %H:%M:%S')
            list[x] = str(str(list[x])+ " " + self.getWeekday(day.weekday()))
        return list


    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        selected_employee = data['form']['employee']
        month = data['form']['month']
        list_employee = []
        works = {}
        works_contract = {}
        real_works = {}
        list_holidays = {}
        list_overtime = {}
        info = 'Permessi/Ferie espressi in giorni lavorativi. Presenze contrattuali, Normalizzate, Straordinari espressi in ore.'

        type = False
        if self.env['hr.config.settings'].fields_get().get('module_hr_holidays_working_hour'):
            if self.env['hr.config.settings'].search([], limit=1, order="id DESC").module_hr_holidays_working_hour:
                type = True
                info = 'Permessi/Ferie, Presenze contrattuali, Presenze Normalizzate e Straordinari espressi in ore.'

        for e in selected_employee:
            employee = self.env['hr.employee'].search([('id','=',e)])
            list_employee.append(employee) #lista dei dipendenti selezionati
            contract = self.env['hr.contract'].search([('employee_id', '=', e)])  # tipo di contratto del dipendente


            '''Presenze Contrattuali'''
            if len(contract.ids) == 1:
                week_hour2 = self.get_week_hour(e)  # orario di lavoro dei dipendenti
                list_hour2 = self.get_work_days_contract(week_hour2, data, e)
            else:
                list_hour2 = self.get_work_days_more_contract_eff(data, e)
            list_hour2.append(self.get_total_hour(list_hour2))

            for l in range(0, list_hour2.__len__()):
                list_hour2[l] = '%.2f' % (list_hour2[l])

            works_contract.update({e: list_hour2})

            '''Presenze Normalizzate'''
            if len(contract.ids) == 1:
                week_hour = self.get_week_hour(e)  # orario di lavoro dei dipendenti
                list_hour = self.get_work_days(week_hour,data,e,type)
            else:
                list_hour = self.get_work_days_more_contract(data,e, type)
            list_hour.append(self.get_total_hour(list_hour))

            for l in range(0,list_hour.__len__()):
                list_hour[l] = '%.2f'%(list_hour[l])

            works.update({e:list_hour})

            '''Recupero delle ore effettive'''
            real_hour = self.get_real_hour(data,e)
            if real_hour[0] == -1:
                date = real_hour[1]
                raise Warning(("Errore: il dipendente "+ employee.name_related +" non ha inserito una timbratura nel giorno " + date))

            real_hour.append(self.get_total_hour(real_hour))
            for l in range(0, real_hour.__len__()):
                real_hour[l] = '%.2f'%(float(real_hour[l]))
            real_works.update({e:real_hour})

            '''Recupero dei permessi'''
            holidays = self.retrieve_holidays(data,e, type)
            list_holidays.update({e:holidays})

            '''Recupero Straordinari'''
            overtime = self.get_overtime(data,e)
            for l in range(0, overtime.__len__()):
                overtime[l] = '%.2f'%(overtime[l])
            verify = False
            for cont in range(0,overtime.__len__()):
                if overtime[int(cont)]!= '0.00':
                    verify = True

            if verify == True:
                list_overtime.update({e:overtime})
            else:
                list_overtime.update({e: [-1]})

        list = self.lengthmonth(month, data['form']['year'])
        list = self.day(data, list)
        data['form']['month'] = self.get_month().get(month)


        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'list_employee': list_employee,
            'test': works,
            'days': list,
            'real_hour':real_works,
            'holidays':list_holidays,
            'overtime':list_overtime,
            'works_contract': works_contract,
            'info':info
        }
        return self.env['report'].render('hr_report.print_attendance', docargs)