# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError


class managing_lots_items_info(models.Model):
    
    _inherit = ['stock.production.lot']
      
      
    '''Ridefinisco l'overriding del metodo: visualizzerà i record filtrati, per life_date e name oppure solo per nome se non è presente life_date   
    @api.multi
    @api.depends('life_date')
    def name_get(self):
        res = []
        for record in self:
            if record.life_date:
                descr = ("[%s] %s") % (record.life_date, record.name)
            else:
                descr = ("%s") % (record.name)
            res.append((record.id, descr))
        return res      
    '''
  
    #Ridefinisco l'overriding del metodo: filtra solo i lotti che ricerco per nome e che non siano scaduti
    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        if not args:
            args = []
        args = args[:]
        
        #Il filtro del lotto viene eseguito solamente se il campo ""group_lot_life_date" viene settato a True
        #In questo modo reperisco l'oggetto relativo a stock.config.settings
        stock_config_settings_obj = self.env['stock.config.settings'].search([],limit=1, order="id DESC")
        if stock_config_settings_obj:  
           #se è presente, vado a prendere la prima riga
           lot_life_date = stock_config_settings_obj.group_lot_life_date
           if lot_life_date:    
               #Prendo la data odierna
               dateToday = fields.Datetime.now()
               #Filtro solo i lotti che vengono cercati per nome e allo stesso tempo non devono essere scaduti
               records = self.search([('name', operator, name),'|',('life_date', '>', dateToday),('life_date', 'in', (None,False))] + args,
                                     limit=limit)
    
               return records.name_get() 
           else:
               #Altrimenti richiamo la name_search di base
               return super(managing_lots_items_info, self).name_search(name, args = args, operator = 'ilike')
        else:
            return super(managing_lots_items_info, self).name_search(name, args = args, operator = 'ilike')
    
    
class managing_lots_items_configuration(models.Model):
    
    _inherit = ['stock.config.settings']
    
    @api.model
    def _get_lot_life_date(self):
        stock_config_obj = self.env['stock.config.settings'].search([],limit=1, order="id DESC")
        lot_life_date_value = stock_config_obj.group_lot_life_date
        return lot_life_date_value
    
    group_lot_life_date = fields.Boolean(string="Non visualizzare lotti scaduti", default=_get_lot_life_date ,help='Questa funzione permette di selezionare solo i lotti che hanno data di fine vita valida ', required=False)    
    
    
        