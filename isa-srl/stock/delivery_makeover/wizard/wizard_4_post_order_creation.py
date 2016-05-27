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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class wizard_post_order_creation(orm.TransientModel):
    _name = 'wizard.post.order.creation'
    _description = 'Wizard Post Order Creation'
    
    _columns = {
                'stock_picking_out_id': fields.many2one('stock.picking',
                                                        'Stock Out')
                }
    
    def view_order_created(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        t_wizard = self.browse(cr, uid, ids[0])
        res_id = t_wizard.stock_picking_out_id.id
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'stock_makeover',
                                              'view_picking_isa_form')
        view_id = result and result[1] or False

        return {
              'name': _("Stock Picking Out"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'stock.picking',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'res_id': res_id,
              'context': context,
              'target': 'inlinenew',
              }
