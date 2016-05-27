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
from openerp import pooler
# import time
from datetime import datetime  # , timedelta
# import copy
import os

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class parser_hol_remaining(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):

    def __init__(self, cr, uid, name, context):

        self.context = context
        self.hols_remaining = {}
        self.cr = cr
        self.uid = uid
        self.hol_types = self.get_holidays_type_by_orm(context)
        super(parser_hol_remaining, self).__init__(cr, uid, name, context)

        self.localcontext.update({
            'get_emps': self.get_employees,
            'get_date': self.get_date,
            'get_holiday_type': self.get_holiday_type,
            'get_remaining_holidays': self.get_remaining_holidays,
            'get_rem_holidays_by_type': self._get_rem_holidays_by_type,
            'get_desc_holiday_by_type': self.get_desc_holiday_by_type
        })

    def get_employees(self):
        sql_string_act_ids = '''
            select emp.id,res.name
            from hr_employee emp
            inner join resource_resource res on emp.resource_id=res.id
            where res.active=true and emp.department_id is not null
            and emp.id in (%s)
            order by res.name
        '''
        sql_string_no_act_ids = '''
            select emp.id,res.name
            from hr_employee emp
            inner join resource_resource res on emp.resource_id=res.id
            where res.active=true and emp.department_id is not null
            order by res.name
        '''
        if('active_ids' in self.context):
            id_string = ','.join(str(n) for n in self.context['active_ids'])
            sql = sql_string_act_ids % (id_string)
        else:
            sql = sql_string_no_act_ids
        self.cr.execute(sql)
        emps = self.cr.dictfetchall()
        return emps

    def get_holidays_type_by_orm(self, context):
        # hrs=self.pool.get('hr.holidays.status')
        hrs = pooler.get_pool(self.cr.dbname).get('hr.holidays.status')
        hrs_list = hrs.search(self.cr, self.uid, [])
        orm_types = hrs.read(self.cr, self.uid,
                             hrs_list,
                             ['id', 'name'],
                             context)
        types = []

        for k in orm_types:
            t_type = []
            t_type.append(k['name'])
            t_type.append(k['id'])
            types.append(t_type)
        return types

    def get_holiday_type(self):
        return self.hol_types

    def get_remaining_holidays(self, emp_id):
        # hrs=self.pool.get('hr.holidays.status')
        hrs = pooler.get_pool(self.cr.dbname).get('hr.holidays.status')
        hrs_list = hrs.search(self.cr, self.uid, [])
        # self.hol_types=hrss.read(self.cr,self.uid,hrs_list,['id','name'])
        self.hols_remaining = hrs.get_days(self.cr,
                                           self.uid,
                                           hrs_list,
                                           emp_id, 0)

    def _get_rem_holidays_by_type(self, hol_type):
        if(hol_type in self.hols_remaining):
            return self.hols_remaining[hol_type].values()
        return 0

    def get_desc_holiday_by_type(self, hol_type):
        if(hol_type in self.hols_remaining):
            return self.hols_remaining[hol_type].keys()
        return 0

    def get_date(self):
        date = datetime.today()
        return date.strftime("%d %B %Y")

HeaderFooterTextWebKitParser('report.holidays',
                             'hr.employee',
                             os.path.dirname(os.path.realpath(__file__)) + '/holidays_rem.mako',
                             parser=parser_hol_remaining)
