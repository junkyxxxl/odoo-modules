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

from openerp.osv import fields, osv


class sale_order_line_montecristo(osv.osv):
    _inherit = "sale.order.line"
    
    def _get_salesagent(self, cr, uid, ids=None, field_name=None, arg=None, context=None):
        res = {}
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        if isinstance(ids, list):
            for id in ids:
                res[id] = salesagent
            return res
        return salesagent

    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):
        
        res = super(sale_order_line_montecristo,self).product_id_change_with_wh(cr,uid,ids,pricelist,product,qty,uom,qty_uos,uos,name,partner_id,lang,update_tax,date_order,packaging,fiscal_position, flag,warehouse_id,context=context)
        
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        res['value']['salesagent'] = salesagent

        return res
    
    _columns = {
                'salesagent': fields.function(_get_salesagent, string="Agente", type="boolean"),
    }

    _defaults = {
                'salesagent': _get_salesagent,
    }