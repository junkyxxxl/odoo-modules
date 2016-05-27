# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
import copy
from openerp import models
from openerp.addons.account.report.account_financial_report import\
    report_account_common


class report_account_common_horizontal(report_account_common):
    def __init__(self, cr, uid, name, context=None):
        super(report_account_common_horizontal, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'get_left_lines': self.get_left_lines,
            'get_right_lines': self.get_right_lines,
        })

    def get_lines(self, data, side=None):
        data = copy.deepcopy(data)
        if data['form']['used_context'] is None:
            data['form']['used_context'] = {}
        data['form']['used_context'].update(
            account_financial_report_horizontal_side=side)
        
        lines = []
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=data['form']['used_context'])
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=data['form']['used_context']):
            vals = {
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
            }
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=data['form']['comparison_context']).balance * report.sign or 0.0
            lines.append(vals)
            account_ids = []
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids])
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
            if account_ids:
                
        
                if 'group_partner' in data['form'] and data['form']['group_partner']:
                    
                    prop_obj = self.pool.get('ir.property')
                    
                    property_id = prop_obj.search(self.cr,self.uid,[('name','=','property_account_receivable'),('res_id','in',[False,None,''])])[0]
                    property_data = prop_obj.browse(self.cr, self.uid, property_id)
                    parent_id = int(property_data.value_reference.split(',')[-1])
                    parent_receivable = self.pool.get('account.account').browse(self.cr, self.uid, parent_id).parent_id
            
                    property_id = prop_obj.search(self.cr,self.uid,[('name','=','property_account_payable'),('res_id','in',[False,None,''])])[0]
                    property_data = prop_obj.browse(self.cr, self.uid, property_id)
                    parent_id = int(property_data.value_reference.split(',')[-1])
                    parent_payable = self.pool.get('account.account').browse(self.cr, self.uid, parent_id).parent_id           
                    
                    if parent_receivable:
                        account_to_remove_ids_receivable = self.pool.get('account.account').search(self.cr, self.uid, [('id','in',account_ids),('parent_id','=',parent_receivable.id)])
                    if parent_payable:
                        account_to_remove_ids_payable = self.pool.get('account.account').search(self.cr, self.uid, [('id','in',account_ids),('parent_id','=',parent_payable.id)])
                        
                    
                    if account_to_remove_ids_receivable:
                        find = False
                        new_account_ids = []
                        for account_id in account_ids:
                            if account_id not in account_to_remove_ids_receivable:
                                new_account_ids.append(account_id)
                            elif not find:
                                new_account_ids.append(parent_receivable.id)
                                find = True
                        account_ids = new_account_ids
                        
                    if account_to_remove_ids_payable:
                        find = False
                        new_account_ids = []
                        for account_id in account_ids:
                            if account_id not in account_to_remove_ids_payable:
                                new_account_ids.append(account_id)
                            elif not find:
                                new_account_ids.append(parent_payable.id)
                                find = True
                        account_ids = new_account_ids
                     
                for account in account_obj.browse(self.cr, self.uid, account_ids, context=data['form']['used_context']):
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    flag = False
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance':  account.balance != 0 and account.balance * report.sign or account.balance,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and min(account.level + 1,6) or 6, #account.level + 1
                        'account_type': account.type,
                    }

                    if data['form']['debit_credit']:
                        vals['debit'] = account.debit
                        vals['credit'] = account.credit
                    if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance']):
                        flag = True
                    if data['form']['enable_filter']:
                        vals['balance_cmp'] = account_obj.browse(self.cr, self.uid, account.id, context=data['form']['comparison_context']).balance * report.sign or 0.0
                        if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance_cmp']):
                            flag = True
                    if flag:
                        lines.append(vals)
        return lines

    def get_left_lines(self, data):
        return self.get_lines(data, side='left')

    def get_right_lines(self, data):
        return self.get_lines(data, side='right')


class ReportFinancial(models.AbstractModel):
    _inherit = 'report.account.report_financial'
    _wrapped_report_class = report_account_common_horizontal
