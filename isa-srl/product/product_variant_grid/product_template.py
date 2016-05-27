# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class product_product(orm.Model):
    _inherit = 'product.product'
    
    def get_active(self, cr, uid, id, context=None):
        if self.browse(cr, uid, id).active and self.browse(cr, uid, id).sale_ok:
            return True
        return False
        

class product_template(orm.Model):
    _inherit = 'product.template'
    
        
    def _get_attributes_count(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for template_id in ids:
            count = len(self.browse(cr,uid,template_id).attribute_line_ids.ids)
            res[template_id] = int(count)
        return res
    
    _columns = {
        'attr_count': fields.function(
                                      _get_attributes_count, 
                                      type='integer', 
                                      string='# of Product Attributes',
                                      store=True,
                                      ),
        }
        
    def get_template_dimension_count(self, cr, uid, template_id, value_filter_id=None, context=None):
        if template_id == False:
            return False
        cr.execute('SELECT COUNT(attribute_id) FROM product_attribute_line WHERE product_tmpl_id = %s', (template_id,))            
        count = cr.fetchone()[0]
        if value_filter_id:
            count = count - 1
        return count
    
    def get_template_dimension(self, cr, uid, template_id, value_filter_id=None, context=None):
        if template_id == False:
            return False
        res = []
        cr.execute('SELECT lin.attribute_id, att.name FROM product_attribute_line AS lin, product_attribute AS att WHERE lin.product_tmpl_id = %s AND lin.attribute_id = att.id ORDER BY att.position, lin.attribute_id DESC', (template_id,))
        res = cr.fetchall()
        if res and value_filter_id:
            del res[-1]
        return res
    
    def get_dimension_options(self, cr, uid, template_id, dimension_id, context=None):
        if template_id == False:
            return False
        res = []
        cr.execute('SELECT val.id, val.name FROM product_attribute_value AS val, product_attribute_line_product_attribute_value_rel AS rel, product_attribute_line AS lin WHERE lin.attribute_id = %s AND lin.product_tmpl_id = %s AND lin.id = rel.line_id AND val.id = rel.val_id ORDER BY val.sequence, val.name', (dimension_id, template_id))
        res = cr.fetchall()
        return res
    
    def get_product_list(self, cr, uid, template_id, value_filter_id=None, context=None):
        if template_id == False:
            return False        
        res = []
        if not value_filter_id:
            cr.execute(''' SELECT prod.id AS "PRODUCT", 
                            (
                                SELECT val.id as "ID_Option1"
                                FROM product_attribute_value AS val
                                WHERE val.id IN 
                                    (
                                        SELECT pd_rel.att_id
                                        FROM product_attribute_value_product_product_rel AS pd_rel
                                        WHERE pd_rel.prod_id = prod.id
                                    )
                                ORDER BY val.attribute_id ASC
                                LIMIT 1
                            ),
                            (
                                SELECT val.id as "ID_Option1"
                                FROM product_attribute_value AS val
                                WHERE val.id IN 
                                    (
                                        SELECT pd_rel.att_id
                                        FROM product_attribute_value_product_product_rel AS pd_rel
                                        WHERE pd_rel.prod_id = prod.id
                                    )
                                ORDER BY val.attribute_id DESC
                                LIMIT 1
                            )
                        FROM product_product AS prod
                        WHERE prod.product_tmpl_id = %s''',
            (template_id,))
        else:
            cr.execute(''' SELECT qry.PRODUCT, qry.ID_Option1, qry.ID_Option2
                            FROM 
                            (
                                SELECT prod.id AS product, 
                                (
                                    SELECT val.id as ID_Option1
                                    FROM product_attribute_value AS val
                                    WHERE val.id IN 
                                    (
                                        SELECT pd_rel.att_id
                                        FROM product_attribute_value_product_product_rel AS pd_rel
                                        WHERE pd_rel.prod_id = prod.id
                                    )
                                    ORDER BY val.attribute_id DESC
                                    LIMIT 1
                                ),
                                (
                                    SELECT val.id as ID_Option2
                                    FROM product_attribute_value AS val
                                    WHERE val.id IN 
                                    (
                                        SELECT pd_rel.att_id
                                        FROM product_attribute_value_product_product_rel AS pd_rel
                                        WHERE pd_rel.prod_id = prod.id
                                    )
                                    ORDER BY val.attribute_id ASC
                                    LIMIT 1
                                )
                                FROM product_product AS prod
                                WHERE prod.product_tmpl_id = %s
                            ) AS qry
                            WHERE id_option2 = %s''',
            (template_id,value_filter_id))            
        t_res = cr.fetchall()
        
        keys = {}
        for line in t_res:
            key = (line[1],line[2])
            if key not in keys:
                keys[key] = []
            keys[key].append(line[0])
        
        for key in keys:
            res.append((max(keys[key]),key[0],key[1]))
        
        return res

