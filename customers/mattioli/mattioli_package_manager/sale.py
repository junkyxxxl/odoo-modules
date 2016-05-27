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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class sale_order_line_mattioli(osv.Model):
    _inherit = "sale.order.line"
    _columns = {
        'package_id': fields.many2one('stock.quant.package', 'Source pack'),
    }

    def onchange_package_id(self, cr, uid, ids, product_id, package_id, qty, context=None):
        context = context or {}
        if not package_id or not product_id:
            return {}
        sum = 0

        cr.execute('SELECT qty FROM stock_quant WHERE package_id = %s AND product_id = %s', (package_id,product_id))
        res = cr.fetchall()
        for i in range(0, len(res)):
            sum += res[i][0]
        if sum < qty:
            warning = {'title': _('Warning!'),
                       'message': _('La quantita\' desiderata non e\' disponibile nel pacco selezionato.\nLa massima quantita\' disponibile sara\' impostata automaticamente.')
                       }
            return {'warning': warning, 'value': {'product_uom_qty': sum}}
        return {}

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False,
                          fiscal_position=False, flag=False, price_unit=False,
                          context=None):

        ret = super(sale_order_line_mattioli, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context=context)
        if flag:
            if context.get('package'):
                package_id = context.get('package')
                if not package_id:
                    return ret
                sum = 0
                res = []
                cr.execute('SELECT qty FROM stock_quant WHERE package_id = %s AND product_id=%s', (package_id,product))
                res = cr.fetchall()
                for i in range(0, len(res)):
                    sum += res[i][0]
                if sum < qty:
                    warning = {'title': _('Warning!'),
                               'message': _('La quantita\' desiderata non e\' disponibile nel pacco selezionato.\nLa massima quantita\' disponibile sara\' impostata automaticamente.')
                               }
                    ret.update({'warning': warning})
                    ret['value'].update({'product_uom_qty': sum})
        return ret

    '''
    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):

        ret = super(sale_order_line_mattioli,self).product_id_change_with_wh(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, warehouse_id, context=context)
        if flag:
            if context.get('package'):        
                package_id = context.get('package')
                if not package_id:
                    return ret
                sum = 0;
                res = []
                cr.execute('SELECT qty FROM stock_quant WHERE package_id = %s AND product_id=%s', (package_id,product))
                res = cr.fetchall()
                for i in range(0,len(res)):
                    sum+=res[i][0]
                if sum<qty:
                    warning =   {
                                 'title': _('Warning!'),
                                 'message': _('La quantita\' desiderata non e\' disponibile nel pacco selezionato.\nLa massima quantita\' disponibile sara\' impostata automaticamente.')
                                }
                    ret.update({'warning':warning})
                    ret['value'].update({'product_uom_qty': sum})
        return ret
        '''