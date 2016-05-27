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

    _name = 'wizard.account.statement'
    _description = 'Wizard Estratti Conto'

    def _get_account_ids(self, cr, uid, context=None):
        res = False
        if context.get('active_model', False) == 'account.account' and context.get('active_ids', False):
            res = context['active_ids']
        return res

    _columns = {
        'company_id': fields.many2one('res.company', 
                                      'Company', 
                                      required=True), 
        'statement_type': fields.selection(
                                [
                                 ('E', 'Aperte e Chiuse'),
                                 ('O', 'Aperte'),
                                 ('H', 'Chiuse'),],
                                'Partite',
                                required=True),
        'date_from': fields.date('Da Data'),
        'target_move': fields.selection([('posted', 'Solo Registrazioni Pubblicate'),
                                         ('all', 'Tutte le Registrazioni'),
                                        ], 'Registrazioni', required=True),
        'account_ids': fields.many2many('account.account', string='Filter on accounts',
                                         help="""Only selected accounts will be printed."""),
    }

    _defaults = {
        'statement_type': 'E',
        'target_move': 'posted',
        'account_ids': _get_account_ids,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, context=c),        
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': [],
             'model': 'account.account',
             'context': context.get('active_ids', []),
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.report.statement',
            'datas':datas,
        }
