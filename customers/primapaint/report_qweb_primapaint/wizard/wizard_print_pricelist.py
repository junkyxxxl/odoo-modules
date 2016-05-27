# -*- coding: utf-8 -*-
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

from openerp.osv import fields, osv


class wizard_print_pricelist(osv.osv_memory):
    _name = 'wizard.print.pricelist'
    _description = 'Print Pricelist'

    _columns = {
        'pricelist': fields.many2one('product.pricelist', 'PriceList', required=True),
        'family': fields.many2one('product.family', 'Family', domain=[('type','=','family')]),
        'subfamily': fields.many2one('product.family', 'Subfamily', domain=[('type','=','subfamily')]),
        'show_onhand': fields.boolean('Show Onhand'),
        'stock_location_ids': fields.many2many('stock.location', string='Stock Locations', domain=[('usage','=','internal')]),
    }
    
    _defaults = {
        'show_onhand': False,
    }

    def _check_locations_number(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            if len(wizard.stock_location_ids.ids) > 2:
                return False
        return True

    _constraints = [
        (_check_locations_number, "It's not possible to select more than 2 locations", ['stock_location_ids']),
    ]

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}
        datas = {}
        res = self.read(cr, uid, ids, ['pricelist','family', 'subfamily','show_onhand','stock_location_ids'], context=context)
        res = res and res[0] or {}
        res['pricelist'] = res['pricelist'][0]
        datas['form'] = res
        return self.pool['report'].get_action(cr, uid, [], 'report_qweb_primapaint.report_pricelist', data=datas, context=context)
