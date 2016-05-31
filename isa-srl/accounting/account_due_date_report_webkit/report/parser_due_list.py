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
import copy
from openerp.report import report_sxw
from openerp.tools.translate import _
import os
from datetime import datetime, date, timedelta
from openerp.osv import orm, fields

from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class account_due_list_report_ext_isa(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    _name = 'account.due.list.report.ext.isa'

    def __init__(self, cursor, uid, name, context):
        self.cr = cursor
        self.uid = uid

        self.context = context
        super(account_due_list_report_ext_isa, self).__init__(cursor, uid, name, context)

        company = self.pool.get('account.due.list.report').browse(self.cr, self.uid, self.parents['active_id']).company_id
        self.mode = self.pool.get('account.due.list.report').browse(self.cr, self.uid, self.parents['active_id']).mode
        self.print_customers = self.pool.get('account.due.list.report').browse(self.cr, self.uid, self.parents['active_id']).print_customers
        self.print_suppliers = self.pool.get('account.due.list.report').browse(self.cr, self.uid, self.parents['active_id']).print_suppliers
        self.type = self.pool.get('account.due.list.report').browse(self.cr, self.uid, self.parents['active_id']).type
        self.all_partner = self.pool.get('account.due.list.report').browse(self.cr, self.uid, self.parents['active_id']).all_partner
        self.filters = [('date_maturity', '!=', False),
                        ('reconcile_id', '=', False),
                        ('company_id','=',company.id),
                        ('date_maturity','!=',None)]
        self.partners = []
        header_report_name = ' - '.join((_('SCADENZARIO'), company.name, company.currency_id.name))

        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('Scadenzario'),
            'get_wizard_params':self.get_wizard_params,
            'get_move_line':self._get_move_line,
            'get_reconcile_name':self.get_reconcile_name,
            'get_maturity':self._get_maturity,
            'get_partner_name':self._get_partner_name,
            'get_residual':self._get_residual,
            'get_mode':self._get_mode,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_mode(self):
        if self.mode == 'tomature':
            return True
        else:
            return False

    def _get_maturity(self,Maturity,Actual,Lower, Higher):
        t = Maturity.split('-')
        dateMaturity = date(int(t[0]),int(t[1]),int(t[2]))
        t = Actual.split('-')
        dateActual = date(int(t[0]),int(t[1]),int(t[2]))
        rangeLower = timedelta(Lower)
        rangeHigher = timedelta(Higher)
        
        if self.mode == 'tomature':
            if Higher == 0 and Lower == 0:
                if dateMaturity < dateActual:
                    return True
                else:
                    return False
            
            if Higher < Lower:
                if dateMaturity>dateActual+rangeLower:
                    return True
                else:
                    return False
             
            if (dateMaturity >= dateActual+rangeLower) and (dateMaturity < dateActual + rangeHigher):
                return True
            else:
                return False
            
        if self.mode == 'matured':
            if Higher == 0 and Lower == 0:
                if dateMaturity >= dateActual:
                    return True
                else:
                    return False
            
            if Higher < Lower:
                if dateMaturity<dateActual-rangeLower:
                    return True
                else:
                    return False
             
            if (dateMaturity >= dateActual-rangeHigher) and (dateMaturity < dateActual - rangeLower):
                return True
            else:
                return False            

    def get_wizard_params(self, date, partner):

        if partner :
            self.partners = partner
        
        domain = ['|', '&', ('account_id.type', '=', 'payable'), ('debit', '=', 0), '&', ('account_id.type', '=', 'receivable'), ('credit', '=', 0)]
        for i in domain:
            self.filters.append(i)
    
    def _get_move_line(self):
        move_lines = []
        hrs = self.pool.get('account.move.line')

        test = self.partners
        if self.all_partner or len(self.partners)==0:
            test = self.pool.get('res.partner').search(self.cr, self.uid,[('id', '!=', None)])

        for partner in test:
            if self.type == 'debit':
                partner = self.pool.get('res.partner').search(self.cr, self.uid, [('customer','=',True),('id','=',partner)])
                for id in partner:
                    lines = self.pool.get('account.move.line').search(self.cr,self.uid,[('partner_id', '=', id),('account_id.type','=','receivable'),('date_maturity','!=',False)])
                    move_lines.append(hrs.browse(self.cr, self.uid, lines))
                    if len(move_lines[-1].ids)>0:
                        move_lines[-1].partner=move_lines[-1][0].partner_id
            if self.type == 'credit':
                partner = self.pool.get('res.partner').search(self.cr, self.uid, [('supplier','=',True),('id','=',partner)])
                for id in partner:
                    lines = self.pool.get('account.move.line').search(self.cr,self.uid,[('partner_id', '=', id),('account_id.type','=','payable'),('date_maturity','!=',False)])
                    move_lines.append(hrs.browse(self.cr, self.uid, lines))
                    if len(move_lines[-1].ids)>0:
                        move_lines[-1].partner=move_lines[-1][0].partner_id
            
        final_move_lines = []
        
        for move_partner_line in move_lines:
            move_lines_ids = []
            for move_line in move_partner_line:
                if move_line.account_id:
                    if (move_line.account_id.type == 'payable'):
                        if move_line.partner_id.property_account_payable == move_line.account_id:
                            move_lines_ids.append(move_line.id)
                    elif (move_line.account_id.type == 'receivable'):
                        if move_line.partner_id.property_account_receivable == move_line.account_id:
                            move_lines_ids.append(move_line.id)
        
            move_lines_ids = list(set(move_lines_ids))
            final_move_lines.append(hrs.browse(self.cr, self.uid, move_lines_ids))
        
        return final_move_lines
    
    def _get_partner_name(self,partner_id):
        partner_obj = self.pool.get('res.partner')
        name= partner_obj.browse(self.cr, self.uid, partner_id).name
        return name
    
    def _get_residual(self,reconcile_ref):
        move_obj = self.pool.get('account.move.line')
        move_ids = move_obj.search(self.cr, self.uid,[('reconcile_ref','=',reconcile_ref)])
        residual = 0
        for line in move_ids:
            move = move_obj.browse(self.cr, self.uid,line)
            residual = residual + move.debit - move.credit
        return round(residual,2)
    
    def get_reconcile_name(self, reconcile_id):
        reconcile_description = ''
        if reconcile_id:
            acc = self.pool.get('account.move.reconcile')
            acc_list = acc.browse(self.cr, self.uid, reconcile_id)
            reconcile_description = acc_list.name_get()[0][1]

        return reconcile_description

    def get_all_partner(self):
        obj = self.pool.get('res.partner')
        return obj
        
HeaderFooterTextWebKitParser('report.due_list_pdf',
                             'account.move.line',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                              '/template_due_list.mako',
                             parser=account_due_list_report_ext_isa)
