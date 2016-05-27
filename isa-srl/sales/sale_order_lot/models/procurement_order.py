# -*- coding: utf-8 -*-
from openerp import models, api


class stock_picking_lot(models.Model):

    _inherit = ['procurement.order']

    @api.model
    def _run_move_create(self, procurement):
        res = super(stock_picking_lot, self)._run_move_create(procurement)
        if res and procurement.sale_line_id and procurement.sale_line_id.lot_id:
            res.update({'restrict_lot_id': procurement.sale_line_id.lot_id.id})
        return res
