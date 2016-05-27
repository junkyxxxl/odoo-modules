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
import openerp.addons.decimal_precision as dp


class product_product_mattioli(osv.osv):
    _inherit = "product.product"

    _columns = {
            'ean13': fields.char('Barcode', size=128, help="International Article Number used for product identification."),
            'uos_id' : fields.many2one('product.uom', 'Unit of Sale',
                help='Specify a unit of measure here if invoicing is made in another unit of measure than inventory. Keep empty to use the default unit of measure.'),
            'uos_coeff': fields.float('Unit of Measure -> UOS Coeff', digits_compute= dp.get_precision('Product UoS'),help='Coefficient to convert default Unit of Measure to Unit of Sale\n uos = uom * coeff'),
            'uos_coeff_deincr' : fields.float('Unit of Measure -> UOS Coeff Non-Incremented', digits_compute= dp.get_precision('Product UoS')),            
    }
    
    _defaults = {
            'uos_coeff': 1.0,
            'uos_coeff_incr' : 1.0,
    }

    def _check_ean_key(self, cr, uid, ids, context=None):
        return True

    _constraints = [(_check_ean_key, 'You provided an invalid "EAN13 Barcode" reference. You may use the "Internal Reference" field instead.', ['ean13'])]
        
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['default_code'] = self.pool.get('ir.sequence').get(cr, uid, 'product.product') or ''
        if 'ean13' not in vals or not vals['ean13']:
            vals['ean13'] = vals['default_code']
        prod_id = super(product_product_mattioli, self).create(cr, uid, vals, context)
        if ('is_wood' in vals and vals['is_wood']) or ('product_tmpl_id' in vals and self.pool.get('product.template').browse(cr,uid,vals['product_tmpl_id']) and self.pool.get('product.template').browse(cr,uid,vals['product_tmpl_id']).is_wood):
            uos_coeff = self._get_volume(cr,uid,prod_id, True)
            uos_coeff_deincr = self._get_volume(cr,uid,prod_id, False)
            if not uos_coeff:
                if 'volume' in vals and vals['volume']:
                    uos_coeff = vals['volume']
                    uos_id = self.pool.get('product.uom').search(cr,uid,[('is_cubic_meter','=',True)])                    
                else:
                    uos_coeff = self._get_surface(cr,uid,prod_id, True)
                    uos_coeff_deincr = self._get_surface(cr,uid,prod_id, False)
                    if uos_coeff:
                        uos_id = self.pool.get('product.uom').search(cr,uid,[('is_square_meter','=',True)])
                    else:
                        uos_coeff = 1.0
                        uos_coeff_incr = 1.0
                        uos_id = None
            else:
                uos_id = self.pool.get('product.uom').search(cr,uid,[('is_cubic_meter','=',True)])
            self.write(cr,uid,prod_id,{'uos_coeff':uos_coeff, 'uos_coeff_deincr':uos_coeff_deincr, 'uos_id':uos_id[0]})
        return prod_id

    def onchange_is_wood(self, cr, uid, ids, flag, context=None):
        return self.pool.get("product.template").onchange_is_wood(cr, uid, ids, flag, context)

    def _get_size(self, cr, uid, prod_id, field):
        res = 0
        cr.execute("""
                    SELECT 
                        val.name
                    FROM
                        product_attribute_value_product_product_rel AS vp_rel,
                        product_attribute_line_product_attribute_value_rel AS lv_rel,
                        product_attribute AS att,
                        product_attribute_value AS val,
                        product_attribute_line AS lin,
                        product_product AS prd
                    WHERE
                        prd.id = %s AND
                        vp_rel.prod_id = prd.id AND
                        vp_rel.att_id = lv_rel.val_id AND
                        lv_rel.line_id = lin.id AND
                        lin.attribute_id = att.id AND
                        lin.product_tmpl_id = prd.product_tmpl_id AND
                        lv_rel.val_id = val.id AND
                        att.name = %s
                """,
                (prod_id, field))
        qry = cr.fetchall()
        if qry and qry[0] and qry[0][0]:
            try:
                res = float(qry[0][0])
            except:
                None
                
        else:
            cr.execute("""
                        SELECT
                            val.name
                        FROM
                            product_attribute_line_product_attribute_value_rel AS lv_rel,
                            product_attribute AS att,
                            product_attribute_line AS lin,
                            product_product AS prd,
                            product_template AS tmpl,
                            product_attribute_value AS val
                        WHERE
                            prd.id = %s AND
                            prd.product_tmpl_id = tmpl.id AND
                            lin.product_tmpl_id = tmpl.id AND
                            lin.attribute_id = att.id AND    
                            lv_rel.line_id = lin.id AND
                            lv_rel.val_id = val.id AND
                            att.name = %s
                    """,
                    (prod_id, field))
            qry = cr.fetchall()
            if qry and qry[0] and qry[0][0]:
                try:
                    res = float(qry[0][0])
                except:
                    None                                
        return res

    def _get_volume(self, cr, uid, prod_id, increment):
        volume = 0
        prod_data = self.browse(cr,uid,prod_id)
        temp_thickness = prod_data.thickness
        temp_width = self._get_size(cr, uid, prod_id,"Larghezza")
        temp_length = self._get_size(cr, uid, prod_id,"Lunghezza")
        
        if increment:
            if prod_data.increment_thickness:
                if prod_data.increment_uom_thickness == 'cm':
                    temp_thickness += prod_data.increment_thickness
                else:
                    temp_thickness *= 1+(prod_data.increment_thickness/100)
                
            if prod_data.increment_width:
                if prod_data.increment_uom_width == 'cm':
                    temp_width += prod_data.increment_width
                else:
                    temp_width *= 1+(prod_data.increment_width/100)
            
            if prod_data.increment_length:
                if prod_data.increment_uom_length == 'cm':
                    temp_length += prod_data.increment_length
                else:
                    temp_length *= 1+(prod_data.increment_length/100)

        volume = temp_width*temp_length*temp_thickness
        volume = volume/1000000
        return volume

    def _get_surface(self, cr, uid, prod_id, increment):
        surface = 0
        prod_data = self.browse(cr,uid,prod_id)
        temp_width = self._get_size(cr, uid, prod_id,"Larghezza")
        temp_length = self._get_size(cr, uid, prod_id,"Lunghezza")
        
        if increment:
            if prod_data.increment_width:
                if prod_data.increment_uom_width == 'cm':
                    temp_width += prod_data.increment_width
                else:
                    temp_width *= 1+(prod_data.increment_width/100)
            
            if prod_data.increment_length:
                if prod_data.increment_uom_length == 'cm':
                    temp_length += prod_data.increment_length
                else:
                    temp_length *= 1+(prod_data.increment_length/100)

        surface = temp_width*temp_length
        surface = surface/10000
        return surface

