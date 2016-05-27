# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.report import report_sxw
import os

from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class parser_exporter_statements(report_sxw.rml_parse):
    _name = 'parser.exporter.statements'

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        self.partner_id = None
        self.exporter_id = None
        self.first_name = ''
        self.surname = ''
        self.vat = ''
        self.date = None
        self.city = None
        self.province = None
        self.res_name = ''
        self.res_street = ''
        self.res_zip = ''
        self.res_city = ''
        self.res_province = ''
        self.gender = ''
        self.letter_type = ''
        self.period_start = None
        self.period_end = None
        super(parser_exporter_statements,
              self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_wizard_params':self._get_wizard_params,
            'get_first_name':self._get_first_name,
            'get_surname':self._get_surname,
            'get_partner_id': self._get_partner_id,
            'get_exporter_id': self._get_exporter_id,
            'get_vat_code': self._get_vat_code,
            'get_date_day': self._get_date_day,
            'get_date_month': self._get_date_month,
            'get_date_year': self._get_date_year,
            'get_city': self._get_city,
            'get_province': self._get_province,
            'get_res_name': self._get_res_name,
            'get_res_street': self._get_res_street,
            'get_res_zip': self._get_res_zip,
            'get_res_city': self._get_res_city,
            'get_res_province': self._get_res_province,
            'get_gender': self._get_gender,
            'get_letter_type': self._get_letter_type,
            'get_day_period_start': self._get_day_period_start,
            'get_day_period_end': self._get_day_period_end,
            'get_month_period_start': self._get_month_period_start,
            'get_month_period_end': self._get_month_period_end,
        })
        
    def _get_wizard_params(self, partner_id, exporter_id):
        res_obj = self.pool.get('res.partner')
        exp_obj = self.pool.get('account.exporter.statements')
        self.partner_id = partner_id
        self.exporter_id = exporter_id
        res = res_obj.browse(self.cr, self.uid, self.partner_id)
        res_exporter = exp_obj.browse(self.cr, self.uid, self.exporter_id)
        self.res_name = res.name
        self.res_street = res.street
        self.res_zip = res.zip
        self.res_city = res.city
        self.res_province = ''
        if res.province:
            self.res_province = res.province.code
        self.first_name = res.person_name
        self.surname = res.person_surname
        self.vat = res.vat
        self.date = res.birth_date
        self.city = ''
        if res.birth_city_id:
            self.city = res.birth_city_id.name
        self.gender = res.sex
        self.province = ''
        if res.birth_city_id and res.birth_city_id.province_id:
            self.province = res.birth_city_id.province_id.code
        self.letter_type = res_exporter.letter_type
        self.period_start = res_exporter.period_start
        self.period_end = res_exporter.period_end
    
    def _get_partner_id(self):
        return self.partner_id
    
    def _get_surname(self):
        return self.surname
    
    def _get_exporter_id(self):
        return self.exporter_id
    
    def _get_vat_code(self):
        return self.vat
    
    def _get_first_name(self):
        return self.first_name
    
    def _get_date_day(self):
        if self.date:
            return str(self.date[8:10])
        return ''
    
    def _get_date_month(self):
        if self.date:
            return str(self.date[5:7])
        return ''
    
    def _get_date_year(self):
        if self.date:
            return str(self.date[:4])
        return ''
    
    def _get_province(self):
        return self.province
    
    def _get_city(self):
        return self.city
    
    def _get_res_name(self):
        return self.res_name
    
    def _get_res_street(self):
        return self.res_street
    
    def _get_res_zip(self):
        return self.res_zip
    
    def _get_res_city(self):
        return self.res_city
    
    def _get_res_province(self):
        return self.res_province
    
    def _get_gender(self):
        return self.gender
    
    def _get_letter_type(self):
        return self.letter_type
    
    def _get_day_period_start(self):
        return str(self.period_start[8:10])
    
    def _get_day_period_end(self):
        return str(self.period_end[8:10])
    
    def _get_month_period_start(self):
        return str(self.period_start[5:7])
    
    def _get_month_period_end(self):
        return str(self.period_end[5:7])
    
HeaderFooterTextWebKitParser('report.exporter_statement_report',
                             'account.exporter.statements',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                                '/exporter_statements.mako',
                             parser=parser_exporter_statements)
