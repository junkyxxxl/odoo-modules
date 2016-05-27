# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def _get_reconcile(self, cr, uid, ids,name, unknow_none, context=None):
        res = dict.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids, context=context):
            if line.reconcile_id:
                res[line.id] = str(self.pool.get('account.move.reconcile').name_get(cr, uid, line.reconcile_id.id))
            elif line.reconcile_partial_id:
                res[line.id] = str(self.pool.get('account.move.reconcile').name_get(cr, uid, line.reconcile_partial_id.id))
        return res

    def _get_move_from_reconcile(self, cr, uid, ids, context=None):
        move_list = []
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move_list.append(line.move_id.id)
            for line in r.line_id:
                move_list.append(line.move_id.id)
        move_line_ids = []
        if move_list:
            move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('move_id','in',move_list)], context=context)
        return move_line_ids

    _columns = {
        'reconcile_ref': fields.function(_get_reconcile, type='char', string='Reconcile Ref', oldname='reconcile',
                                         store={'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['reconcile_id','reconcile_partial_id'], 50),
                                                'account.move.reconcile': (_get_move_from_reconcile, None, 50)
                                                }),                
    }
