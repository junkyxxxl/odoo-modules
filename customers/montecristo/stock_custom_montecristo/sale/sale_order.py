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
import openerp.addons.decimal_precision as dp
    
class sale_order_montecristo(osv.osv):
    _inherit = "sale.order"   

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context and 't_check' in context and context['t_check']:
            if args and isinstance(args[0],list) and len(args[0])==3 and args[0][2] and isinstance(args[0][2],list) and len(args[0][2][0])==3 and args[0][2][0][2]: 
                args = [('id','in',args[0][2][0][2])] 
        return super(sale_order_montecristo,self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


    def _get_stock_number_txt(self, cr, uid, ids, field_name, arg, context=None):
        r = {}
        for id in ids:
            order = self.browse(cr, uid, id)
            r[id] = str(order.stock_number).rjust(4, '0')
        return r
    
    _columns = {
                'stock_number': fields.integer('Numero magazzino'),
                'package_number': fields.integer('Numero pacchi'),
                'stock_number_txt' : fields.function(_get_stock_number_txt, type='char', string='Numero Magazzino',
                    store={
                           'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['stock_number'], 10),
                    }),
    }

    def _check_stock_number(self, cr, uid, ids, context=None):
        this = self.browse(cr,uid,ids)
        if not this.stock_number:
            return True
        if not this or not this.season:
            return False

        check = self.search(cr,uid,[('season','=',this.season.id),('stock_number','=',this.stock_number),('id','!=',this.id),('partner_id','!=',this.partner_id.id)])
        if check:
            return False
        return True   

    _constraints = [
        (_check_stock_number, 'Il numero di magazzino impostato è già assegnato ad un altro ordine della stessa stagionalità.', 
         ['season','stock_number']),
    ]


    