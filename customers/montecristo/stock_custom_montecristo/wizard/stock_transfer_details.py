# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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
from openerp import api
from openerp.tools.translate import _

class stock_transfer_details_enhanced(osv.osv_memory):
    _inherit = 'stock.transfer_details'
    _description = 'Picking wizard'

    def _get_res_lines(self, cr, uid, ids, fields, args, context=None):
        line_obj = self.pool.get('stock.transfer_details_items')
        res = {}
        for transfer in self.browse(cr, uid, ids):
            args = [('transfer_id', '=', transfer.id)]
            if transfer.product_tmpl_id:
                args.append(('product_id.product_tmpl_id','=',transfer.product_tmpl_id.id))
            line_ids = line_obj.search(cr, uid, args, context=context)
            res[transfer.id] = line_ids
        return res
    
    def _set_res_lines(self, cr, uid, id, name, value, inv_arg, context):
        line_obj = self.pool.get('stock.transfer_details_items')
        for line in value:
            if line[0] == 1: # one2many Update
                line_id = line[1]
                line_obj.write(cr, uid, [line_id], line[2], context=context)
            if line[0] == 2:
                line_id = line[1]
                line_obj.unlink(cr, uid, [line_id], context=context)
        return True

    def _get_products(self, cr, uid, ids, name, args, context=None):
        result = {}
        for wizard in self.browse(cr, uid, ids, context=context):
            res = []
            for item in wizard.item_ids:
                res.append(item.product_id.product_tmpl_id.id)
            result[wizard.id] = res
        return result      

    _columns = {
                'product_tmpl_id': fields.many2one('product.template','Product Template'), 
                'product_tmpl_ids': fields.function(_get_products, string='Orders', relation="product.template", method=True, type="many2many"),
                'view_item_ids': fields.function(_get_res_lines, fnct_inv=_set_res_lines, string='Showed Transfer Lines', relation="stock.transfer_details_items", method=True, type="one2many"),
                
    }

    def button_dummy(self, cr, uid, ids, context=None):
        return self.wizard_view(cr, uid, ids[0], context=context)

    def button_clear_filter(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'product_tmpl_id':None},context=context)
        return self.wizard_view(cr, uid, ids[0], context=context)
  