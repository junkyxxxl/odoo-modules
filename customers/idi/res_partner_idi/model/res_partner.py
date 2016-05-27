'''
Created on 23/set/2015

@author: redondo81
'''

from openerp import api, models, fields

class res_partner(models.Model):
    _inherit = "res.partner"
    
    destination_code = fields.Char(string = 'Codice Destinazione')