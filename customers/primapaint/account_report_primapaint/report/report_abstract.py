# -*- coding: utf-8 -*-

import time
from openerp import api, models
from openerp.exceptions import ValidationError, Warning
from datetime import datetime
import datetime

class ReportTrial(models.AbstractModel):
    _name = 'report.account_report_primapaint.print_budget'


    def calculate_day_of_month(self, month, year):
        if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
            return 29
        if month == 2:
            return 28
        if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
            return 31
        return 30


    def get_sum_for_month(self,user_id,categ_id,startDate,finalDate):
        query1 = ('''
                    SELECT
                         sum(price_total)
                    FROM
                         account_invoice_report
                    WHERE
                        account_invoice_report.user_id = %s
                        AND account_invoice_report.categ_id = %s
                        AND account_invoice_report.date between %s and %s
                 ''')

        self.env.cr.execute(query1, (user_id,categ_id,startDate,finalDate))
        result1 = self.env.cr.dictfetchall()
        if not result1[0].get('sum'):
            result1 = 0
        else:
            result1 = result1[0].get('sum')

        return result1


    def calculate_annual_invoice(self,year,salesagent_id,categ_id):
        user_obj = self.env['res.users'].search([('partner_id','=',salesagent_id)])
        user_id = user_obj.id
        lista_mese = []
        lista_progressive = []
        progressive = 0
        if user_id:
            for i in range (1,13):
                if i<10:
                     month = '0'+str(i)
                     startDate = str(year) + '-' + month + '-' + '01'
                else:
                     month = str(i)
                     startDate = str(year) + '-' + month + '-' + '01'

                day_of_month = self.calculate_day_of_month(i,year)
                finalDate = str(year) + '-' + month + '-' + str(day_of_month)
                queryResult = self.get_sum_for_month(user_id,categ_id,startDate,finalDate)
                lista_mese.append(queryResult)

                if queryResult:
                    progressive = progressive + queryResult
                else:
                    progressive = progressive + 0
                lista_progressive.append(progressive)
            return (lista_mese,lista_progressive)
        return None


    def calculate_diff(self,lista2,lista1):
        lista_scostamento_mese = []
        lista_scostamento_prog = []
        list1 = lista1[0]
        list2 = lista2[0]
        list3 = lista1[1]
        list4 = lista2[1]
        cont1 = 0
        cont2 = 0
        while cont1<12:
                if list2[cont1] and list1[cont1]:
                    resto_percentuale1 = (list2[cont1]-list1[cont1])/list1[cont1]
                    elemento1 = resto_percentuale1*100
                else:
                    elemento1 = 0
                lista_scostamento_mese.append(elemento1)
                cont1 = cont1+1
        while cont2<12:
                if list4[cont2] and list3[cont2]:
                    resto_percentuale2 = (list4[cont2]-list3[cont2])/list3[cont2]
                    elemento2 = resto_percentuale2*100
                else:
                    elemento2 = 0
                lista_scostamento_prog.append(elemento2)
                cont2 = cont2+1

        return (lista_scostamento_mese,lista_scostamento_prog)


    def calculate_annual_budget(self,year,salesagent_id,category):
        account_fiscalyear_obj = self.env['account.fiscalyear'].search([('code','=',year)])
        salesagent_target_obj = self.env['salesagent.target'].search([('salesagent_id','=',salesagent_id), ('year_id','=',account_fiscalyear_obj.id), ('categ_id','=',category[0])])
        salesagent_target_id = salesagent_target_obj.id
        list_mese = []
        list_progressivo = []
        elemento2 = 0
        if salesagent_target_id:
            salesagent_target_line_ids = self.env['salesagent.target.line'].search([('salesagent_target_id', '=', salesagent_target_id)])
            for target_line_id in salesagent_target_line_ids:
                elemento1 = target_line_id.target
                elemento2 = elemento2 + elemento1
                list_mese.append(elemento1)
                list_progressivo.append(elemento2)
            return (list_mese,list_progressivo)

        list_mese = [0,0,0,0,0,0,0,0,0,0,0,0]
        list_progressivo = [0,0,0,0,0,0,0,0,0,0,0,0]
        return (list_mese, list_progressivo)


    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        selected_salesagent = data['form']['salesagent']
        budget_year = data['form']['budget_year']
        last_year = int(budget_year)-1
        category = data['form']['category']
        invoice_deviation = str(budget_year) +'/'+ str(last_year)
        list_salesagent = []

        if not selected_salesagent:
            raise Warning("Non è stato selezionato nessun agente")
        else:
            fatturato_anno_precedente_mese = {}
            fatturato_anno_precedente_progressivo = {}
            fatturato_anno_corso_mese = {}
            fatturato_anno_corso_progressivo = {}
            scostamento_fatt_mese = {}
            scostamento_fatt_progressivo = {}
            budget_anno_precedente_mese = {}
            budget_anno_precedente_progressivo = {}
            budget_anno_corso_mese = {}
            budget_anno_corso_progressivo = {}
            scostamento_budget_mese = {}
            scostamento_budget_progressivo = {}


            for s in selected_salesagent:
                lista_fatturato_annuale_precedente = self.calculate_annual_invoice(int(last_year),int(s),int(category[0]))
                lista_fatturato_annuale_corso = self.calculate_annual_invoice(int(budget_year),int(s),int(category[0]))
                lista_scostamento_fatt = self.calculate_diff(lista_fatturato_annuale_corso,lista_fatturato_annuale_precedente)
                lista_budget_annuale_precedente = self.calculate_annual_budget(int(last_year),int(s),category)
                lista_budget_annuale_corso = self.calculate_annual_budget(int(budget_year),int(s),category)
                lista_scostamento_budget = self.calculate_diff(lista_budget_annuale_corso,lista_budget_annuale_precedente)
                salesagent = self.env['res.partner'].search([('id','=',s)])
                list_salesagent.append(salesagent)

                listElement1 = fatturato_anno_precedente_mese.get(salesagent, [])
                listElement1.append(lista_fatturato_annuale_precedente[0])
                fatturato_anno_precedente_mese.update({s: listElement1})

                listElement2 = fatturato_anno_precedente_progressivo.get(salesagent, [])
                listElement2.append(lista_fatturato_annuale_precedente[1])
                fatturato_anno_precedente_progressivo.update({s: listElement2})

                listElement3 = fatturato_anno_corso_mese.get(salesagent, [])
                listElement3.append(lista_fatturato_annuale_corso[0])
                fatturato_anno_corso_mese.update({s: listElement3})

                listElement4 = fatturato_anno_corso_progressivo.get(salesagent, [])
                listElement4.append(lista_fatturato_annuale_corso[1])
                fatturato_anno_corso_progressivo.update({s: listElement4})

                listElement5 = scostamento_fatt_mese.get(salesagent, [])
                listElement5.append(lista_scostamento_fatt[0])
                scostamento_fatt_mese.update({s: listElement5})

                listElement6 = scostamento_fatt_progressivo.get(salesagent, [])
                listElement6.append(lista_scostamento_fatt[1])
                scostamento_fatt_progressivo.update({s: listElement6})

                listElement7 = budget_anno_precedente_mese.get(salesagent, [])
                listElement7.append(lista_budget_annuale_precedente[0])
                budget_anno_precedente_mese.update({s: listElement7})

                listElement8 = budget_anno_precedente_progressivo.get(salesagent, [])
                listElement8.append(lista_budget_annuale_precedente[1])
                budget_anno_precedente_progressivo.update({s: listElement8})

                listElement9 = budget_anno_corso_mese.get(salesagent, [])
                listElement9.append(lista_budget_annuale_corso[0])
                budget_anno_corso_mese.update({s: listElement9})

                listElement10 = budget_anno_corso_progressivo.get(salesagent, [])
                listElement10.append(lista_budget_annuale_corso[1])
                budget_anno_corso_progressivo.update({s: listElement10})

                listElement11 = scostamento_budget_mese.get(salesagent, [])
                listElement11.append(lista_scostamento_budget[0])
                scostamento_budget_mese.update({s: listElement11})

                listElement12 = scostamento_budget_progressivo.get(salesagent, [])
                listElement12.append(lista_scostamento_budget[1])
                scostamento_budget_progressivo.update({s: listElement12})


            docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'data': data['form'],
                'docs': docs,
                'time': time,
                'list_salesagent': list_salesagent,
                'category': category,
                'budget_year': budget_year,
                'last_year': last_year,
                'invoice_deviation': invoice_deviation,
                'fatturato_anno_precedente_mese': fatturato_anno_precedente_mese,
                'fatturato_anno_precedente_progressivo': fatturato_anno_precedente_progressivo,
                'fatturato_anno_corso_mese': fatturato_anno_corso_mese,
                'fatturato_anno_corso_progressivo': fatturato_anno_corso_progressivo,
                'scostamento_fatt_mese': scostamento_fatt_mese,
                'scostamento_fatt_progressivo': scostamento_fatt_progressivo,
                'budget_anno_precedente_mese': budget_anno_precedente_mese,
                'budget_anno_precedente_progressivo': budget_anno_precedente_progressivo,
                'budget_anno_corso_mese': budget_anno_corso_mese,
                'budget_anno_corso_progressivo': budget_anno_corso_progressivo,
                'scostamento_budget_mese': scostamento_budget_mese,
                'scostamento_budget_progressivo': scostamento_budget_progressivo,
            }

            return self.env['report'].render('account_report_primapaint.print_budget', docargs)