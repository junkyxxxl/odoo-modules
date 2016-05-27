# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import os
from openerp.report import report_sxw
from openerp.tools.translate import _
import logging
import math
from datetime import datetime
from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser

_logger = logging.getLogger(__name__)

class Parser(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):

    def _compute_protocol_number(self,protocol_number):
        padding = self._get_padding()
        pnumb = str(protocol_number)
        digits = math.floor(math.log10(float(protocol_number)))+1
        for i in range(0,int(padding-digits)):
            pnumb = '0'+pnumb
        return pnumb
        
    def _tax_amounts_by_code(self, move):
        res={}
        for move_line in move.line_id:
            if move_line.tax_code_id and move_line.tax_amount:
                if not res.get(move_line.tax_code_id.id):
                    res[move_line.tax_code_id.id] = 0.0
                    self.localcontext['used_tax_codes'][move_line.tax_code_id.id] = True
                res[move_line.tax_code_id.id] += (move_line.tax_amount
                    * self.localcontext['data']['tax_sign'])
        return res

    def _get_tax_lines(self, move):
        res=[]
        tax_code_obj=self.pool.get('account.tax.code')
        # index è usato per non ripetere la stampa dei dati fattura quando ci sono più codici IVA
        index=0
        invoice = None
        for move_line in move.line_id:
            invoice_type = ''
            invoice = None
            if move_line.invoice:
                if invoice and invoice.id != move_line.invoice.id:
                    raise Exception(_("Move %s contains different invoices") % move.name)
                invoice = move_line.invoice
                if invoice:
                    if invoice.type in ['in_invoice', 'out_invoice']:
                        invoice_type = 'Fattura'
                    elif invoice.type in ['in_refund', 'out_refund']:
                        invoice_type = 'N. Credito'

        amounts_by_code = self._tax_amounts_by_code(move)
        for tax_code_id in amounts_by_code:
            tax_code = tax_code_obj.browse(self.cr, self.uid, tax_code_id)
            tax_item = {
                'tax_code_name': tax_code.name,
                'tax_code': tax_code.code,
                'amount': amounts_by_code[tax_code_id],
                'index': index,
                'invoice_date': (invoice and invoice.date_invoice or move.date or ''),
                'invoice_type': (invoice_type),
                'supplier_invoice_number': (invoice and invoice.supplier_invoice_number or '')
                }
            res.append(tax_item)
            index += 1
        return res

    def _get_invoice_total(self, move):
        total = 0.0
        receivable_payable_found = False
        for move_line in move.line_id:
            if move_line.account_id.type == 'receivable':
                total += move_line.debit or ( - move_line.credit)
                receivable_payable_found = True
            elif move_line.account_id.type == 'payable':
                total += ( - move_line.debit) or move_line.credit
                receivable_payable_found = True
        if receivable_payable_found:
            return abs(total)
        else:
            return abs(move.amount)
    
    def build_parent_tax_codes(self, tax_code):
        res={}
        if tax_code.parent_id and tax_code.parent_id.parent_id:
            res[tax_code.parent_id.id]=True
            res.update(self.build_parent_tax_codes(tax_code.parent_id))
        return res
    
    def _compute_totals(self, tax_code_ids):
        res=[]
        res_dict={}
        tax_code_obj = self.pool.get('account.tax.code')
        for period_id in self.localcontext['data']['period_ids']:
            for tax_code in tax_code_obj.browse(self.cr, self.uid,
                tax_code_ids, context={
                'period_id': period_id,
                }):
                if not res_dict.get(tax_code.id):
                    res_dict[tax_code.id] = 0.0
                    tax_code_childs = tuple(tax_code_obj.search(self.cr, self.uid, [('parent_id', 'child_of', tax_code.id)]))
                    self.cr.execute('''
                                    SELECT 
                                        line.tax_code_id,
                                        SUM(line.tax_amount)
                                    FROM
                                        account_move_line AS line,
                                        account_move AS move,
                                        account_journal AS journal
                                    WHERE
                                        line.tax_code_id IN %s AND
                                        move.state LIKE 'posted' AND
                                        line.journal_id = journal.id AND
                                        journal.iva_registry_id = %s AND 
                                        line.period_id = %s AND
                                        line.move_id = move.id
                                    GROUP BY
                                        line.tax_code_id
                                    ''',(tax_code_childs, self.localcontext['data']['iva_registry_id'],period_id))    
                    line_to_add = self.cr.fetchall()
                    to_add = 0.0
                    if line_to_add:
                        for to_add_line in line_to_add: 
                            to_add += to_add_line[1]
                    res_dict[tax_code.id] += (to_add * self.localcontext['data']['tax_sign'])                    
                    
        for tax_code_id in res_dict:
            tax_code = tax_code_obj.browse(self.cr, self.uid, tax_code_id)
            if res_dict[tax_code_id]:
                res.append((tax_code.name,res_dict[tax_code_id],tax_code.code))
        return res
    
    def _get_tax_codes(self):
        return self._compute_totals(self.localcontext['used_tax_codes'].keys())

    def _get_padding(self):
        padding = self.localcontext['data']['padding']
        return self.localcontext['data']['padding']
    
    def _get_company_id(self):
        tmp = self.localcontext
        temp = self.localcontext['data']
        company = self.localcontext['data']['company_id']
        return self.localcontext['data']['company_id']
                
    def _get_tax_codes_totals(self):
        parent_codes = {}
        tax_code_obj = self.pool.get('account.tax.code')
        for tax_code in tax_code_obj.browse(self.cr, self.uid,
            self.localcontext['used_tax_codes'].keys()):
            parent_codes.update(self.build_parent_tax_codes(tax_code))
        return self._compute_totals(parent_codes.keys())
    
    def _all_compute_totals(self, tax_code_ids):
        res=[]
        res_dict={}

        tax_code_obj = self.pool.get('account.tax.code')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        period_obj = self.pool.get('account.period')
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid,
                                   [('name', 'like', self.localcontext['fiscal_year'])],
                                   limit=1)
        for fiscalyear_data in fiscalyear_obj.browse(self.cr, self.uid,
                                            fiscalyear_ids):
            
            t_ids = self.localcontext['data']['period_ids']
            if t_ids:
                max = period_obj.browse(self.cr, self.uid, t_ids[0]).date_stop
                for t_id in t_ids:
                    t_date = period_obj.browse(self.cr, self.uid, t_id).date_stop
                    if t_date > max:
                        max = t_date
                        
            for period_id in fiscalyear_data.period_ids:
                if period_id.date_start > max:
                    continue
                for tax_code in tax_code_obj.browse(self.cr, self.uid,
                    tax_code_ids, context={
                    'period_id': period_id.id,
                    }):

                    tax_code_childs = tuple(tax_code_obj.search(self.cr, self.uid, [('parent_id', 'child_of', tax_code.id)]))
                    if not res_dict.get(tax_code.id):
                        res_dict[tax_code.id] = 0.0
                    self.cr.execute('''
                                    SELECT 
                                        line.tax_code_id,
                                        SUM(line.tax_amount)
                                    FROM
                                        account_move_line AS line,
                                        account_move AS move,
                                        account_journal AS journal
                                    WHERE
                                        line.tax_code_id IN %s AND
                                        move.state LIKE 'posted' AND
                                        line.journal_id = journal.id AND
                                        journal.iva_registry_id = %s AND 
                                        line.period_id = %s AND
                                        line.move_id = move.id
                                    GROUP BY
                                        line.tax_code_id
                                    ''',(tax_code_childs, self.localcontext['data']['iva_registry_id'],period_id.id))    
                    line_to_add = self.cr.fetchall()
                    to_add = 0.0
                    if line_to_add:
                        for to_add_line in line_to_add: 
                            to_add += to_add_line[1]
                            
                    res_dict[tax_code.id] += (to_add * self.localcontext['data']['tax_sign'])
            for tax_code_id in res_dict:
                tax_code = tax_code_obj.browse(self.cr, self.uid, tax_code_id)
                if res_dict[tax_code_id]:
                    res.append((tax_code.name,res_dict[tax_code_id],tax_code.code))
        return res

    def _get_all_tax_codes(self):
        t_tax_code_keys = self.localcontext['used_tax_codes'].keys()
        return self._all_compute_totals(t_tax_code_keys)

    def _get_all_tax_codes_totals(self):
        parent_codes = {}
        tax_code_obj = self.pool.get('account.tax.code')
        for tax_code in tax_code_obj.browse(self.cr, self.uid,
            self.localcontext['used_tax_codes'].keys()):
            parent_codes.update(self.build_parent_tax_codes(tax_code))
        return self._all_compute_totals(parent_codes.keys())

    def _get_all_start_date(self):
        start_date = None

        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid,
                                   [('name', 'like', self.localcontext['fiscal_year'])],
                                   limit=1)
        for fiscalyear_data in fiscalyear_obj.browse(self.cr, self.uid,
                                            fiscalyear_ids):

            for period in fiscalyear_data.period_ids:
                period_start = datetime.strptime(period.date_start, '%Y-%m-%d')
                if not start_date or start_date > period_start:
                    start_date = period_start
        return start_date.strftime('%Y-%m-%d')

    def _get_start_date(self):
        period_obj = self.pool.get('account.period')
        start_date = None
        for period in period_obj.browse(self.cr,self.uid,
            self.localcontext['data']['period_ids']):
            period_start = datetime.strptime(period.date_start, '%Y-%m-%d')
            if not start_date or start_date > period_start:
                start_date = period_start
        return start_date.strftime('%Y-%m-%d')

    def _get_end_date(self):
        period_obj = self.pool.get('account.period')
        end_date = None
        for period in period_obj.browse(self.cr,self.uid,
            self.localcontext['data']['period_ids']):
            period_end = datetime.strptime(period.date_stop, '%Y-%m-%d')
            if not end_date or end_date < period_end:
                end_date = period_end
        return end_date.strftime('%Y-%m-%d')

    def _get_moves(self):
        move_obj = self.pool.get('account.move')
        move_ids = move_obj.search(self.cr, self.uid, [('id','in',self.ids)], order='date,protocol_number')
        
        return move_obj.browse(self.cr, self.uid, move_ids)

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.company = self.pool.get('wizard.vat.registry').browse(self.cr, self.uid, self.parents['active_id']).company_id
        self.localcontext.update({
            'tax_lines': self._get_tax_lines,
            'tax_codes': self._get_tax_codes,
            'tax_codes_totals': self._get_tax_codes_totals,
            'all_tax_codes': self._get_all_tax_codes,
            'all_tax_codes_totals': self._get_all_tax_codes_totals,
            'all_start_date': self._get_all_start_date,
            'used_tax_codes': {},
            'start_date': self._get_start_date,
            'end_date': self._get_end_date,
            'invoice_total': self._get_invoice_total,
            'display_target_move': self._get_display_target_move,
            'report_name': _('Registro IVA'),
            'get_moves': self._get_moves,
            'compute_protocol_number':self._compute_protocol_number,
            'get_padding':self._get_padding,
            'get_company_id':self._get_company_id,
        })

    def set_context(self, objects, data, ids, report_type=None):
        header_report_name = ''
        
        if not 'final' in data or not data['final']:
            header_report_name += 'PROVA - '
        
        header_report_name = header_report_name + self.company.name + ' - ' + self.company.vat + ' - ' +(_('Registro I.V.A.: '))     
        header_report_name = header_report_name + self.pool.get('vat.registries.isa').browse(self.cr, self.uid, data['iva_registry_id']).name

        if data['period_ids'] and len(data['period_ids']) == 1:
            header_report_name = header_report_name + ' - Periodo: ' + self.pool.get('account.period').browse(self.cr, self.uid, data['period_ids'][0]).name            

        if not 'final' in data or not data['final']:
            header_report_name += ' - PROVA'

        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)

        t_year = ''
        if objects:
            t_year = objects[0].period_id and objects[0].period_id.fiscalyear_id and objects[0].period_id.fiscalyear_id.name or ''

        self.localcontext.update({
            'fiscal_page_base': data.get('fiscal_page_base'),
            'fiscal_year': t_year,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                #('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Pagina'), t_year, _('/'), '[page]'))),
                ('--footer-line',),
                ('--page-offset',str(data.get('fiscal_page_base'))),
            ],
        })
        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)

HeaderFooterTextWebKitParser('report.vat_registry_sale_webkit',
                             'account.move',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                               '/vat_registry_sale.mako',
                             parser=Parser)
HeaderFooterTextWebKitParser('report.vat_registry_purchase_webkit',
                             'account.move',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                               '/vat_registry_purchase.mako',
                             parser=Parser)
HeaderFooterTextWebKitParser('report.vat_registry_corrispettivi_webkit',
                             'account.move',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                               '/vat_registry_corrispettivi.mako',
                             parser=Parser)
