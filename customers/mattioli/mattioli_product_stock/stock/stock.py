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

from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp

class stock_picking_mattioli_ps(orm.Model):
    _inherit = "stock.picking"

    def _get_partner_to_invoice(self, cr, uid, picking, context=None):
        if picking.group_id:
            return super(stock_picking_mattioli_ps, self)._get_partner_to_invoice(cr, uid, picking, context=context)
        return picking.partner_id and picking.partner_id.id


class stock_move_mattioli(orm.Model):
    _inherit = "stock.move"

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move_mattioli, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)

        if move.procurement_id and move.procurement_id.sale_line_id:
            if move.procurement_id.sale_line_id.product_uom_qty and move.procurement_id.sale_line_id.product_uos and (move.procurement_id.sale_line_id.product_uos.is_cubic_meter or move.procurement_id.sale_line_id.product_uos.is_square_meter):
                res['length'] = move.procurement_id.sale_line_id.length
                res['width'] = move.procurement_id.sale_line_id.width
                res['thickness'] = move.procurement_id.sale_line_id.thickness
                res['uos_coeff'] = move.procurement_id.sale_line_id.product_uos_qty/move.procurement_id.sale_line_id.product_uom_qty
        return res
        
    def _get_master_data(self, cr, uid, move, company, context=None):
        partner, user_id, currency_id = super(stock_move_mattioli, self)._get_master_data(cr, uid, move, company, context=context)
        return partner, uid, currency_id

    def _create_invoice_line_from_vals(self, cr, uid, move, invoice_line_vals, context=None):
        if move.purchase_line_id:
            order_line = self.pool.get('purchase.order.line').browse(cr, uid, move.purchase_line_id.id, context=context)
            if order_line.product_uom and order_line.uos_id and order_line.uos_qty:
                if order_line.uos_id.is_cubic_meter or order_line.uos_id.is_square_meter:
                    invoice_line_vals['price_unit'] = (order_line.price_unit * order_line.product_qty)/order_line.uos_qty
                    invoice_line_vals['uos_id'] = order_line.uos_id.id
                    invoice_line_vals['quantity'] = order_line.uos_qty
        return super(stock_move_mattioli, self)._create_invoice_line_from_vals(cr, uid, move, invoice_line_vals, context=context)


class stock_quant(orm.Model):
    _inherit = "stock.quant"

    def _get_inventory_value(self, cr, uid, quant, context=None):
        if quant.uos_id and quant.uos_qty:
            return quant.product_id.standard_price * quant.uos_qty
        else:
            return quant.product_id.standard_price * quant.qty

    def _get_size(self, cr, prod_id, field):
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
        return res

    def _get_thickness(self, cr, uid, ids, name, arg, context=None):
        res = {}
        product_obj = self.pool.get('product.product')
        tmpl_obj = self.pool.get('product.template')
        for quant_id in self.browse(cr, uid, ids):
            product_id = product_obj.browse(cr,uid,quant_id.product_id.id)
            tmpl_id = tmpl_obj.browse(cr,uid,product_id.product_tmpl_id.id)
            if tmpl_id.increment_uom_thickness == 'percent':
                res[quant_id.id]=tmpl_id.thickness + (tmpl_id.thickness*tmpl_id.increment_thickness/100)
            else:
                res[quant_id.id]=tmpl_id.thickness + tmpl_id.increment_thickness
        return res

    def _get_width(self, cr, uid, ids, name, arg, context=None):
        res = {}
        product_obj = self.pool.get('product.product')
        tmpl_obj = self.pool.get('product.template')
        for quant_id in self.browse(cr, uid, ids):
            product_id = product_obj.browse(cr,uid,quant_id.product_id.id)
            tmpl_id = tmpl_obj.browse(cr,uid,product_id.product_tmpl_id.id)
            tmp_width= self._get_size(cr, product_id.id,"Larghezza")
            if tmpl_id.increment_uom_width == 'percent':
                res[quant_id.id]=tmp_width + (tmp_width*tmpl_id.increment_width/100)
            else:
                res[quant_id.id]=tmp_width + tmpl_id.increment_width
        return res

    def _get_length(self, cr, uid, ids, name, arg, context=None):
        res = {}
        product_obj = self.pool.get('product.product')
        tmpl_obj = self.pool.get('product.template')
        for quant_id in self.browse(cr, uid, ids):
            product_id = product_obj.browse(cr,uid,quant_id.product_id.id)
            tmpl_id = tmpl_obj.browse(cr,uid,product_id.product_tmpl_id.id)
            tmp_length= self._get_size(cr, product_id.id,"Lunghezza")
            if tmpl_id.increment_uom_length == 'percent':
                res[quant_id.id]=tmp_length + (tmp_length*tmpl_id.increment_length/100)
            else:
                res[quant_id.id]=tmp_length + tmpl_id.increment_length
        return res

    def _get_uos_qty(self, cr, uid, ids, name, arg, context=None):
        res = {}
        product_obj = self.pool.get('product.product')
        tmpl_obj = self.pool.get('product.template')
        for quant_id in self.browse(cr, uid, ids):
            product_id = product_obj.browse(cr,uid,quant_id.product_id.id)
            if product_id.uos_id:
                    res[quant_id.id]=quant_id.qty * product_id.uos_coeff_deincr
        return res
    
    def _get_opening(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for quant_id in self.browse(cr, uid, ids):
            package_id = quant_id.package_id
            if package_id:
                res[quant_id.id]=package_id.is_open
            else:
                res[quant_id.id]=False
        return res    

    _columns = {
        'essence': fields.related('product_id',
                                  'essence',
                                  type='many2one',
                                  relation='res.essence',
                                  string='Essence',
                                  readonly=True,
                                  store=True),
        'seasoning': fields.related('product_id',
                                    'seasoning',
                                    type='many2one',
                                    relation='res.seasoning',
                                    string='Seasoning',
                                    readonly=True,
                                    store=True),
        'wood_type': fields.related('product_id',
                                    'wood_type',
                                    type='many2one',
                                    relation='res.wood.type',
                                    string='Wood Type',
                                    readonly=True,
                                    store=True),
        'wood_quality': fields.related('product_id',
                                       'wood_quality',
                                       type='many2one',
                                       relation='res.wood.quality',
                                       string='Wood Quality',
                                       readonly=True,
                                       store=True),
        'thickness': fields.related('product_id',
                                    'thickness',
                                    type='float',
                                    string='Thickness',
                                    readonly=True),
        'incremented_thickness': fields.function(_get_thickness,
                                                 type='float',
                                                 store=True,
                                                 string="Thickness"),
        'incremented_length': fields.function(_get_length,
                                                 type='float',
                                                 store=True,
                                                 string="Length"),
        'incremented_width': fields.function(_get_width,
                                                 type='float',
                                                 store=True,
                                                 string="Width"),
        'package_id': fields.many2one('stock.quant.package', 
                                      string='Package', 
                                      help="The package containing this quant", 
                                      select=True),
        'uom_id': fields.related('product_id',
                                 'uom_id',
                                 type='many2one',
                                 relation='product.uom',
                                 string='UoM',
                                 readonly=True,
                                 store=True),
        'uos_id': fields.related('product_id',
                                 'uos_id',
                                 type='many2one',
                                 relation='product.uom',
                                 string='UoS',
                                 readonly=True,
                                 store=True),
        'uos_qty': fields.function(_get_uos_qty,
                                   type='float',
                                   store=True,
                                   digits_compute= dp.get_precision('Product UoS'),
                                   string="Quantità (UoS)"),
        'is_open_pckg': fields.function(_get_opening,
                                   type='boolean',
                                   store=False,
                                   string="Aperto"),                                   
    }
