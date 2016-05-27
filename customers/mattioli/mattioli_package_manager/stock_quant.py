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
from openerp.tools.translate import _

class stock_quant(osv.Model):
    _inherit = "stock.quant"
    
    def quants_get_prefered_domain(self, cr, uid, location, product, qty, domain=None, prefered_domain_list=[], restrict_lot_id=False, restrict_partner_id=False, context=None):
        if domain is None:
            domain = []

        if 'lines' in context and len(context['lines'])>0:            
            flag = True
            while flag == True:
                flag = False
                for i in range(0,len(domain)):
                    p = domain[i]
                    if type(p) == type(tuple()) and p[0] == 'package_id':
                        del domain[i]
                        flag = True
                        break
                                
            for line in context['lines']:
                
                for i in range(0,len(prefered_domain_list)):
                    p = prefered_domain_list[i][0]
                    if type(p) == type(tuple()) and p[0]=='reservation_id' and p[2]==line[1]:
                        del prefered_domain_list[i]
                        
                pckg = self.pool.get('stock.move').browse(cr,uid,line[1],context=context).procurement_id.sale_line_id.package_id
                if pckg: 
                    domain += [('package_id', '=', pckg.id)]
                else:
                    domain += [('package_id', "in", [False,None])]   
             
                domain += location and ['|',('location_id', 'child_of', location.id),('location_id','=',location.id)] or []
        return super(stock_quant, self).quants_get_prefered_domain(cr, uid, location, product, qty, domain, prefered_domain_list, restrict_lot_id, restrict_partner_id, context)

    def _quants_get_order(self, cr, uid, location, product, quantity, domain=[], orderby='in_date', context=None):
        return super(stock_quant,self)._quants_get_order(cr,uid,None,product,quantity,domain,orderby,context)