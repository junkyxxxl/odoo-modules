# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ISA s.r.l. (<http://www.isa.it>).
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

from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.osv import orm, fields
from openerp.tools.translate import _


class central_journal_report(orm.TransientModel):

    _name = 'wizard.central.journal.report'
    _description = 'Printing parameters of the Center Journal'

    def _get_fiscal_years(self, cr, uid, context=None):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr, uid, [], order="id desc")
        fiscalyears = []
        for account_fiscalyear in fiscalyear_obj.browse(cr,
                                                uid, fiscalyear_ids):
            fiscalyears.append((account_fiscalyear.id,
                                account_fiscalyear.name))
        return fiscalyears

    def _get_account_fiscalyear_data(self, cr, uid, ids, fiscalyear_id):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_data = fiscalyear_obj.browse(cr, uid, fiscalyear_id)
        return fiscalyear_data

    def _dates_control(self, str_date_start, str_date_end):
        today_date = date.today()
        date_start = datetime.strptime(str_date_start, DF).date() 
        date_stop = datetime.strptime(str_date_end, DF).date() 
        if date_start > date_stop:
            raise orm.except_orm(_('Wrong dates !'),
                                 _("The end date must be greater than the initial date."))
            return False
        if date_stop > today_date:
            raise orm.except_orm(_('Wrong dates !'),
                                 _("The end date can not be greater than today's date."))
        return True

    def _get_report_datas(self, cr, uid, ids, context=None):
        wizard_form_datas = self.read(cr, uid, ids)[0]
        datas = {
            'ids': [],
            'model': 'account.move.line',
            'form': wizard_form_datas,
        }
        return datas

    _columns = {
        'company_id': fields.many2one('res.company', 
                                      'Company', 
                                      required=True), 
        'date_move_line_from': fields.date('From date', required=True,),
        'date_move_line_from_view': fields.date('From date'),
        'date_move_line_to': fields.date('to date', required=True),
        'fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal Year',
                                       required=True),
        'print_state': fields.selection([('draft', 'Draft'),
                                         ('print', 'Ready for printing'),
                                         ('printed', 'Printed')], 'State',
                                        readonly=True),
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = {'value': {}}
        res['value'].update({'fiscalyear': ''})        
        return res

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False,
                                context=None):
        print_state = 'draft'
        date_move_line_from = date_move_line_from_view = False
        date_move_line_to = False
        if fiscalyear_id:
            print_state = 'print'
            fiscalyear_data = self._get_account_fiscalyear_data(cr,
                                                uid, ids, fiscalyear_id)
            # set values
            today_date = date.today()
            date_start = datetime.strptime(fiscalyear_data.date_start,
                                           DF).date() 
            date_stop = datetime.strptime(fiscalyear_data.date_stop,
                                          DF).date() 
            # set date_move_line_from
            t_date_last_print = fiscalyear_data.date_last_print
            if t_date_last_print:
                date_last_print = datetime.strptime(t_date_last_print,
                                                    DF).date()
                date_move_line_from_view = (date_last_print + \
                                            timedelta(days=1)).__str__()
                date_move_line_from = date_move_line_from_view
                if date_last_print == date_stop:
                    date_move_line_from_view = date_start.__str__()
                    date_move_line_from = date_move_line_from_view
                    print_state = 'printed'
            else:
                date_move_line_from_view = date_start.__str__()
                date_move_line_from = date_move_line_from_view
            # set date_move_line_to
            if today_date > date_stop:
                date_move_line_to = date_stop.__str__()
            else:
                date_move_line_to = (today_date - timedelta(days=1)).__str__()

        return {'value': {
                    'date_move_line_from': date_move_line_from,
                    'date_move_line_from_view': date_move_line_from_view,
                    'date_move_line_to': date_move_line_to,
                    'print_state': print_state,
                    }
                }

    def print_report(self, cr, uid, ids, context=None):
        datas = self._get_report_datas(cr, uid, ids, context=context)
        if self._dates_control(datas['form']['date_move_line_from'],
                               datas['form']['date_move_line_to']) == False:
            return False
        datas['print_final'] = False
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'central_journal_report',
            'datas': datas,
        }

    def print_report_final(self, cr, uid, ids, context=None):
        datas = self._get_report_datas(cr, uid, ids, context)
        if self._dates_control(datas['form']['date_move_line_from'],
                               datas['form']['date_move_line_to']) == False:
            return False
        datas['print_final'] = True
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'central_journal_report',
            'datas': datas,
        }

    _defaults = {
        'print_state': 'draft',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, context=c),        
    }
