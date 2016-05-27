# -*- coding: utf-8 -*-
from openerp import models, fields, api


class sale_order_invoiced(models.Model):
    _inherit = 'sale.order'

    invoiced_untaxed_sale = fields.Float(string="Totale imponibile fatturato", compute="_calculate_invoiced_untaxed_sale")
    to_invoice_untaxed_sale = fields.Float(string="Totale imponibile da fatturare", compute="_calculate_to_invoice_untaxed_sale")

    @api.one
    def _calculate_invoiced_untaxed_sale(self):
        # inizializzo la variabile del totale fatturato senza tasse (iva)
        total_untaxed_invoiced = 0
        # Accedo alle fatture collegate all'ordine di vendita per reperire le fatture che sono state già state fatturate
        # (mi serve poi per identificare eventuali linee di acconto, che hanno la fattura ma non hanno il collegamento
        # con le linee dell'ordine)
        order_line_invoiced = self.order_line.filtered(lambda l: l.invoiced==True).mapped('invoice_lines').mapped('id')
        invoice_line_in_percentage = self.invoice_ids.mapped('invoice_line').filtered(lambda il: il.id not in order_line_invoiced )
        # Conteggio anche le fatture in percentuale
        for invoice_line in invoice_line_in_percentage:
            total_untaxed_invoiced += invoice_line.price_subtotal
        # Accedo alle linee fatture collegate alle linee dell'ordine di vendita per calcolare il totale fatturato
        if not self.order_line:
            return None
        for order_line in self.order_line:
            if not order_line.invoice_lines:
                continue
            for line in order_line.invoice_lines:
                    total_untaxed_invoiced += line.price_subtotal
        self.invoiced_untaxed_sale = total_untaxed_invoiced

    @api.one
    def _calculate_to_invoice_untaxed_sale(self):
        to_invoice = self.amount_untaxed - self.invoiced_untaxed_sale
        to_invoice = round(to_invoice,5)
        self.to_invoice_untaxed_sale = to_invoice
