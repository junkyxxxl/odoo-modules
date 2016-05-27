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

from openerp.osv import fields, orm


class account_analytic_account(orm.Model):
    _inherit = 'account.analytic.account'

    def _get_project_state(self, cr, uid, ids, name, args, context=None):
        res = {}
        proj_obj = self.pool.get('project.project')
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = None
            t_project_ids = proj_obj.search(cr, uid,
                                            [('analytic_account_id', '=', data.id),
                                             ('state', '!=', 'template')],
                                            limit=1,
                                            context=context)
            if t_project_ids:
                t_project_data = proj_obj.browse(cr, uid, t_project_ids[0], context=context)
                res[data.id] = t_project_data.state or None
        return res

    def _search_project_state(self, cr, uid, obj, name, args, domain=None, context=None):

        if not len(args):
            return []

        cr.execute("""SELECT account.id FROM project_project project
                      JOIN account_analytic_account account ON account.id = project.analytic_account_id
                      WHERE project.state != 'template'
                   """)
        res = cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        t_values = map(lambda x: x[0], res)
        return [('id', 'in', t_values)]

    def _get_fnct_amount_toinvoice(self, cr, uid, ids, name, arg, context=None):
        res = dict([(i, {}) for i in ids])
        for account in self.browse(cr, uid, ids, context=context):
            res[account.id] = 0.0
            for line in account.line_ids:
                if not line.invoice_id and line.to_invoice:
                    factor = self.pool.get('hr_timesheet_invoice.factor').browse(cr, uid, line.to_invoice.id, context=context)
                    res[account.id] += line.amount * (100-factor.factor or 0.0) / 100.0
        return res

    def _search_fnct_amount_toinvoice(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        cr.execute("""
            SELECT account_id, sum(amount)
            FROM account_analytic_line line
                LEFT JOIN account_analytic_journal journal ON (journal.id = line.journal_id)
            WHERE journal.type != 'purchase'
                AND invoice_id IS NULL
                AND to_invoice IS NOT NULL
                AND amount != 0.0
            GROUP BY account_id""")
        res = cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]


    _columns = {'project_state': fields.function(_get_project_state,
                                                 method=True,
                                                 type='char',
                                                 string='Project State',
                                                 fnct_search=_search_project_state),
                'department_id': fields.many2one('hr.department',
                                                 'Department'),
                'fnct_amount_toinvoice': fields.function(_get_fnct_amount_toinvoice,
                                                         type='float',
                                                         string="Importo da Fatturare",
                                                         store=False,
                                                         fnct_search=_search_fnct_amount_toinvoice),
                }




