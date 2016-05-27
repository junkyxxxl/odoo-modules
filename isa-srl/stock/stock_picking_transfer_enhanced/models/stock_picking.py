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

from openerp import models, fields, api
from openerp.tools.translate import _


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def select_all(self):
        item_obj = self.pool.get('stock.move')
        for item in self.move_lines:
            item_obj.write(self._cr, self._uid, item.id, {'selected':True}, self._context)
        return True

    @api.multi
    def invert_selection(self):
        item_obj = self.pool.get('stock.move')
        for item in self.move_lines:
            flag = True
            if item_obj.browse(self._cr, self._uid, item.id, self._context).selected:
                flag = False
            item_obj.write(self._cr, self._uid, item.id, {'selected':flag})
        return True

    @api.multi
    def delete_selected(self):
        item_obj = self.pool.get('stock.move')
        for item in self.move_lines:
            if item_obj.browse(self._cr, self._uid, item.id, self._context).selected:
                item_obj.write(self._cr, self._uid, item.id, {'product_uom_qty':0.0})
        return True

    @api.multi
    def restore_selected(self):
        item_obj = self.pool.get('stock.move')
        for item in self.move_lines:
            if item_obj.browse(self._cr, self._uid, item.id, self._context).selected:
                item_obj.write(self._cr, self._uid, item.id, {'product_uom_qty':item.orig_quants})
        return True

    origin_picking_id = fields.Many2one('stock.picking',
                                          string="Picking d'origine")
    inv_picking_ids = fields.One2many('stock.picking',
                                        'origin_picking_id',
                                        string='Picking di rientro')