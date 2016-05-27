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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_move_line_makeover(orm.Model):
    _inherit = 'account.move.line'

    def get_invoice(self, cr, uid, ids, context=None):
        invoice_pool = self.pool.get('account.invoice')
        res = {}
        for line in self.browse(cr, uid, ids):
            t_line_id = line.move_id.id
            inv_ids = invoice_pool.search(cr, uid,
                                          [('move_id', '=', t_line_id)])
            if len(inv_ids) > 1:
                raise orm.except_orm(_('Error'), _('Incongruent data: move %s has more than one invoice') % line.move_id.name)
            if inv_ids:
                res[line.id] = inv_ids[0]
            else:
                res[line.id] = False
        return res

    def _sign_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            if(line.credit > 0):
                res[line.id] = line.credit
            else: 
                res[line.id] = -line.debit
        return res

    def create(self, cr, uid, vals, context=None, check=True):
        
        if 'move_id' in vals and vals['move_id'] and 'invoice' in context and context['invoice']:
            move_id = self.pool.get('account.move').browse(cr, uid, vals['move_id'], context=context)
            if 'journal_id' in vals and vals['journal_id']:
                journal_id = self.pool.get('account.journal').browse(cr, uid, vals['journal_id'], context=context)
            else:
                journal_id = move_id.journal_id
                
            if 'period_id' in vals and vals['period_id']:
                period_id = self.pool.get('account.period').browse(cr, uid, vals['period_id'], context=context)
            else:
                period_id = move_id.period_id
                
            if journal_id and period_id:
                invoice_id = context['invoice']
                date = invoice_id.registration_date
                fiscalyear_id = period_id.fiscalyear_id
                if journal_id.check_previous_date:
                    previous_date = None
                    next_date = None
                    
                    if move_id.protocol_number or invoice_id.force_protocol_number:
                        
                        protocol_number = move_id.protocol_number or invoice_id.force_protocol_number
                        cr.execute('''
                            SELECT MAX (date)
                            FROM account_move
                            WHERE journal_id = %s AND CAST(protocol_number AS INT) < %s AND period_id IN %s
                        ''',(journal_id.id, protocol_number, tuple(fiscalyear_id.period_ids.ids)))
                        qry_result = cr.fetchall()
                        if qry_result:
                            previous_date = qry_result[0][0]                    
        
                        cr.execute('''
                            SELECT MIN (date)
                            FROM account_move
                            WHERE journal_id = %s AND CAST(protocol_number AS INT) > %s AND period_id IN %s
                        ''',(journal_id.id, protocol_number, tuple(fiscalyear_id.period_ids.ids)))
                        qry_result = cr.fetchall()
                        if qry_result:
                            next_date = qry_result[0][0]     
                        
                    else:
        
                        cr.execute(''' 
                            SELECT MAX (date)
                            FROM account_move
                            WHERE journal_id = %s AND period_id IN %s
                        ''',(journal_id.id, tuple(fiscalyear_id.period_ids.ids)))
                        qry_result = cr.fetchall()
                        if qry_result:
                            previous_date = qry_result[0][0]
                    
                    if previous_date and date < previous_date:
                        raise orm.except_orm(_('Error'), _('Data di registrazione incongruente con le altre registrazioni già effettuate su questo sezionale'))
                    if next_date and date > next_date:
                        raise orm.except_orm(_('Error'), _('Data di registrazione incongruente con le altre registrazioni già effettuate su questo sezionale'))
        
        if 'account_id' in vals and not vals['account_id']:
            raise orm.except_orm(_('Error'), _('Non puoi creare un movimento senza selezionare il conto contabile.'))      
          
        return super(account_move_line_makeover,self).create(cr, uid, vals, context=context, check=check)

    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result

    _columns = {
        'payment_type_move_line': fields.selection([('C', 'Cash'),
                                          ('B', 'Bank Transfer'),
                                          ('D', 'Bank Draft')],
                                         'Payment Type',),
        'is_selected': fields.selection([('draft', 'Draft'),
                                         ('accepted', 'Accepted'),
                                         ('valid', 'Valid')],
                                        'Selection Type'),
        'document_number': fields.related('move_id', 'document_number',
                                          type='char',
                                          relation='account.move',
                                          string='Document Number'),
        'currency_date': fields.date('Currency Date'),
        'fnct_amount': fields.function(_sign_amount,
                                       string='Amount',
                                       type='float'),
        'is_wht': fields.boolean('Withholding tax'),
        'wht_state': fields.selection([('open', 'Open'),
                                       ('confirmed', 'Confirmed'),
                                       ('selected', 'Selected'),
                                       ('paid', 'Paid')], 'Wht State'),
        'period_id': fields.related('move_id', 'period_id', string='Period', type='many2one', relation='account.period', required=True, select=True,
                                store = {
                                    'account.move': (_get_move_lines, ['period_id','line_id'], 20)
                                }),                
        }

    _defaults = {
        'state': 'draft',
        'is_wht': False,
        'wht_state': None
        }