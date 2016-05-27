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

from openerp.osv import orm, fields


class account_statement(orm.TransientModel):

    _name = 'wizard.hr.expense.final'
    _description = 'Wizard Consuntivo Nota Spese'

    def _get_fiscal_years(self, cr, uid, context=None):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr, uid, [], order="id desc")
        fiscalyears = []
        for account_fiscalyear in fiscalyear_obj.browse(cr,
                                                uid, fiscalyear_ids) :
            fiscalyears.append((account_fiscalyear.id,
                                account_fiscalyear.name))
        return fiscalyears

    def _get_employee_ids(self, cr, uid, context=None):
        res = False
        if context.get('active_model', False) == 'hr.employee' and context.get('active_ids', False):
            res = context['active_ids']
        return res

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False,
                                context=None):

        date_move_line_from = ''
        date_move_line_to = ''
        if fiscalyear_id:

            fiscalyear_obj = self.pool.get('account.fiscalyear')
            fiscalyear_data = fiscalyear_obj.browse(cr, uid, fiscalyear_id)
            if fiscalyear_data:
                date_move_line_from = fiscalyear_data.date_start
                date_move_line_to = fiscalyear_data.date_stop
                return {'value': {
                            'date_from': date_move_line_from,
                            'date_to': date_move_line_to,
                            }
                        }
        return {'value': {
                    'date_from': None,
                    'date_to': None,
                    }
                }

    _columns = {
        'company_id': fields.many2one('res.company', 
                                      'Company', 
                                      required=True), 
        'fiscalyear': fields.selection(_get_fiscal_years, 'Fiscal Year',
                                       required=True),
        'employee_ids': fields.many2many('hr.employee', string='Filtro su Impiegati',
                                         help="""Only selected employees will be printed."""),
        'only_total': fields.boolean('Solo Totali'),
        'date_from': fields.date('From date'),
        'date_to': fields.date('To date'),
    }

    _defaults = {
        'employee_ids': _get_employee_ids,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, context=c),        
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {'ids': [],
                 'model': 'hr.expense.expense',
                 'context': context.get('active_ids', []),
                 'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_report_expense_final',
            'datas':datas,
        }
