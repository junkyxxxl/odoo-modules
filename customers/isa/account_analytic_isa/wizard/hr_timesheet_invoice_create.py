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


class hr_timesheet_invoice_create(osv.osv_memory):

    _inherit = 'hr.timesheet.invoice.create'

    _columns = {
        'date_invoice': fields.date('Data Fattura'),
    }

    def do_create(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        # Create an invoice based on selected timesheet lines
        invs = self.pool.get('account.analytic.line').invoice_cost_create(
            cr, uid, context['active_ids'], data, context=context)

        if data['date_invoice']:
            self.pool.get('account.invoice').write(cr, uid, invs,
                                                   {'date_invoice': data['date_invoice'],
                                                    'registration_date': data['date_invoice'],
                                                    },
                                                   context=context)

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        mod_ids = mod_obj.search(cr, uid, [('name', '=', 'action_invoice_tree1')], context=context)[0]
        res_id = mod_obj.read(cr, uid, mod_ids, ['res_id'], context=context)['res_id']
        act_win = act_obj.read(cr, uid, res_id, [], context=context)
        act_win['domain'] = [('id', 'in', invs), ('type', '=', 'out_invoice')]
        act_win['name'] = _('Invoices')
        return act_win
