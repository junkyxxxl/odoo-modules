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

class stock_quant(orm.Model):
    _inherit = 'stock.quant'
    _columns = {

        'product_tmpl_id' : fields.related(
                                            'product_id',
                                            'product_tmpl_id',
                                            type="many2one",
                                            relation="product.template",
                                            string="Template"
                                            ),
        'wizard_id' : fields.many2one('wizard.product.variant.quantities', 
                                      'Wizard'),
                }
        
    
    def create(self, cr, uid, vals, context=None):
        return super(stock_quant, self).create(cr,uid,vals,context)
    
    def write(self, cr, uid, ids, vals, context=None):
        return super(stock_quant, self).write(cr, uid, ids, vals, context)
                
    def get_product_quantities(self, cr, uid, template_id, location_id, company_id, context=None):
        if template_id == False or location_id == False or company_id == False:
            return False
        res = []
        cr.execute('''SELECT prod.id AS "PRODUCT", qty.qty AS "QTY"
                    FROM     stock_quant AS qty, product_product AS prod
                    WHERE qty.product_id IN 
                        (
                            SELECT DISTINCT
                                prod.id AS "ID"
                            FROM    
                                product_product AS prod,
                                product_attribute_value_product_product_rel AS pd_rel,
                                product_attribute_value AS val,
                                product_attribute AS typ,
                                product_attribute_line AS lin
                            WHERE
                                pd_rel.prod_id = prod.id AND
                                pd_rel.att_id = val.id AND
                                val.attribute_id = typ.id AND
                                typ.id = lin.attribute_id AND
                                lin.product_tmpl_id = %s AND
                                prod.product_tmpl_id = lin.product_tmpl_id
                            ORDER BY 
                                prod.id 
                        ) AND 
                        qty.product_id = prod.id AND
                        qty.location_id = %s AND
                        qty.company_id = %s''',
        (template_id,location_id,company_id,))
        res = cr.fetchall()
        return res

