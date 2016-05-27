# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

class product_template_omniapart(osv.osv):
    _inherit = "product.template"

    _columns = {
                'categ_id': fields.many2one('product.category','Internal Category', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Select category for the current product"),                
    }
    
    def _default_category(self, cr, uid, context=None):
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, context=context)
        
        categ_id = self.pool.get('product.category').search(cr,uid,[('parent_id','in',[None, False]),('company_id','=',company_id)])
        if categ_id:
            categ_id = categ_id[0]
        else:
            return False

        return categ_id    
    
    _defaults = {
        'categ_id' : _default_category,
    }
    
    
    
class product_category_omniapart(osv.osv):
    
    _inherit = 'product.category'
    
    _columns = {
                'company_id': fields.many2one('res.company', string='Company'),
    }
    
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, context=c),
    }