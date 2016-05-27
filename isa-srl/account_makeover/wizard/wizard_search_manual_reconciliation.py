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


from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from math import ceil
import openerp.addons.decimal_precision as dp

class wizard_search_manual_reconciliation(osv.osv_memory):
    _name = "wizard.search.manual.reconciliation"
    _description = "Search Manual Reconciliation"

    _columns = {
        'move_id': fields.many2one('account.move', string='Account Move'),
    }


    def search_reconciliation(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        line_obj = self.pool.get('account.move.line')
        part_obj = self.pool.get('res.partner')

        move_id = self.browse(cr, uid, ids)[0].move_id
        
        partner_ids = []
        
        for line in move_id.line_id:
            if line.partner_id and line.partner_id.id not in partner_ids:
                partner_ids.append(line.partner_id.id)
        
        res_ids = []
        
        for partner_id in partner_ids:
            line_ids = line_obj.search(cr, uid, [('partner_id','=',partner_id)])
            for id in line_ids:
                res_ids.append(id)
        
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account',
                                              'view_move_line_tree')
        view_id = result and result[1] or False

        return {'domain': "[('id','in', ["+','.join(map(str,res_ids))+"])]",
                'name': _("Riconciliazioni per Registrazione Contabile"),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'context': {'group_by': 'partner_id','search_default_unreconciled': 1,'view_mode':True},
                'views': [(view_id,'tree'),(False,'form')],
                }
        
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    