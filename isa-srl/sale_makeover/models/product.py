# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2010-2012 Camptocamp SA
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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

from openerp.addons import decimal_precision as dp
from openerp.tools.float_utils import float_round
from openerp.osv import fields, osv

class product_product_makeover(osv.osv):
    _inherit = "product.product"

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        context = context or {}
        field_names = field_names or []

        res = super(product_product_makeover,self)._product_available(cr, uid, ids, field_names=field_names, arg=arg, context=context)
        if res:
            domain_products = [('product_id', 'in', ids)]
            domain_quant = []
            domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations(cr, uid, ids, context=context)
            domain_quant += domain_products
    
            if context.get('lot_id'):
                domain_quant.append(('lot_id', '=', context['lot_id']))
            if context.get('owner_id'):
                domain_quant.append(('owner_id', '=', context['owner_id']))
            if context.get('package_id'):
                domain_quant.append(('package_id', '=', context['package_id']))
    
            domain_quant += domain_quant_loc
            quants = self.pool.get('stock.quant').read_group(cr, uid, domain_quant, ['product_id', 'qty'], ['product_id'], context=context)
            quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))
    
            for product in self.browse(cr, uid, ids, context=context):
                id = product.id
                virtual_available = float_round(quants.get(id, 0.0), precision_rounding=product.uom_id.rounding)
                res[id].update({'virtual_available': virtual_available,})
        return res

    _columns = {

        'virtual_available': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Quantity Available',
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, "
                 "or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "typed as 'internal'."),

    }
