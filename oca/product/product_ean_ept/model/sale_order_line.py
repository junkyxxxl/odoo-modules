# -*- coding: utf-8 -*-
from openerp import models, fields, api

class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    
    ean13_id=fields.Many2one('product.ean13', 'Codice Prodotto')
    
    @api.onchange('ean13_id')
    def _ean13_id_change_with_wh(self):
       self.product_id = self.ean13_id.product_id.id
       self.product_uom_qty = self.ean13_id.quantity