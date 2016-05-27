# -*- coding: utf-8 -*-
from openerp import models, fields


class account_account_asset(models.Model):

    _inherit = ['account.asset.asset']

    serial_number = fields.Char(
        string='Serial number',
    )
