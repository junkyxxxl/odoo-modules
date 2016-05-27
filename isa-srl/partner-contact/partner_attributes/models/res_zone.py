# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError

class res_zone(models.Model):
    
    _name = 'res.zone'
    
    code = fields.Char(string="Codice zona", required=False)
    description = fields.Char(string="Descrizione zona", required=True)
    
    
    '''Se esiste il codice, effettuo un controllo dell'univocità del codice e descrizione'''
    @api.one
    @api.constrains('code','description')
    def check_unique_code_by_description(self):
        if self.code:
            record_filter = self.env['res.zone'].search_count([('code','=',self.code),('description','=',self.description)])
            #Ora effettuo il controllo sull'univocità: se il risultato è maggiore di 1, allora sollevo il messaggio di warning
            if record_filter > 1:
                raise ValidationError("La zona con codice: " +self.code+ " e descrizione: " +self.description+  " risulta esistente!")
                  
    
    #Ridefinisco la funzione name_get  
    @api.multi
    @api.depends('code', 'description')
    def name_get(self):
        res = []
        for record in self:
            if record.code:
                descr = ("[%s] %s") % (record.code, record.description)
            else:
                descr = ("%s") % (record.description)
            res.append((record.id, descr))
        return res    
        
        
    #Ridefinisco la funzione base per la search relativa alle zone: ricerco per codice e descrizione
    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        if not args:
            args = []
        args = args[:]
        records = self.search(['|',('code', operator, name),('description', operator, name)] + args,
                              limit=limit)
        return records.name_get()
    
    
    
    
    