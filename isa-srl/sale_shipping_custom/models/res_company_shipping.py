# -*- coding: utf-8 -*-
from openerp import models, fields, api


class res_company_value_shipping(models.Model):
    _inherit = 'res.company'
    
    transportation_reason_id_custom = fields.Many2one('stock.picking.transportation_reason',string="Causale")
    goods_description_id_custom = fields.Many2one('stock.picking.goods_description',string="Aspetto dei beni")
    carriage_condition_id_custom = fields.Many2one('stock.picking.carriage_condition',string="Resa merce")
    transportation_method_id_custom = fields.Many2one('stock.picking.transportation_method',string="Trasporto a mezzo")
    