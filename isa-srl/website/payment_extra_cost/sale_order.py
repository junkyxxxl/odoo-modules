# -*- coding: utf-8 -*-
from openerp import models, api, fields


class sale_order(models.Model):

    _inherit = ['sale.order']

    website_order_line = fields.One2many(
            'sale.order.line',
            'order_id',
            string='Order Lines displayed on Website',
            readonly=True,
            domain=[('is_delivery', '=', False), ('is_payment', '=', False)],
            help='Order Lines to be displayed on the website. They should not be used for computation purpose.',
    )

    @api.cr_uid_ids_context
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = super(sale_order, self)._amount_all(cr, uid, ids, field_name, arg, context=context)
        currency_pool = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            line_amount = sum([line.price_subtotal for line in order.order_line if line.is_payment])
            currency = order.pricelist_id.currency_id
            res[order.id]['amount_delivery'] += currency_pool.round(cr, uid, currency, line_amount)
        return res

    @api.model
    def _check_acquairer_payment_quotation(self, order, acquirer_payment=None):
        if not order:
            return False
        if acquirer_payment:
            acquire_obj = self.env['payment.acquirer'].browse(acquirer_payment)
            acquire_id = acquire_obj.payment_term_id.id or None
            order_vals = {
                'payment_acquirer_id': acquirer_payment,
                'payment_term': acquire_id
            }
            order.write(order_vals)
            # Se collegato un prodotto al metodo di pagamento, creo la riga
            # sull'ordine.
            order.payment_set()
        else:
            order.payment_unset()
        return bool(acquirer_payment)

    def payment_set(self):
        self.payment_unset()
        # Creo la riga se presente il prodotto collegato
        # al termine di pagamento
        payment_acquirer = self.payment_acquirer_id
        if not payment_acquirer.product_id:
            return None
        acc_fp_obj = self.env['account.fiscal.position']
        taxes = payment_acquirer.product_id.taxes_id
        taxes_ids = [tax.id for tax in acc_fp_obj.map_tax(taxes)]
        line_id = self.env['sale.order.line'].create({
            'order_id': self.id,
            'name': payment_acquirer.product_id.name,
            'product_uom_qty': 1,
            'product_uom': 1,
            'product_id': payment_acquirer.product_id.id,
            'price_unit': payment_acquirer.product_id.lst_price,
            'tax_id': [(6, 0, taxes_ids)],
            'is_payment': True
        })
        return line_id

    def payment_unset(self):
        # Cancello l'eventuale righe di pagamento già associate (se presenti)
        order_line = self.order_line.filtered(lambda l: l.is_payment)
        # La riga di pagamento deve essere solo e soltanto sempre una
        if order_line:
            order_line.ensure_one()
            order_line.unlink()
        return None
