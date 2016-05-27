from openerp.osv import osv, fields

class product_template( osv.osv ):
    _inherit = 'product.template'
    _columns = {
                'ean13': fields.related( 'product_variant_ids', 'main_ean13', type='char', string='EAN13 Barcode' ),
    }
