##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class bom_massive_update_line(osv.osv_memory):
    _name = "bom.massive.update.line"
    _description = "BoM Massive Update Line"

    @api.model
    def _calculate_domain_row(self):
        if not self._context or 'active_ids' not in self._context or not self._context['active_ids']:
            return
        bom_obj = self.pool.get('mrp.bom')
        res = []
        for id in self._context['active_ids']:
            bom_data = bom_obj.browse(self._cr, self._uid, id)
            if bom_data.product_id:
                if bom_data.product_id.attribute_value_ids:
                    for id in  bom_data.product_id.attribute_value_ids.ids:
                        res.append(id)
            else:
                if bom_data.product_tmpl_id.attribute_line_ids:
                    for attribute_line in bom_data.product_tmpl_id.attribute_line_ids:
                        if attribute_line.value_ids:
                            for id in attribute_line.value_ids.ids:
                                res.append(id)
        res = list(set(res))        
        return [('id', 'in', res),('attribute_id.position','=','row')]
    
    @api.model
    def _calculate_domain_column(self):
        if not self._context or 'active_ids' not in self._context or not self._context['active_ids']:
            return
        bom_obj = self.pool.get('mrp.bom')
        res = []
        for id in self._context['active_ids']:
            bom_data = bom_obj.browse(self._cr, self._uid, id)
            if bom_data.product_id:
                if bom_data.product_id.attribute_value_ids:
                    for id in  bom_data.product_id.attribute_value_ids.ids:
                        res.append(id)
            else:
                if bom_data.product_tmpl_id.attribute_line_ids:
                    for attribute_line in bom_data.product_tmpl_id.attribute_line_ids:
                        if attribute_line.value_ids:
                            for id in attribute_line.value_ids.ids:
                                res.append(id)
        res = list(set(res))        
        return [('id', 'in', res),('attribute_id.position','=','column')]    

    _columns = {
        'type': fields.selection([('normal', 'Normal'), ('phantom', 'Phantom')], 'BoM Line Type', required=True,
                help="Phantom: this product line will not appear in the raw materials of manufacturing orders,"
                     "it will be directly replaced by the raw materials of its own BoM, without triggering"
                     "an extra manufacturing order."),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_qty': fields.float('Product Quantity', required=True, digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"),
        'product_efficiency': fields.float('Manufacturing Efficiency', required=True, help="A factor of 0.9 means a loss of 10% within the production process."),
        'attribute_value_row_ids': fields.many2many('product.attribute.value', 'rel_wizard_row', string='Row Variants', help="BOM Product Variants needed form apply this line.", domain=_calculate_domain_row),
        'attribute_value_column_ids': fields.many2many('product.attribute.value', 'rel_wizard_column', string='Column Variants', help="BOM Product Variants needed form apply this line.", domain=_calculate_domain_column),        
        'wizard_id': fields.many2one('bom.massive.update', 'Wizard'),
    }
       
    def _get_uom_id(self, cr, uid, *args):
        return self.pool["product.uom"].search(cr, uid, [], limit=1, order='id')[0]   
    
    _defaults = {
        'product_qty': lambda *a: 1.0,
        'product_efficiency': lambda *a: 1.0,
        'type': lambda *a: 'normal',
        'product_uom': _get_uom_id,
    }

    _sql_constraints = [
        ('bom_qty_zero', 'CHECK (product_qty>0)', 'All product quantities must be greater than 0.\n'),
    ]    

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        """ Changes UoM if product_id changes.
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        res = {}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            res['value'] = {
                'product_uom': prod.uom_id.id,
            }
        return res

class bom_massive_update(osv.osv_memory):
    _name = "bom.massive.update"
    _description = "BoM Massive Update"

    _columns = {
        'bom_ids': fields.many2many('mrp.bom', string='BoMs'),
        'line_ids': fields.one2many('bom.massive.update.line','wizard_id','Lines'),
    }

    def _get_ids(self, cr, uid, context = None):
        if not context or 'active_ids' not in context or not context['active_ids']:
            return
        return context['active_ids']
    
    _defaults = {
        'bom_ids': _get_ids,
    }
    
    def _get_attribute_values(self, cr, uid, template_id, context = None):
        tmpl_data = self.pool.get('product.template').browse(cr, uid, template_id)
        res = []
        for line in tmpl_data.attribute_line_ids:
            for value_id in line.value_ids.ids:
                res.append(value_id)
        return res

    def insert_update(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids)[0]
        bom_line_obj = self.pool.get('mrp.bom.line')
        for bom in wizard.bom_ids:
            for line in wizard.line_ids:
                #CASO IN CUI NON CI SIANO VARIANTI
                if not line.attribute_value_row_ids and not line.attribute_value_column_ids: 
                    vals = {
                            'bom_id': bom.id, 
                            'product_id': line.product_id.id,
                            'product_qty': line.product_qty,
                            'product_uom': line.product_uom.id,
                            'product_efficiency': line.product_efficiency,
                    }
                    bom_line_obj.create(cr, uid, vals)      
                #CASO IN CUI CI SIANO VARIANTI DI COLONNA MA NON VARIANTI DI RIGA  
                elif not line.attribute_value_row_ids and line.attribute_value_column_ids:
                    for value in line.attribute_value_column_ids:
                        if (bom.product_id and value.id in bom.product_id.attribute_value_ids.ids) or (not bom.product_id and value.id in self._get_attribute_values(cr,uid,bom.product_tmpl_id.id)):
                            vals = {
                                    'bom_id': bom.id, 
                                    'product_id': line.product_id.id,
                                    'product_qty': line.product_qty,
                                    'product_uom': line.product_uom.id,
                                    'product_efficiency': line.product_efficiency,
                                    'attribute_value_ids': [(6,0,[value.id])],
                            }
                            bom_line_obj.create(cr, uid, vals)  
                #CASO IN CUI CI SIANO VARIANTI DI RIGA MA NON VARIANTI DI COLONNA
                elif line.attribute_value_row_ids and not line.attribute_value_column_ids:
                    for value in line.attribute_value_row_ids:
                        if (bom.product_id and value.id in bom.product_id.attribute_value_ids.ids) or (not bom.product_id and value.id in self._get_attribute_values(cr,uid,bom.product_tmpl_id.id)):
                            vals = {
                                    'bom_id': bom.id, 
                                    'product_id': line.product_id.id,
                                    'product_qty': line.product_qty,
                                    'product_uom': line.product_uom.id,
                                    'product_efficiency': line.product_efficiency,
                                    'attribute_value_ids': [(6,0,[value.id])],
                            }
                            bom_line_obj.create(cr, uid, vals)                 
                #CASO IN CUI CI SIANO ENTRAMBE LE VARIANTI
                else:
                    for value1 in line.attribute_value_column_ids:
                        for value2 in line.attribute_value_row_ids:
                            if (bom.product_id and value1.id in bom.product_id.attribute_value_ids.ids and value2.id in bom.product_id.attribute_value_ids.ids) or (not bom.product_id and value1.id in self._get_attribute_values(cr,uid,bom.product_tmpl_id.id) and value2.id in self._get_attribute_values(cr,uid,bom.product_tmpl_id.id)):
                                vals = {
                                        'bom_id': bom.id, 
                                        'product_id': line.product_id.id,
                                        'product_qty': line.product_qty,
                                        'product_uom': line.product_uom.id,
                                        'product_efficiency': line.product_efficiency,
                                        'attribute_value_ids': [(6,0,[value1.id,value2.id])],
                                }
                                bom_line_obj.create(cr, uid, vals)                     
        return
        
    def remove_update(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids)[0]
        bom_line_obj = self.pool.get('mrp.bom.line')
        for bom in wizard.bom_ids:
            for line in wizard.line_ids:
                #CASO IN CUI NON CI SIANO VARIANTI
                if not line.attribute_value_row_ids and not line.attribute_value_column_ids: 
                    line_ids = bom_line_obj.search(cr, uid, [('bom_id', '=', bom.id),('product_id','=',line.product_id.id)])
                    bom_line_obj.unlink(cr, uid, line_ids)      
                #CASO IN CUI CI SIANO VARIANTI DI COLONNA MA NON VARIANTI DI RIGA  
                elif not line.attribute_value_row_ids and line.attribute_value_column_ids:
                    for value in line.attribute_value_column_ids:
                        if (bom.product_id and value.id in bom.product_id.attribute_value_ids.ids) or (not bom.product_id and value.id in self._get_attribute_values(cr,uid,bom.product_tmpl_id.id)):
                            line_ids = bom_line_obj.search(cr, uid, [('bom_id', '=', bom.id),('product_id','=',line.product_id.id)])
                            for id in line_ids:
                                if value in bom_line_obj.browse(cr, uid, id).attribute_value_ids:                                       
                                    bom_line_obj.unlink(cr, uid, id)  
                #CASO IN CUI CI SIANO VARIANTI DI RIGA MA NON VARIANTI DI COLONNA
                elif line.attribute_value_row_ids and not line.attribute_value_column_ids:
                    for value in line.attribute_value_row_ids:
                        if (bom.product_id and value.id in bom.product_id.attribute_value_ids.ids) or (not bom.product_id and value.id in self._get_attribute_values(cr,uid,bom.product_tmpl_id.id)):
                            line_ids = bom_line_obj.search(cr, uid, [('bom_id', '=', bom.id),('product_id','=',line.product_id.id)])
                            for id in line_ids:
                                if value in bom_line_obj.browse(cr, uid, id).attribute_value_ids:                                       
                                    bom_line_obj.unlink(cr, uid, id)               
                #CASO IN CUI CI SIANO ENTRAMBE LE VARIANTI
                else:
                    for value1 in line.attribute_value_column_ids:
                        for value2 in line.attribute_value_row_ids:
                            if (bom.product_id and value1.id in bom.product_id.attribute_value_ids.ids and value2.id in bom.product_id.attribute_value_ids.ids) or (not bom.product_id and value1.id in self._get_attribute_values(cr,uid,bom.product_tmpl_id.id) and value2.id in self._get_attribute_values(cr,uid,bom.product_tmpl_id.id)):
                                line_ids = bom_line_obj.search(cr, uid, [('bom_id', '=', bom.id),('product_id','=',line.product_id.id)])
                                for id in line_ids:
                                    if value1 in bom_line_obj.browse(cr, uid, id).attribute_value_ids and value2 in bom_line_obj.browse(cr, uid, id).attribute_value_ids:                                       
                                        bom_line_obj.unlink(cr, uid, id)                    
        return

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
