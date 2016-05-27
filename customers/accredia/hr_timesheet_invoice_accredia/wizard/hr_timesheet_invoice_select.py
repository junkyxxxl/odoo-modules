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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class hr_timesheet_invoice_select(osv.osv_memory):

    _name = 'hr.timesheet.invoice.select'

    _columns = {
        'name': fields.char('Wizard'),
    }

    def do_select(self, cr, uid, ids, context=None):
        lines_obj = self.pool.get('account.analytic.line')
        purchase_obj = self.pool.get('purchase.order')

        for line_data in lines_obj.browse(cr, uid,
                                          context['active_ids'],
                                          context=context):
            if line_data.purchase_order_line_id:
                t_order_id = line_data.purchase_order_line_id.order_id.id
                purchase_obj.write(cr, uid,
                                   [t_order_id],
                                   {'is_confirmed': True},
                                   context=context)

        lines_obj.write(cr, uid,
                        context['active_ids'],
                        {'to_invoice': 1,  # TODO
                         })
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        mod_ids = mod_obj.search(cr, uid, [('name', '=', 'action_account_tree1')], context=context)[0]
        res_id = mod_obj.read(cr, uid, mod_ids, ['res_id'], context=context)['res_id']
        act_win = act_obj.read(cr, uid, res_id, [], context=context)
        act_win['domain'] = [('id', 'in', context['active_ids'])]
        act_win['name'] = _('Lines')
        return act_win
