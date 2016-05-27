# -*- coding: utf-8 -*-
##############################################################################
#
#   Ridefinisce soltanto la funzione "do_enter_transfer_details" permettendo
#   una sottomissione in batch della funzione.
#   In pratica, invece di far vedere la vista wizard, se passato un determinato
#   parametro, vengono aggiornati i dati in background (come se fossero stati
#   inviati dal wizard) e viene eseguito il transfer
##############################################################################
from openerp import models, api


class stock_picking_transfer(models.Model):
    _inherit = ['stock.picking']

    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        submit_type = context[
            'submit_type'] if 'submit_type' in context else None
        lots = context['lots'] if 'lots' in context else None
        context = {}
        result = super(stock_picking_transfer, self).do_enter_transfer_details(
            cr, uid, picking, context)
        '''
        Controllo e si tratta di un operazione interattiva
        (impostata di default) oppure si
        tratta di un operazione batch.
        Se si tratta di un operazione batch simulo il submit del
        wizard facendo l'update manuale delle righe
        create dal wizard per settare i lotti
        '''
        if submit_type == "batch":
            stock_transfer_id = result['res_id']
            stock_transfer_details = self.pool.get('stock.transfer_details').browse(
                cr, uid, stock_transfer_id, context)
            # La procedura considera anche packop_ids. In questo specifico caso non deve essere implementato tale
            # metodo, quindi considero solo item_ids
            # Questa procedura non è più necessaria perchè sono stati introdotti i lotti negli ordini di vendita.
            # Viene lasciata comunque.
            if lots:
                items_value = []
                for item in stock_transfer_details.item_ids:
                    item_id = item.id
                    product_id = item.product_id.id
                    lot = filter(
                        lambda lotti: lotti['product_id'] == product_id, lots)
                    # Dovrebbe eserci un solo elemento. Considero il primo
                    lot = lot[0]
                    lot_id = lot['lot_id']
                    # Per ogni riga di item_ids devo aggiornare il lotto
                    items_value.append((1, item_id, {'lot_id': lot_id}))
                # Devo aggiornare la riga di stock_transfer.details con le righe dei prodotti modificati con il
                # numero di serie aggiornato
                self.pool.get('stock.transfer_details').write(
                    cr, uid, stock_transfer_details.id, {'item_ids': items_value})
            return stock_transfer_details.do_detailed_transfer()
        else:
            return result
