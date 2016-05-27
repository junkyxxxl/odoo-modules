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

class product_template(orm.Model):
    _inherit = 'product.template'
                
    def get_dimension_options(self, cr, uid, template_id, dimension_id, context=None):
        if template_id == False:
            return False
        res = []
        
        position = self.pool.get('product.attribute').browse(cr,uid,dimension_id).position
        if position == 'row':
            sql = 'SELECT val.id, val.name FROM product_attribute_value AS val, product_attribute_line_product_attribute_value_rel AS rel, product_attribute_line AS lin WHERE lin.attribute_id = ' + str(dimension_id) + ' AND lin.product_tmpl_id = ' + str(template_id) + ' AND lin.id = rel.line_id AND val.id = rel.val_id ORDER BY val.name, val.sequence'
        else:
            sql = 'SELECT val.id, val.name FROM product_attribute_value AS val, product_attribute_line_product_attribute_value_rel AS rel, product_attribute_line AS lin WHERE lin.attribute_id = ' + str(dimension_id) + ' AND lin.product_tmpl_id = ' + str(template_id) + ' AND lin.id = rel.line_id AND val.id = rel.val_id ORDER BY val.sequence, val.name'
        cr.execute(sql)
        res = cr.fetchall()
        return res
    


