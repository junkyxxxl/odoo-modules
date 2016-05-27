# -*- coding: utf-8 -*-
from openerp import models, fields


class stock_picking_type(models.Model):

    _inherit = ['stock.picking.type']

    ddt_default_journal = fields.Many2one('account.journal', string="Sezionale di default DDT")
