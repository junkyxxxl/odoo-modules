# -*- coding: utf-8 -*-
from openerp import models, fields, api

class partner_attributes_info(models.Model):
    
    _inherit = ['res.partner']  

    partner_zone = fields.Many2one('res.zone', string="Zona cliente", required=False)
    partner_category = fields.Many2one('category.partner', string="Categoria cliente", required=False)
    


   
    

     
    

           
      
    
    
    
    
    