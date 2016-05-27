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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError

class sale_order_bill(models.Model):

    _inherit = 'sale.order'
    
    @api.multi
    def action_print_bill(self):
        invoices = [] 
        mod_obj = self.env['ir.model.data']
        result = mod_obj.get_object_reference('sale_order_pos_primapaint','wizard_sale_print_bill_view')
        view_id = result and result[1] or False

        return {'domain': "[('id','in', ["+','.join(map(str,invoices))+"])]",
                'name': _("Print Bill"),
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wizard.sale.print.bill',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'view_mode':True},
                'views': [(view_id,'form'),(False,'tree')],
                }