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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_move_line_isa(orm.Model):

    _inherit = 'account.move.line'


    def create(self, cr, uid, vals, context=None, check=True):

        # necessario in quanto il campo date è readonly
        #vals['date'] = fields.date.context_today(self, cr, uid, context=context)

        vals['date'] = fields.date.context_today(self, cr, uid, context=context)

        result = super(account_move_line_isa,
                       self).create(cr,
                                    uid,
                                    vals,
                                    context=context)
        return result

    def write(self, cr, uid, ids, vals, context=None, check=True,
                    update_check=True):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if len(ids) == 1:
            move = self.read(cr, uid, ids)
            if len(move) == 1:
                move = move[0]
                if move['date_maturity_temp']:
                    t_date_maturity_temp = move['date_maturity_temp']
                    vals['date_maturity_previous'] = t_date_maturity_temp
                
                if 'date_maturity' in vals:
                    t_date_maturity = vals['date_maturity']
                    vals['date_maturity_temp'] = t_date_maturity

        todo_date = None
        if vals.get('date', False):
            todo_date = vals['date']
#            del vals['date']

        result = super(account_move_line_isa,
                       self).write(cr, uid, ids,
                                   vals, context=context,
                                   check=check,
                                   update_check=update_check)

        move_obj = self.pool.get('account.move')
        if check:
            done = []
            for line in self.browse(cr, uid, ids):
                if line.move_id.id not in done:
                    done.append(line.move_id.id)
                    move_obj.validate(cr, uid, [line.move_id.id], context)
                    if todo_date:
                        move_obj.write(cr, uid, [line.move_id.id],
                                       {'date': todo_date}, context=context)
        return result

    def wizard_open(self, cr, uid, ids, context=None):

        wizard_obj = self.pool.get('account.move.line')
        res = wizard_obj.read(cr, uid, ids, ['debit', 'credit', 'quantity',
                                             'date_maturity',
                                             'date_maturity_previous'])
        res = res[0]

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_due_list_ext_isa',
                                              'wizard_split_maturity_form')
        view_id = result and result[1] or False

        context.update({
            'default_move_id': ids[0],
            'default_debit1': res['debit'],
            'default_credit1': res['credit'],
            'default_quantity1': res['quantity'],
            'default_date_maturity1': res['date_maturity'],
            'default_date_maturity_temp1': res['date_maturity'],
            'default_date_maturity_temp2': res['date_maturity'],
            'default_date_maturity_previous1': res['date_maturity_previous'],
            'default_date_maturity_previous2': res['date_maturity_previous'],
        })
        return {
              'name': _('Split maturity'),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'account.move.line.split',
              'type': 'ir.actions.act_window',
              'context': context,
              'view_id': view_id,
              'target' : 'new',
              }

    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result


    _columns = {
        'date_maturity_previous': fields.date('Previous due date',
                    select=True,
                    help="This field contains previous maturity due date."),
        'date_maturity_temp': fields.date('Temporary due date', select=True),
        'move_lines_isa': fields.one2many('account.move.line', 'move_id',
                    'Move lines'),
        'document_date': fields.related('move_id','document_date', string='Data documento', type='date',
                                store = {
                                    'account.move': (_get_move_lines, ['document_date'], 20)
                                }),


    }
