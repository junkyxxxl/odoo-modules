# -*- coding: utf-8 -*-
# © <2016> <Antonio Malatesta>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class StockPickingTransferModel(models.TransientModel):

    _name = 'stock.picking.transfer.all'
    _description = 'Transfer all selected picking'

    force_quantity = fields.Boolean(
        string='Force quantity',
        help='Enable forcing assignment and transfer if quantity is not available.'
    )

    @api.multi
    @api.model
    def transfer_all(self):
        for record in self:
            selected_pickings = self.env.context.get('active_ids', False)
            transfer_pick = []
            for picking in self.env['stock.picking'].browse(selected_pickings):
                state = picking.state
                # state to not considered
                if state in ('draft', 'cancel', 'done'):
                    continue
                # different operations based state
                if state in ('waiting', 'partially_available') and record.force_quantity:
                    self._go_rereserve_pick(picking)
                elif state in ('confirmed') and record.force_quantity:
                    self._go_action_assign(picking)
                elif state in ('assigned'):
                    self._go_do_enter_transfer_details(picking)
                else:
                    continue
                transfer_pick.append(picking.id)
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "name": "Picking trasferiti con successo",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", transfer_pick]],
        }

    # available for waiting and partially_available
    def _go_rereserve_pick(self, picking):
        picking.rereserve_pick()
        # recheck state
        if picking.state != 'assigned':
            return self._go_action_assign(picking)
        self._go_do_enter_transfer_details(picking)

    @api.model
    def _go_do_enter_transfer_details(self, picking):
        # context = {} for prevent frozen dict error.
        res = picking.with_context({}).do_enter_transfer_details()
        transfer_id = res.get('res_id', False)
        transfer_detail = self.env['stock.transfer_details'].browse(transfer_id)
        transfer_detail.do_detailed_transfer()

    def _go_force_assign(self, picking):
        picking.force_assign()
        return self._go_do_enter_transfer_details(picking)

    # available for confirmed
    def _go_action_assign(self, picking):
        picking.action_assign()
        if picking.state != 'assigned':
            return self._go_force_assign(picking)
        self._go_do_enter_transfer_details(picking)
