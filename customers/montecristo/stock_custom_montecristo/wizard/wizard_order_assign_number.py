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


from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from math import ceil
import openerp.addons.decimal_precision as dp

class wizard_assign_stock_number(osv.osv_memory):
    _name = "wizard.assign.stock.number"
    _description = "Assign Stock Numbers"

    _columns = {
        'season_id': fields.many2one('res.family', string='Season', domain='[("type","=","production")]'),
        'category_ids': fields.many2many('product.category', string='Excluded Categories'),
    }

    def _get_season(self, cr, uid, context = None):
        seasons = self.pool.get('res.family').search(cr,uid,[('current','=',True)])
        if seasons:
            return seasons[0]
        return 
    
    _defaults = {
        'season_id': _get_season,
    }

    def assign_stock_number(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')

        season_id = self.browse(cr, uid, ids)[0].season_id.id
        category_ids = self.browse(cr, uid, ids)[0].category_ids.ids
        
        #ESTRAGGO TUTTI GLI ORDINI
        sale_order_ids = order_obj.search(cr, uid, [('state','not in',['draft', 'sent', 'cancel','shipping_except','invoice_except','done']),('season','=',season_id),('document_type_id','=',None)])
        if not sale_order_ids:
            return
        sales_per_partner = {}
        
        #RAGGRUPPO GLI ORDINI PER PARTNER
        for id in sale_order_ids:
            order = order_obj.browse(cr,uid,id)
            if order.partner_id.id not in sales_per_partner:
                sales_per_partner[order.partner_id.id] = {'orders':{},'num_packages':0}
            sales_per_partner[order.partner_id.id]['orders'][order.id] = 0
        
        
        #PER OGNI PARTNER, CALCOLO IL NUMERO DI PACCHI PRODOTTI DA CIASCUN SUO ORDINE E SCRIVO QUESTO VALORE SUL DB
        for partner in sales_per_partner.items():
            for order_tuple in partner[1]['orders'].items():
                order_id = order_tuple[0]
                order = order_obj.browse(cr,uid,order_id)
                tot_packages = 0.0
                for line in order.order_line:
                    if line.product_id.categ_id.id not in category_ids:
                        if line.product_id and line.product_id.categ_id and line.product_id.categ_id.qty_per_pack != 0:
                            tot_packages += (1/line.product_id.categ_id.qty_per_pack)*line.product_uom_qty
                partner[1]['orders'][order.id] = ceil(tot_packages)
                #order_obj.write(cr,uid,order.id,{'package_number': partner[1]['orders'][order.id]})
                cr.execute('''
                            UPDATE sale_order
                            SET package_number = %s
                            WHERE id = %s                
                ''',(partner[1]['orders'][order.id],order.id))

        #RIORDINO I RAGGRUPPAMENTI (Partner,Ordini) IN BASE AL NUMERO TOTALE DI PACCHI GENERATI E RINUMERO
        cr.execute('''
                SELECT partner_id, sum(package_number) as pacchi
                FROM sale_order
                WHERE id IN %s
                GROUP BY partner_id
                ORDER BY pacchi desc;            
        ''',(tuple(sale_order_ids),))
        tot_per_partner = cr.fetchall()
        count = 1
        for obj in tot_per_partner:            
            cr.execute('''
                SELECT id
                FROM sale_order
                WHERE partner_id = %s AND
                      id IN %s
            ''',(obj[0],tuple(sale_order_ids)))            
            
            for ord_id in cr.fetchall():                
                cr.execute('''
                    UPDATE sale_order
                    SET stock_number = %s, stock_number_txt = %s
                    WHERE id = %s
                ''',(count, str(count).rjust(4, '0'), ord_id[0]))
                count += 1            
        return 


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    