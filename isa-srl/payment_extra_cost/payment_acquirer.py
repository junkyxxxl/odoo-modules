# -*- coding: utf-8 -*-
from openerp import models, fields


class payment_acquirer(models.Model):

    _inherit = ['payment.acquirer']

    product_id = fields.Many2one(
        'product.product',
        string="Prodotto",
        help="Per imputare un costo aggiuntivo al metodo di pagamento selezionato (Verrà considerato il prezzo del prodotto).",
        context="{'default_type':'service'}"
    )
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string="Termini pagamento collegati",
        help="Per imputare automaticamente i termini di pagamento nel caso di ordini da web con modalità pagamento selezionata."
    )
