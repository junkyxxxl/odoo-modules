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
import re
from openerp.osv import fields, osv, expression


class product_template_montecristo(osv.osv):
    _inherit = "product.template"

    def _get_showed_name(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for item in self.browse(cr, uid, ids, context=context):
            result[item.id] = item.id
        return result

    _columns = {
        'famiglia': fields.many2one('res.family', 'Famiglia'),
        'sottofamiglia': fields.many2one('res.family', 'Sottofamiglia'),
        'sottogruppo': fields.many2one('res.family', 'Sottogruppo'),
        'composizione': fields.many2one('res.family', 'Composizione'),         
        'origine': fields.many2one('res.family', 'Origine'),
        'produzione': fields.many2one('res.family', 'Produzione'),
        'tmpl_default_code' : fields.char('Riferimento interno', select=True),
        'is_shipping': fields.boolean('Spedizione'),
        'pricelist_ids': fields.one2many('product.pricelist.item','product_tmpl_id','Listini', domain=[('product_id','in',[False,None])]),  
        'showed_name' : fields.function(_get_showed_name, type='many2one', relation="product.template", string='Nome', select=True, readonly=True, store= True),     
    }

    #_sql_constraints = [('code_uniq', 'unique (tmpl_default_code)', 'Il Riferimento Interno scelto è già associato ad un altro prodotto!')]
    
    _defaults = {
        'is_shipping':False,
    }

    def remove_from_quotation(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        template_obj = self.pool.get('product.template')
        
        order_ids = order_obj.search(cr, uid, [('state','in',['draft','sent']),('document_type_id','in',[False,None])],context=context)
        p_ids = product_obj.search(cr, uid, [('active','=',True),('sale_ok','=',False),('product_tmpl_id','in',ids)],context=context)
        line_ids = order_line_obj.search(cr, uid, [('order_id','in',order_ids),('product_id','in',p_ids)],context=context)
            

        if line_ids:
            order_line_obj.unlink(cr,uid,line_ids,context=context)
          
        return
        
    def create_variant_ids(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        tmpl_default_code = self.browse(cr,uid,ids[0]).tmpl_default_code
        standard_price = self.browse(cr,uid,ids[0]).standard_price
        sale_ok =  self.browse(cr,uid,ids[0]).sale_ok
        if tmpl_default_code:
            context.update({'tmpl_default_code':tmpl_default_code})
        if standard_price:
            context.update({'standard_price':standard_price})            
        context.update({'sale_ok':sale_ok})
        return super(product_template_montecristo,self).create_variant_ids(cr,uid,ids,context)
    
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','tmpl_default_code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['tmpl_default_code']:
                name = '['+record['tmpl_default_code']+'] - '+name
            res.append((record['id'], name))
        return res    

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            ids = []
            if operator in positive_operators:
                ids = self.search(cr, user, [('tmpl_default_code','=',name)]+ args, limit=limit, context=context)
            if not ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set(self.search(cr, user, args + [('tmpl_default_code', operator, name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(ids)) if limit else False
                    ids.update(self.search(cr, user, args + [('name', operator, name)], limit=limit2, context=context))
                ids = list(ids)
            elif not ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                ids = self.search(cr, user, args + ['&', ('tmpl_default_code', operator, name), ('name', operator, name)], limit=limit, context=context)
            if not ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('tmpl_default_code','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
    
