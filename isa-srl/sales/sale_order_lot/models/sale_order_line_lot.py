# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning


class sale_order_line_lot(models.Model):

    _inherit = ['sale.order.line']

    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    use_date = fields.Datetime(related='lot_id.use_date', readonly=True)

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if not self.lot_id or not self.product_id:
            return None
        lot = self.env['stock.production.lot'].search([
            ('product_id', '=', self.product_id.id),
            ('id', '=', self.lot_id.id)
        ])[0]
        if lot:
            self.use_date = lot.use_date

    @api.model
    def create(self, vals):
        # Controllo se il prodotto possiede il lotto di produzione specificato
        product_id = vals.get('product_id', False)
        lot_id = vals.get('lot_id', False)
        status, message = self._check_product_lot(product_id, lot_id)
        if not status:
            raise Warning(message)
        return super(sale_order_line_lot, self).create(vals)

    @api.one
    def write(self, vals):
        # Controllo se il prodotto possiede il lotto di produzione specificato
        product_id = vals.get('product_id', self.product_id.id)
        lot_id = vals.get('lot_id', self.lot_id.id)
        status, message = self._check_product_lot(product_id, lot_id)
        if not status:
            raise Warning(message)
        return super(sale_order_line_lot, self).write(vals)

    def _check_product_lot(self, product_id, lot_id):
        message = None
        status = True
        if product_id and lot_id:
            product = self.env['product.product'].browse(product_id)
            lot = self.env['stock.production.lot'].browse(lot_id)
            product_lot = self.env['stock.production.lot'].search([
                ('product_id', '=', product_id),
                ('id', '=', lot_id)
            ])
            if not product_lot.exists():
                message = "Il prodotto %s non possiede il lotto di produzione %s" % (
                    product.name, lot.name
                )
                status = False
        return status, message
