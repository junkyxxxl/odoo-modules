# -*- coding: utf-8 -*-

import time
from openerp import api, models
from openerp.exceptions import Warning
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


    def get_sum_for_month(self,user_id,startDate,finalDate):
        query = ('''
                    SELECT
                         sum(amount_untaxed)
                    FROM
                         account_invoice
                    WHERE
                        account_invoice.user_id = %s

                        AND account_invoice.date_invoice between %s and %s
                 ''')
        self.env.cr.execute(query, (user_id,startDate,finalDate))
        result = self.env.cr.dictfetchall()
        result = result[0].get('sum')
        return result


    def calculate_annual_invoice(self,year,salesagent_id):
        #year = int(data['form']['budget_year'])
        #salesagents_id = data['form']['salesagent'][0]
        user_obj = self.env['res.users'].search([('partner_id','=',salesagent_id)])
        user_id = user_obj.id
        list_year = []
        list_progressive = []
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
                type_invoice = 'out_invoice'
                queryResult = self.get_sum_for_month(user_id,startDate,finalDate)
                list_year.append(queryResult)

                if queryResult:
                    progressive = progressive + queryResult
                else:
                    progressive = 0
                list_progressive.append(progressive)
            return (list_year,list_progressive)
        return None


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
        #invoice_list = self.get_invoice_list(data)

        dictionary_result = {}
        for s in selected_salesagent:
            list_annual_invoice = self.calculate_annual_invoice(budget_year,s)
            salesagent = self.env['res.partner'].search([('id','=',s)])
            list_salesagent.append(salesagent) #lista degli agenti selezionati




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
            'invoice_deviation': invoice_deviation
        }

        return self.env['report'].render('account_report_primapaint.print_budget', docargs)