# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class product_family_info(models.Model):
    
    _name="product.family"
        
    code = fields.Char(string="Codice",required=False)
    name = fields.Char(string="Nome",required=True)
    type = fields.Selection([('family', 'Famiglia'),
                             ('subfamily','Sottofamiglia'),
                             ('subgroup','Sottogruppo'),
                             ('classifier1','Classificatore 1'),
                             ('classifier2','Classificatore 2'),
                             ('classifier3','Classificatore 3')
                            ],required=True)
    
    
    '''Per garantire l'univocità del codice in base al tipo'''
    @api.one
    @api.constrains('code','type')
    def check_unique_code_by_type(self):
        if self.code:
            record_filter = self.env['product.family'].search([('code','=',self.code),('type','=',self.type)])
            record_filter.ensure_one()
        
        
    '''Ridefinisco la funzione name_get'''    
    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        res = []
        for record in self:
            if record.code:
                descr = ("[%s] %s") % (record.code, record.name)
            else:
                descr = ("%s") % (record.name)
            res.append((record.id, descr))
        return res    
        
        
    '''Ridefinisco la funzione base per la search relativa alla classificazione dei prodotti'''
    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        if not args:
            args = []
        args = args[:]
        records = self.search(['|',('name', operator, name),('code', operator, name)] + args,
                              limit=limit)
        return records.name_get()
        
        
            
            