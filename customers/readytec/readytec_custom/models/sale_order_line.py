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


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def _discounts_preview(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        t_pricelist_id = context.get('pricelist_id', None)

        for line in self.browse(cr, uid, ids, context):
            t_list = []
            if t_pricelist_id:
                price_obj = self.pool.get('product.pricelist')
                price_data = price_obj.browse(cr, uid, t_pricelist_id, context)
                if (price_data and price_data.version_id):
                    for version in price_data.version_id:
                        for item in version.items_id:
                            if item.price_discount and not item.product_id and not item.categ_id:
                                t_list.append("%d" % (item.price_discount*100))
            res[line.id] = str(t_list).strip('[]')
        return res

    def _default_discounts_preview(self, cr, uid, context=None):
        res = ''
        t_pricelist_id = context.get('pricelist_id', None)
        if t_pricelist_id:
            price_obj = self.pool.get('product.pricelist')
            price_data = price_obj.browse(cr, uid, t_pricelist_id, context)
            t_list = []
            if (price_data and price_data.version_id):
                for version in price_data.version_id:
                    for item in version.items_id:
                        if item.price_discount and not item.product_id and not item.categ_id:
                            t_list.append("%d" % (item.price_discount*100))
            res = str(t_list).strip('[]')
        return res

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):

        res = super(sale_order_line, self).product_id_change(cr,
                                           uid, ids, pricelist, product, qty,
                                           uom, qty_uos, uos, name,
                                           partner_id, lang, update_tax,
                                           date_order, packaging,
                                           fiscal_position, flag, context)

        if context is None:
            context = {}

        qty_available     = 0.0
        virtual_available = 0.0
        incoming_qty      = 0.0
        outgoing_qty      = 0.0

        if 'value' in res and res['value']:
            if product:
                product_obj = self.pool.get('product.product')
                product_data = product_obj.browse(cr, uid, product)
                qty_available     = product_data.qty_available
                virtual_available = product_data.virtual_available
                incoming_qty      = product_data.incoming_qty
                outgoing_qty      = product_data.outgoing_qty
            res['value'].update({
                                 'related_qty_available': qty_available,
                                 'related_virtual_available': virtual_available,
                                 'related_incoming_qty': incoming_qty,
                                 'related_outgoing_qty': outgoing_qty,
                                 })
        return res

    _columns = {
        'related_qty_available': fields.related('product_id',
                                     'qty_available',
                                     type="float",
                                     relation="product.product",
                                     string='Quantità in possesso',
                                     store=False),
        'related_virtual_available': fields.related('product_id',
                                     'virtual_available',
                                     type="float",
                                     relation="product.product",
                                     string='Quantità prevista',
                                     store=False),
        'related_incoming_qty': fields.related('product_id',
                                     'incoming_qty',
                                     type="float",
                                     relation="product.product",
                                     string='In entrata',
                                     store=False),
        'related_outgoing_qty': fields.related('product_id',
                                     'outgoing_qty',
                                     type="float",
                                     relation="product.product",
                                     string='In uscita',
                                     store=False),
        'related_discount_preview': fields.function(_discounts_preview,
                                     string='Anteprima Sconti',
                                     type='char',
                                     store=False),
    }

    _defaults = {
        'related_discount_preview': _default_discounts_preview,
    }
