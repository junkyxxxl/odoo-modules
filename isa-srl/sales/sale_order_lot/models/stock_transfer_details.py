# -*- coding: utf-8 -*-
from openerp import models, api
from copy import copy


class stock_transfer_details(models.TransientModel):

    _inherit = ['stock.transfer_details']

    @api.model
    def default_get(self, fields):
        '''
        Funzione che verifica se presente il restricted_lot_id e crea le righe di prodotto
        per prodotto/lotto in base a quelle presente sul picking
        '''
        res = super(stock_transfer_details, self).default_get(fields)
        picking_ids = self._context.get('active_ids', [])
        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        picking_id, = picking_ids
        picking = self.env['stock.picking'].browse(picking_id)
        '''Verifico se presente il lotto in almeno una linea, altrimenti non applico la funzione'''
        exist_lot = picking.move_lines.filtered(lambda m: m.restrict_lot_id)
        if not exist_lot:
            return res
        # Aggiorno i movimenti specificando il lotto
        item_ids = res.get('item_ids', [])
        new_item = []
        for i, move_line in enumerate(picking.move_lines):
            item = {}
            product_id = move_line.product_id.id
            '''Ricerco la riga del prodotto negli item'''
            item = (item for item in item_ids if item["product_id"] == product_id).next()
            item = copy(item)
            item.update({'lot_id': move_line.restrict_lot_id.id})
            item.update({'quantity': move_line.product_qty})
            if i != 1:
                item.update({'packop_id': None})
            new_item.append(item)
        res['item_ids'] = new_item
        return res
