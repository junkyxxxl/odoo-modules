# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import re


class account_invoice(models.Model):

    _inherit = ['account.invoice']

    amount_cashing_fees = fields.Float(
        string='Total account cashing fees',
        digits=dp.get_precision('Account'),
        compute='_compute_total_amount_cashing_fees',
        store=True
    )
    total_compute_tax = fields.Float(
        string='Total compute tax',
        digits=dp.get_precision('Account'),
        compute='_compute_total_tax'
    )

    @api.one
    @api.depends('invoice_line')
    def _compute_total_amount_cashing_fees(self):
        self.amount_cashing_fees = 0
        cashing_fees_lines = self.invoice_line.filtered(lambda l: l.product_id.is_cashing_fees)
        for line in cashing_fees_lines:
            self.amount_cashing_fees += line.price_subtotal

    @api.one
    @api.depends('amount_tax', 'amount_tax_free')
    def _compute_total_tax(self):
        self.total_compute_tax = self.amount_tax + self.amount_tax_free

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'account_report.invoice')


class account_invoice_line(models.Model):

    _inherit = ['account.invoice.line']

    def sanitize_description(self):
        return re.sub('[[].+?[]]', '', self.name)
