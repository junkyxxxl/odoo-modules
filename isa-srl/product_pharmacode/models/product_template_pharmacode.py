# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class product_template_pharmacode_info(models.Model):
    _inherit = ['product.template']
    
    #Questo campo serve ad indicare che un prodotto ha più varianti, e per fare riferimento al singolo prodotto utilizzo product_tmpl_id
    product_variant_ids = fields.One2many('product.product', 'product_tmpl_id')
    #Inserisco il campo related pharmacode(nella tabella product.template non viene inserito) che fa riferimento a
    #quello situato in product.product 
    pharmacode = fields.Char(string='Pharmacode', related='product_variant_ids.pharmacode')
     
     
    #Ridefinisco il metodo set_pharma_code su prodotti in modo che se modifico il pharmacode, deve cambiare anche il relativo ean
    @api.onchange('pharmacode')
    def _set_pharma_code(self):
        if not self.pharmacode:
            return 
        
        product_product = self.env['product.product']
        is_valid = product_product._check_digit_pharmacode(self.pharmacode)
        if not is_valid:
            self.ean13 = None
            return {
                'warning': {
                    'title': "Pharmacode errato",
                    'message': "Il codice pharmacode non è valido.",
                },
            }
        ean = product_product._decode_pharmacode(self.pharmacode)
        self.ean13 = ean
      
           