# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class stock_move(osv.osv):
    
    _inherit = 'stock.move'


    def onchange_date(self, cr, uid, ids, date, date_expected, context=None):
        res = {}
        res = super(stock_move,self).onchange_date(cr,uid,ids,date,date_expected,context)

        stock_picking_date = context.get('date_picking', False)
        if stock_picking_date:
            return {'value': {'date_expected': stock_picking_date, 'date': stock_picking_date}}
        else:
            return res