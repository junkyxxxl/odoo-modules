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

from openerp.osv import orm, fields

class analytic_journal_report(orm.TransientModel):

    _name = 'analytic.journal_report'
    _description = 'report of analytic journal items filters'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True), 
        'date_from': fields.date('From the date'),
        'date_to': fields.date('at the date'),
        'account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'partner_id': fields.many2one('res.partner', 'Partner', select=1),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, context=c),        
    }

    def print_report(self, cr, uid, ids, context=None):
        datas = {
             'ids': [],
             'model': 'account.analytic.line',
             'form': self.read(cr, uid, ids)[0]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_journal_items_pdf',
            'datas':datas,
        }
