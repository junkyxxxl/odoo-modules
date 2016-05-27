# -*- coding: utf-8 -*-
##############################################################################
#Eliminazione controllo su campo ean13 di product product
##############################################################################
from openerp import api, models, fields,osv
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError, Warning

class product_product(models.Model):
    _inherit = "product.product"

    # disable constraint
    def _check_ean_key(self, cr, uid, ids):
        "Inherit the method to disable the EAN13 check"
        return True
    
    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]

    