# -*- coding: utf-8 -*-
from openerp import models, fields, api


class res_partner_value_shipping(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def _get_goods_description_id(self):
        stock_picking_goods_descriptions_id = self.env['stock.picking.goods_description'].search([('name','=','CARTONE')])
        if stock_picking_goods_descriptions_id:
            return stock_picking_goods_descriptions_id[0]
        return 
    
    @api.model
    def _get_carriage_condition_id(self):
        stock_picking_carriage_condition_id = self.env['stock.picking.carriage_condition'].search([('name','=','PORTO FRANCO')])
        if stock_picking_carriage_condition_id:
            return stock_picking_carriage_condition_id[0]
        return  
    
    @api.model
    def _get_transportation_reason_id(self):
        stock_picking_transportation_reason_id = self.env['stock.picking.transportation_reason'].search([('name','=','VENDITA')])
        if stock_picking_transportation_reason_id:
            return stock_picking_transportation_reason_id[0]
        return    
    
    @api.model
    def _get_transportation_method_id(self):
        stock_picking_transportation_method_id = self.env['stock.picking.transportation_method'].search([('name','=','CORRIERE')])
        if stock_picking_transportation_method_id:
            return stock_picking_transportation_method_id[0]
        return         
    
    goods_description_id = fields.Many2one(
     'stock.picking.goods_description', 'Description of Goods',
     default=_get_goods_description_id)  
    
    carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', 'Carriage Condition', 
     default=_get_carriage_condition_id)
    
    transportation_reason_id = fields.Many2one(
     'stock.picking.transportation_reason',
     'Reason for Transportation',
     default=_get_transportation_reason_id)    
    
    transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        'Method of Transportation',
     default=_get_transportation_method_id)     
    
              