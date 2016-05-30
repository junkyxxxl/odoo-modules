# -*- coding: utf-8 -*-
# © <2016> <Antonio Malatesta>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockConfigSettings(models.TransientModel):

    _inherit = ['stock.config.settings']

    default_force_quantity = fields.Boolean(
        string='Force quantity',
        default_model='stock.picking.transfer.all'
    )
