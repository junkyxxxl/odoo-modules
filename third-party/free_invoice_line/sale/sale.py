# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import openerp.addons.decimal_precision as dp


class sale_order(orm.Model):

    _inherit = "sale.order"

    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = super(sale_order,self)._amount_all(cr, uid, ids, field_name, arg, context=context)
        
        for order in self.browse(cr, uid, ids, context=context):
            
            res[order.id].update({'amount_untaxed_free':0.0, 'amount_tax_free':0.0})
            
            cur = order.pricelist_id.currency_id
            tax_lines = {}            
            for line in order.order_line:
                
                if line.free in ['gift', 'base_gift']:
                    res[order.id]['amount_untaxed_free'] += line.price_subtotal
                    if line.free == 'gift':
                        for tax in line.tax_id:
                            if tax.amount in tax_lines:
                                tax_lines[tax.amount] += line.price_subtotal
                            else:
                                tax_lines[tax.amount] = line.price_subtotal
            for tl in tax_lines:
                res[order.id]['amount_tax_free'] += tax_lines[tl] * tl
            res[order.id]['amount_untaxed'] -= res[order.id]['amount_untaxed_free']
            res[order.id]['amount_tax'] = res[order.id]['amount_tax'] - res[order.id]['amount_tax_free']
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'amount_untaxed_free' : fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='"For Free" Amount', 
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums'),                                    
        'amount_tax_free' : fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='"For Free" Tax', 
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums'),  
    }

class sale_order_line(orm.Model):

    _inherit = "sale.order.line"

    _columns = {
        'free': fields.selection([
            ('gift', 'Gift on Amount Total'),
            ('base_gift', 'Gift on Amount Untaxed')],
            'Free')
    }

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False,
                                         context=None):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        res = {}
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id, context)
        res.update({
            'free': line.free,
        })
        return res

class stock_move(orm.Model):

    _inherit = 'stock.move'

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type,
                               context=None):
        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        if move.procurement_id and move.procurement_id.sale_line_id:
            sale_line = move.procurement_id.sale_line_id
            res['free'] = sale_line.free
        return res
