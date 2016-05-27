# -*- coding: utf-8 -*-
from openerp import models, fields, api


class invoice_dhl_info(models.Model):
    
    _inherit = 'account.invoice'
    
    @api.model
    def _get_product_code_dhl(self):
    
      #Devo prendere inizialmente la res_company di cui fa parte l'utente loggato e lo faccio tramite: self.env.user.company_id
      company_obj = self.env.user.company_id
      #Una volta che ho l'oggetto di res.company, vado a prendermi il campo product_code_dhl (che è un oggetto product_product: product.product(41616,))
      product_product_obj = company_obj.product_code_dhl
      return product_product_obj
  
  
    @api.model
    def _get_shipping_type(self):
    
      #Devo prendere inizialmente la res_company di cui fa parte l'utente loggato e lo faccio tramite: self.env.user.company_id
      company_obj = self.env.user.company_id
      #Una volta che ho l'oggetto di res.company, vado a prendermi il campo shipping_type 
      shipping_type_obj = company_obj.shipping_type
      return shipping_type_obj
  
    
    product_code_dhl = fields.Many2one('product.product', 'Codice prodotto dhl', default=_get_product_code_dhl)
    shipping_type = fields.Selection([('D', 'D - Nazionale'),('G', 'G - Extra UE'),('UE', 'UE - Unione Europea')], string="Tipo spedizione", size=30, default=_get_shipping_type)
