# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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


class account_report_journal_account(orm.TransientModel):

    _name = 'account.journal_account_report'
    _description = 'report of analytic journal items filters'

    _columns = {
        'date_from': fields.date('From date'),
        'date_to': fields.date('To date'),
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {'ids': [],
                 'model': 'account.analytic.account',
                 'context': context.get('active_ids', []),
                 'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_report_journal_account_flati',
            'datas': datas,
        }
