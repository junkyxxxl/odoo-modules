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

from openerp.osv import osv, fields

class analytic_user_funct_grid(osv.osv):
    _inherit="analytic.user.funct.grid"

    _columns = {
                'date_from': fields.datetime('Valido da'),
                'date_to': fields.datetime('Valido fino a'),
    } 

    def onchange_user_product_id(self, cr, uid, ids, user_id, product_id, context=None):
        if not user_id:
            return {}
        emp_obj = self.pool.get('hr.employee')
        cmp_id = self.pool.get('res.users').browse(cr,uid,user_id).company_id.id
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', user_id),('company_id','=', cmp_id)])        
        if not emp_id:
            return {}

        value = {}
        prod = False
        if product_id:
           prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        emp = emp_obj.browse(cr, uid, emp_id[0], context=context)
        if emp.product_id and not product_id:
            value['product_id'] = emp.product_id.id
            prod = emp.product_id
        if prod:
            value['price'] = prod.list_price
            value['uom_id'] = prod.uom_id.id
        return {'value': value}
