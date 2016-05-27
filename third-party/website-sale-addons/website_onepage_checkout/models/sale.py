# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp import api, fields, models
from openerp.addons import decimal_precision


class SaleOrder(models.Model):
    """Overwrites and add Definitions to module: sale."""

    _inherit = 'sale.order'

    amount_subtotal = fields.Float(
        compute='_compute_amount_subtotal',
        digits=decimal_precision.get_precision('Account'),
        string='Subtotal Amount',
        store=True,
        help="The amount without anything.",
        track_visibility='always'
    )

    @api.depends('order_line', 'order_line.price_subtotal')
    def _compute_amount_subtotal(self):
        """compute Function for amount_subtotal."""
        for rec in self:
            line_amount = sum([line.price_subtotal for line in
                               rec.order_line if not line.is_delivery])
            currency = rec.pricelist_id.currency_id
            rec.amount_subtotal = currency.round(line_amount)

    @api.model
    def tax_overview(self, order):
        """
        Calculate additional tax information for displaying them in
        onestepcheckout page.
        """
        taxes = {}
        for line in order.order_line:
            for tax in line.tax_id:
                if str(tax.id) in taxes:
                    taxes[str(tax.id)]['value'] += self._amount_line_tax(line)
                else:
                    taxes[str(tax.id)] = {'label': tax.name,
                                          'value': self._amount_line_tax(line)}

        # round and formatting valid taxes
        res = []
        currency = order.pricelist_id.currency_id
        for key in taxes:
            if taxes[key]['value'] > 0:
                taxes[key]['value'] = '%.2f' % currency.round(taxes[key][
                    'value'])
                res.append(taxes[key])

        return res

