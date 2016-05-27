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


class product_template(osv.osv):
    _inherit = "product.template"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context and 't_check' in context and context['t_check']:
            if args and isinstance(args[0],list) and len(args[0])==3 and args[0][2] and isinstance(args[0][2],list) and len(args[0][2][0])==3 and args[0][2][0][2]: 
                args = [('id','in',args[0][2][0][2])] 
        return super(product_template,self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)
