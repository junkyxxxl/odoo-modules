# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning

class account_payment_term(models.Model):
    _inherit = 'account.payment.term'
    
    payment_code = fields.Char(string="Codice pagamento", required=False)