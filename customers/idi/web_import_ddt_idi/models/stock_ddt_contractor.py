# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning

class stock_ddt_contractor(models.Model):
    _inherit = 'stock.ddt'
         
    @api.one
    @api.depends('name')
    def _get_contractor(self):
        if not self.picking_ids:
            return None
        #Da stock.ddt vado a prendere la prima riga presente in ddt_lines (campo di stock.ddt) e da qui prendo il picking_type
        picking_type = self.picking_ids[0].picking_type_id
        #Dal picking_type vado a prendermi il magazzino
        if not picking_type: return None
        warehouse_obj = picking_type.warehouse_id
        #Dal magazzino risalgo al contractor
        if not warehouse_obj: return None
        contractor_obj = warehouse_obj.partner_id
        #Con self.contractor instanzio il mio campo calcolato contractor
        if not contractor_obj: return None
        self.contractor = contractor_obj.id
  
    contractor = fields.Many2one('res.partner', required=False, compute="_get_contractor", store=True)
    
    