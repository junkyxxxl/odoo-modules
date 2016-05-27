# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID

class stock_quant(osv.osv):

    _inherit = 'stock.quant'

    def _quant_create(self, cr, uid, qty, move, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False, force_location_from=False, force_location_to=False, context=None):
        quant = super(stock_quant, self)._quant_create(cr, uid, qty, move, lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id, dest_package_id=dest_package_id, force_location_from=force_location_from, force_location_to=force_location_to, context=context)

        #Prendo gli oggetti di stock.move:
        stock_move_obj = move
        #Ora reperisco la data pianificata inizialmente
        min_date = stock_move_obj.date_expected

        #Ora reperisco gli oggetti delle quants create:
        stock_quant_obj = stock_move_obj.quant_ids

        for quant in stock_quant_obj:
            self.write(cr, SUPERUSER_ID, quant.id, {'in_date': min_date}, context=context)

        return quant