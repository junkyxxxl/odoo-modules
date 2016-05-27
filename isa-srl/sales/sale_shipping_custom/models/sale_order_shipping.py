# -*- coding: utf-8 -*-
from openerp import models, fields, api


class sale_order_value_shipping(models.Model):
    _inherit = 'sale.order'

         
    @api.model
    def _get_transportation_reason_id_custom(self):
        # Prendo l'id relativo alla compagnia selezionata
        company_id = self.env.user.company_id.id
        # Dal modello res.company, seleziono la riga (browse) contenente l'id della compagnia selezionata
        company_obj = self.env['res.company'].browse(company_id)
        # Dalla compagnia vado a prendere la variabile che ho creato io
        default = company_obj.transportation_reason_id_custom
        
        # Adesso effettuo un controllo in cui mi ritorna la variabile se è presente, altrimenti null
        if default:
            return default
        return 
    
    @api.multi
    def _get_goods_description_id_custom(self):
        company_id = self.env.user.company_id.id
        company_obj = self.env['res.company'].browse(company_id)
        default_goods_descriptions = company_obj.goods_description_id_custom
        
        if default_goods_descriptions:
            return default_goods_descriptions
        return  
    
    @api.model
    def _get_carriage_condition_id_custom(self):
        company_id = self.env.user.company_id.id
        company_obj = self.env['res.company'].browse(company_id)
        default_carriage_condition = company_obj.carriage_condition_id_custom
        if default_carriage_condition:
            return default_carriage_condition
        return   
    
    @api.model
    def _get_transportation_method_id_custom(self):
        company_id = self.env.user.company_id.id
        company_obj = self.env['res.company'].browse(company_id)
        default_transportation_method = company_obj.transportation_method_id_custom
        if default_transportation_method:
            return default_transportation_method
        return      
    
    transportation_reason_id = fields.Many2one(
     'stock.picking.transportation_reason',
     'Reason for Transportation',
     default=_get_transportation_reason_id_custom) 
    
    goods_description_id = fields.Many2one(
     'stock.picking.goods_description', 'Description of Goods',
     default=_get_goods_description_id_custom)
    
    carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', 'Carriage Condition', 
     default=_get_carriage_condition_id_custom)  
    
    transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        'Method of Transportation',
     default=_get_transportation_method_id_custom)    
    
        

    
        
        
        
            
    
