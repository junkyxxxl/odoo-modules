# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _


class wizard_stock_sheet_result_line(orm.TransientModel):
    _name = 'wizard.stock.sheet.result.line'
    _description = 'Print Stock Sheet Result Lines'

    def _sign_quantity(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = line.quantity
            if(line.sign == 'outgoing'):
                res[line.id] = -line.quantity
        return res

    def view_stock_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_id = context.get('move_id', None)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'stock_makeover',
                                              'view_stock_move_isa_form')
        view_id = result and result[1] or False

        return {
              'name': _("Stock Move"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'stock.move',
              'type': 'ir.actions.act_window',
              'res_id': move_id,
              'view_id': view_id,
              'target': 'current',
              }

    _columns = {
        'result_id': fields.many2one('wizard.stock.sheet.result',
                                     'Result'),
        'date': fields.date(string="Date"),
        'document_number': fields.char('Document Number',
                                       size=128),
        'partner_id': fields.many2one('res.partner',
                                      'Partner'),
        'unit_of_measure': fields.char('Unit of Measure',
                                       size=10),
        'cause': fields.char('Cause',
                             size=128),
        'quantity': fields.integer('Absolute Quantity'),
        'warehouse_id': fields.many2one('stock.warehouse',
                                         'Warehouse'),
                
        'document_origin': fields.char('Origin',
                                       size=128),
        'move_id': fields.many2one('stock.move',
                                   'Move'),
        'sign': fields.selection([('ingoing', 'Load'),
                                  ('outgoing', 'Unload')],
                                  'State'),
        'fnct_quantity': fields.function(_sign_quantity,
                                  string='Quantity',
                                  type='float'),
    }
