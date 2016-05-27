from openerp.osv import fields,osv

class res_company(osv.Model):
    _inherit = 'res.company'
    _columns = {
                "barcode_at_product_create":fields.boolean('Allow to generate barcode at product creation time'),
                }
    
     
    
