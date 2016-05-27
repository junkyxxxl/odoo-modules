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
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from datetime import datetime

class stock_reservation_product(osv.osv):
    
    _inherit = 'stock.reservation.product'

    def _get_delivery_date(self, cr, uid, ids, field_name, arg, context=None):

        r = {}
        
        for id in ids:
            line = self.browse(cr, uid, id, context=context)

            try:

                if line.order_id or (line.move_id and line.move_id.procurement_id and line.move_id.procurement_id.sale_line_id and line.move_id.procurement_id.sale_line_id.order_id):

                    if line.order_id:
                        order = line.order_id
                    else:
                        order = line.move_id.procurement_id.sale_line_id.order_id
                    
                    if line.product_id and line.product_id.categ_id:
                        if line.product_id.categ_id.parent_id:
                            category_id = line.product_id.categ_id.parent_id.id
                        else:
                            category_id = line.product_id.categ_id.id
                            
                    elif line.move_id and line.move_id.product_id: 
                        if line.move_id.product_id.categ_id.parent_id:
                            category_id = line.move_id.product_id.categ_id.parent_id.id
                        else:
                            category_id = line.move_id.product_id.categ_id.id                        
                                                           
                    find = False
                    
                    if order.date_per_category_ids:
                        for dc_line in order.date_per_category_ids:
                            if dc_line.category_id.id == category_id:
                                find = True
                                r[id] = dc_line.delivery_date

                    if not find:            
                        line_id = self.pool.get('res.family.category.date').search(cr, uid, [('family_id','=',order.season.id),('category_id','=',category_id)], context=context)
                        if line_id:
                            find = True
                            r[id] = self.pool.get('res.family.category.date').browse(cr, uid, line_id[0],context=context).begin_date
                        else:
                           r[id] = order.delivery_date
         
                else:
                    r[id] = line.move_id.date_expected
                    
            except:
                None
            
        return r

    _columns = {
                'delivery_date': fields.function(_get_delivery_date, type='date', string='Delivery Date', store=True),   
                'rating': fields.related('move_id','partner_id','internal_rating', type='integer', string='Internal Rating', store = True),
    }

    _order = 'delivery_date ASC, rating DESC, move_id ASC, id ASC'
