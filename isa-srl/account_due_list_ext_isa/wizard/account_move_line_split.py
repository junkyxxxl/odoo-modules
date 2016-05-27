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


class account_move_line_split(orm.TransientModel):

    _name = 'account.move.line.split'

    def _get_lines(self, cr, uid, move_id, context=None):
        cr.execute('SELECT * '\
                    'FROM account_move_line '\
                    'WHERE id = %s ', (move_id,))
        lines = cr.dictfetchall()[0]

        return lines

    def onchange_debit1(self, cr, uid, ids, move_id=False,
                        debit1=False, context=None):

        values = self._get_lines(cr, uid, move_id, context)
        if not values:
            return {'value': {}}

        return {'value': {
                    'debit1': round(debit1, 2) ,
                    'debit2': round(values['debit'] - debit1, 2) ,
                    }
        }

    def onchange_debit2(self, cr, uid, ids, move_id=False,
                        debit2=False, context=None):

        values = self._get_lines(cr, uid, move_id, context)
        if not values:
            return {'value': {}}

        return {'value': {
                    'debit1': round(values['debit'] - debit2, 2) ,
                    'debit2': round(debit2, 2) ,
                    }
        }

    def onchange_credit1(self, cr, uid, ids, move_id=False,
                         credit1=False, context=None):

        values = self._get_lines(cr, uid, move_id, context)
        if not values:
            return {'value': {}}

        return {'value': {
                    'credit1': round(credit1, 2) ,
                    'credit2': round(values['credit'] - credit1, 2) ,
                    }
        }

    def onchange_credit2(self, cr, uid, ids, move_id=False,
                         credit2=False, context=None):

        values = self._get_lines(cr, uid, move_id, context)
        if not values:
            return {'value': {}}

        return {'value': {
                    'credit1': round(values['credit'] - credit2, 2) ,
                    'credit2': round(credit2, 2) ,
                    }
        }

    def _get_sql_insert_statement(self, move, lines):
        vars_to_sql = []
        keys_to_sql = []
        for t_key, t_value in lines.items():
            if t_key != 'id' and (t_key == 'date_maturity_previous'
                                  or t_value != None):
                value_type = type(t_value)
                if value_type is unicode:
                    t_value = t_value.encode('ascii', 'ignore')
                    t_key = t_key.encode('ascii', 'ignore')
                keys_to_sql.append(t_key)
                if t_key == 'debit':
                    vars_to_sql.append(move['debit2'])
                elif t_key == 'credit':
                    vars_to_sql.append(move['credit2'])
                elif t_key == 'date_maturity':
                    vars_to_sql.append(move['date_maturity2'])
                elif t_key == 'date_maturity_previous':
                    vars_to_sql.append(move['date_maturity_temp2'])
                else:
                    vars_to_sql.append(t_value)
        
        keys_to_sql = ', '.join(keys_to_sql)
        insert_sql = 'INSERT INTO account_move_line(%s) values %s'
        return insert_sql, keys_to_sql, vars_to_sql

    def _get_sql_update_statement(self, move, lines):
        vars_to_sql = []
        for t_key, t_value in lines.items():
            if t_key == 'date_maturity_previous' or t_value != None:
                value_type = type(t_value)
                if value_type == type('string') or value_type is unicode:
                    t_value = '\047' + t_value + '\047'
                else:
                    t_value = str(t_value)
                t_key = str(t_key)
                if value_type is unicode:
                    t_value = t_value.encode('ascii', 'ignore')
                    t_key = t_key.encode('ascii', 'ignore')
                if t_key == 'debit':
                    vars_to_sql.append(t_key + ' = ' + str(move['debit1']))
                elif t_key == 'credit':
                    vars_to_sql.append(t_key + ' = ' + str(move['credit1']))
                elif t_key == 'date_maturity':
                    vars_to_sql.append(t_key + ' = \047' + 
                                    str(move['date_maturity1']) + '\047')
                elif t_key == 'date_maturity_previous':
                    vars_to_sql.append(t_key + ' = \047' + 
                                    str(move['date_maturity_temp1']) + '\047')
                else:
                    vars_to_sql.append(t_key + ' = ' + t_value)
        
        vars_to_sql = ', '.join(vars_to_sql)
        update_sql = 'UPDATE account_move_line SET %s WHERE id = %s'
        return update_sql, vars_to_sql

    def split_maturities(self, cr, uid, ids, context=None):
        
        move = self.read(cr, uid, ids, ['move_id', 'debit1', 'credit1',
                                        'quantity1', 'date_maturity1',
                                        'date_maturity_previous1', 'debit2',
                                        'credit2', 'quantity2',
                                        'date_maturity2',
                                        'date_maturity_previous2',
                                        'date_maturity_temp1',
                                        'date_maturity_temp2'])[0]
        move_id = move['move_id']

        cr.execute('SELECT * '\
                    'FROM account_move_line '\
                    'WHERE id = %s ', (move_id,))
        lines = cr.dictfetchall()[0]

        if lines['debit'] != move['debit1'] + move['debit2']:
            raise orm.except_orm(_('Error!'),
                                 (_('Sum of Debit and New Debit must be equal to original Debit!')))
        if lines['credit'] != move['credit1'] + move['credit2']:
            raise orm.except_orm(_('Error!'),
                                 (_('Sum of Credit and New Credit must be equal to original Credit!')))

        if move['debit1'] < 0 or move['debit2'] < 0:
            raise orm.except_orm(_('Error!'),
                                 (_('Debit values cannot be negative!')))
        if move['credit1'] < 0 or move['credit2'] < 0:
            raise orm.except_orm(_('Error!'),
                                 (_('Credit values cannot be negative!')))

        if move['debit1'] * move['debit2'] == 0 and move['credit1'] * move['credit2'] == 0:
            raise orm.except_orm(_('Error!'),
                                 (_('Values cannot be negative!')))

        insert_sql, keys_to_sql, vars_to_sql = self._get_sql_insert_statement(
                                                                move, lines)

        to_execute = insert_sql % (keys_to_sql, tuple(vars_to_sql),)
        cr.execute(to_execute)

        update_sql, vars_to_sql = self._get_sql_update_statement(move, lines)

        to_execute = update_sql % (vars_to_sql, move_id,)
        cr.execute(to_execute)

        return True

    _columns = {
        'move_id': fields.integer('Move id'),
        
        'debit1': fields.float('Debit', digits=(12, 2)),
        'credit1': fields.float('Credit', digits=(12, 2)),
        'date_maturity1': fields.date('Date maturity'),
        'date_maturity_previous1': fields.date('Previous due date'),
        'date_maturity_temp1': fields.date('Temporary due date'),
        
        'debit2': fields.float('New Debit', digits=(12, 2)),
        'credit2': fields.float('New Credit', digits=(12, 2)),
        'date_maturity2': fields.date('New Date maturity'),
        'date_maturity_previous2': fields.date('New previous due date'),
        'date_maturity_temp2': fields.date('New Temporary due date'),
    }
