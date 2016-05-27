# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv


class accounting_report(osv.osv_memory):
    _inherit = "accounting.report"

    _columns = {
        'group_partner': fields.boolean('Solo saldo conto cli/for'),
        }

    def _get_account_report(self, cr, uid, context=None):
        # TODO deprecate this it doesnt work in web
        menu_obj = self.pool.get('ir.ui.menu')
        report_obj = self.pool.get('account.financial.report')
        report_ids = []
        if context.get('active_id'):
            menu = menu_obj.browse(cr, uid, context.get('active_id')).name
            report_ids = report_obj.search(cr, uid, [('name','ilike',menu)])
        return report_ids and report_ids[0] or False

    _defaults = {
            'filter_cmp': 'filter_no',
            'target_move': 'posted',
            'account_report_id': _get_account_report,
    }

    def _build_comparison_context(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = super(accounting_report,self)._build_comparison_context(cr, uid, ids, data, context=context)
        if not result:
            result = {}
        group_partner = self.read(cr, uid, ids, ['group_partner'], context=context)[0]
        if group_partner['group_partner']:
            result['group_partner'] = group_partner['group_partner'] or False
        return result

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(accounting_report, self).check_report(cr, uid, ids, context=context)
        data = {}
        data['form'] = self.read(cr, uid, ids, ['account_report_id', 'date_from_cmp',  'date_to_cmp',  'fiscalyear_id_cmp', 'journal_ids', 'period_from_cmp', 'period_to_cmp',  'filter_cmp',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id_cmp', 'chart_account_id', 'period_from_cmp', 'period_to_cmp', 'account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(cr, uid, ids, data, context=context)
        res['data']['form']['comparison_context'] = comparison_context
        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'date_to_cmp',  'fiscalyear_id_cmp', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter','target_move'], context=context)[0])

        group_partner = self.read(cr, uid, ids, ['group_partner'], context=context)[0]        
        if group_partner['group_partner']:
            data['form']['group_partner'] = group_partner['group_partner'] or False        
            
        return self.pool['report'].get_action(cr, uid, [], 'account.report_financial', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
