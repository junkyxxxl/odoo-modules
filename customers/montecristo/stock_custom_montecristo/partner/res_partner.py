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


class res_partner(osv.osv):
    _inherit = "res.partner"

    _columns = {
        'financial_rating1': fields.integer('Rating Finanziario', help='Rating finanziario, compreso tra 0 e 9'),
        'financial_rating2': fields.integer('Rating Finanziario', help='Rating finanziario compreso tra 0 e 999'),
        'internal_rating': fields.integer('Rating Interno', help='Rating cliente compreso tra 0 e 9'),
    }

    def _check_rating(self, cr, uid, ids, context=None):
        financial_rating1 = self.browse(cr,uid,ids,context=context).financial_rating1
        financial_rating2 = self.browse(cr,uid,ids,context=context).financial_rating2
        internal_rating = self.browse(cr,uid,ids,context=context).internal_rating
        if  financial_rating1 < 0 or financial_rating1 > 9:
            return False
        if financial_rating2 < 0 or financial_rating2 > 999:
            return False
        if internal_rating < 0 or internal_rating > 9:
            return False
        return True

    _defaults = {
        'financial_rating1': 0,
        'financial_rating2': 0,
        'internal_rating': 0,
    }

    _constraints = [
        (_check_rating, 'Il rating finanziario deve essere composto di due numeri: il primo compreso tra 0 e 10 ed il secondo compreso tra 0 e 999;\nil rating interno deve essere compreso tra 0 e 9', 
         ['financial_rating1','financial_rating2','internal_rating']),
    ]

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context and 't_check' in context and context['t_check']:
            if args and isinstance(args[0],list) and len(args[0])==3 and args[0][2] and isinstance(args[0][2],list) and len(args[0][2][0])==3 and args[0][2][0][2]: 
                args = [('id','in',args[0][2][0][2])] 
        return super(res_partner,self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)
