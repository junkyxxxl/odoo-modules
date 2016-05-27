# -*- coding: utf-8 -*-
from openerp import models, fields


class res_company(models.Model):
    _inherit = ['res.company']

    start_new_partner_code_from = fields.Integer(
        string='Start new account code from',
        default=1,
    )

    start_new_supplier_code_from = fields.Integer(
        string='Start new supplier code from',
        default=1,
    )
