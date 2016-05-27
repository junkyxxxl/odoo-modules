# -*- coding: utf-8 -*-
from openerp import fields, models


class account_payment_term(models.Model):

    _inherit = ['account.payment.term']

    fees_uncollected = fields.Boolean(
        string='Fees uncollected',
    )
