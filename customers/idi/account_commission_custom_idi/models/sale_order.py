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

class sale_order_commission_idi(models.Model):

    _inherit = 'sale.order'

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = super(sale_order_commission_idi, self).onchange_partner_id(cr, uid, ids, partner_id, context=context)
        if res:
            current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            if current_user.salesagent:
                res['value'].update({'pricelist_id':(current_user.property_product_pricelist and current_user.property_product_pricelist.id) or False})
        return res