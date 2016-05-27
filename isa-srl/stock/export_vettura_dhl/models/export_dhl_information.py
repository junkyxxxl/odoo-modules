# -*- coding: utf-8 -*-
import math
from openerp import models, fields, api


class export_dhl_info(models.Model):
    
    _inherit = ['res.company']
      
        
    product_code_dhl = fields.Many2one('product.product', string="Codice prodotto dhl", required=False)
    shipping_type = fields.Selection([('D', 'D - Nazionale'),('G', 'G - Extra UE'),('UE', 'UE - Unione Europea')], string="Tipo spedizione", required=False)
    paying_code_dhl = fields.Char(string="Codice pagante", size=30, required=False)
    
        

        