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

class product_category_show_price(osv.osv):
    _inherit = "product.category"

    _columns = {
        'purchase_pricelist_ids': fields.one2many('product.pricelist.item','categ_id','Listini Fornitore', domain=[('price_version_id.pricelist_id.type','=','purchase'),('product_id','in',[False,None]),('product_tmpl_id','in',[False,None])]),                  
        'pricelist_ids': fields.one2many('product.pricelist.item','categ_id','Listini', domain=[('price_version_id.pricelist_id.type','=','sale'),('product_id','in',[False,None]),('product_tmpl_id','in',[False,None])]),  
    }

class product_template_show_price(osv.osv):
    _inherit = "product.template"

    _columns = {
        'purchase_pricelist_ids': fields.one2many('product.pricelist.item','product_tmpl_id','Listini Fornitore', domain=[('price_version_id.pricelist_id.type','=','purchase'),('product_id','in',[False,None])]),                  
        'pricelist_ids': fields.one2many('product.pricelist.item','product_tmpl_id','Listini', domain=[('price_version_id.pricelist_id.type','=','sale'),('product_id','in',[False,None])]),  
        'categ_purchase_pricelist_ids': fields.related('categ_id','purchase_pricelist_ids', type='one2many', relation='product.pricelist.item', string='Listini Fornitore di Categoria'),
        'categ_pricelist_ids': fields.related('categ_id','pricelist_ids', type='one2many', relation='product.pricelist.item', string='Listini di Categoria'),        
    }
    
class product_product_show_price(osv.osv):
    _inherit = "product.product"
    
    _columns = {
            'purchase_pricelist_ids': fields.one2many('product.pricelist.item','product_id','Listini Fornitore',domain=[('price_version_id.pricelist_id.type','=','purchase')]),                
            'pricelist_ids': fields.one2many('product.pricelist.item','product_id','Listini',domain=[('price_version_id.pricelist_id.type','=','sale')]),
            'template_pricelist_ids': fields.related('product_tmpl_id','pricelist_ids', type='one2many', relation='product.pricelist.item', string='Listini Padre'),
            'template_purchase_pricelist_ids': fields.related('product_tmpl_id','purchase_pricelist_ids', type='one2many', relation='product.pricelist.item', string='Listini Fornitore Padre'), 
            'categ_purchase_pricelist_ids': fields.related('categ_id','purchase_pricelist_ids', type='one2many', relation='product.pricelist.item', string='Listini Fornitore di Categoria'),
            'categ_pricelist_ids': fields.related('categ_id','pricelist_ids', type='one2many', relation='product.pricelist.item', string='Listini di Categoria'),                               
    }