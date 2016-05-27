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

class stock_transfer_details_enhanced(models.TransientModel):
    _inherit = 'stock.transfer_details'
    _description = 'Picking wizard'

    @api.multi
    def select_all(self):
        item_obj = self.pool.get('stock.transfer_details_items')
        for item in self.item_ids:
            item_obj.write(self._cr, self._uid, item.id, {'selected':True}, self._context)            
        return self[0].wizard_view()
    
    @api.multi    
    def invert_selection(self):
        item_obj = self.pool.get('stock.transfer_details_items')
        for item in self.item_ids:
            if item_obj.browse(self._cr, self._uid, item.id, self._context).selected:
                flag = False
            else:
                flag = True
            item_obj.write(self._cr, self._uid, item.id, {'selected':flag})    
        return self[0].wizard_view()

    @api.multi    
    def delete_selected(self):
        item_obj = self.pool.get('stock.transfer_details_items')
        for item in self.item_ids:
            if item_obj.browse(self._cr, self._uid, item.id, self._context).selected:
                item_obj.unlink(self._cr, self._uid, item.id, self._context)
        return self[0].wizard_view()


class stock_transfer_details_items_enhanced(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    selected = fields.Boolean(string="Select", default=True)
    partner_id = fields.Many2one('res.partner', string="Partner", store=True, related="transfer_id.picking_id.partner_id")
    company_id = fields.Many2one('res.company', string="Company", store=True, related="transfer_id.picking_id.company_id")
