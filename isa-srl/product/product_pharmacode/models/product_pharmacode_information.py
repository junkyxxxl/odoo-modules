# -*- coding: utf-8 -*-
import math
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class product_pharmacode_info(models.Model):

    _inherit = ['product.product']

    pharmacode = fields.Char(string="Pharmacode", size=30, required=False)


    #Definisco una funzione che data una cifra, mi ritorna il carattere corrispondente
    def _table_of_conversion(self, cifra):
      caratteri = ["0","1","2","3","4","5","6","7","8","9","B","C","D","F","G","H","J","K","L","M","N","P","Q","R","S","T","U","V","W","X","Y","Z"]
      carattere = caratteri[cifra]
      return carattere


    #Verifica esistenza pharmacode in chiaro
    def _check_digit_pharmacode(self, pharmacode):
        lista = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        somma = 0
        originalPharmacode = pharmacode
        firstChar = pharmacode[0]

        #Viene eseguito il substring del pharmacode fino al penultimo carattere
        checkPharmacode = pharmacode[1:9]

        #Controllo la lunghezza del pharmacode che deve essere lungo 9 + il carattere di controllo e il
        #carattere iniziale deve essere 'A'
        lunghezza_pharmacode = len(originalPharmacode)
        if lunghezza_pharmacode !=10 or firstChar != 'A':
            return False

        #Ora controllo la stringa checkPharmacode, e controllo se ogni singolo carattere è un intero e di
        #conseguenza non deve far parte della lista
        for i in range(8):
            if i%2 == 1:
              if checkPharmacode[i] in lista:
                  return False
              else:
                  carattere = int(checkPharmacode[i]) * 2
                  if len(str(carattere)) > 1:
                      carattere = str(carattere)
                      carattere = int(carattere[0]) + int(carattere[1])
                      somma+= int(carattere)
                  else:
                      somma+= int(carattere)
            else:
              if checkPharmacode[i] in lista:
                  return False
              else:
                  carattere = int(checkPharmacode[i]) * 1
                  somma+= int(carattere)

        check_digit = somma % 10
        pharmacode = str(firstChar) + checkPharmacode + str(check_digit)
        if originalPharmacode == pharmacode:
            return True
        else:
            return False


    #Decodifica del pharmacode in chiaro a codice a barre
    def _decode_pharmacode(self, pharmacode):
        #Viene eseguito il substring del pharmacode
        pharmacode = pharmacode[1:]
        divisore = math.pow(32,5)
        result = int(pharmacode) / int(divisore)
        cifra = str(result).split('.')[0]
        resto = int(pharmacode) % divisore
        carattereCorrispondente = self._table_of_conversion(int(cifra))
        ean = str(carattereCorrispondente)
        i=5

        while i>0:
            i -= 1
            divisore = math.pow(32,i) # 32^i
            result = resto / int(divisore)
            cifra = str(result).split('.')[0]
            resto = resto % divisore
            carattereCorrispondente = self._table_of_conversion(int(cifra))
            ean = ean + str(carattereCorrispondente)

        return ean


    @api.onchange('pharmacode')
    def _set_pharma_code(self):
        #Inizialmente se è vuoto il pharmacode, faccio un return a vuoto (errore: TypeError: 'bool' object has no attribute '__getitem__')
        if not self.pharmacode:
            return

        is_valid = self._check_digit_pharmacode(self.pharmacode)
        if not is_valid:
            self.ean13 = None
            return {
                'warning': {
                    'title': "Pharmacode errato",
                    'message': "Il codice pharmacode non è valido.",
                },
            }
        ean = self._decode_pharmacode(self.pharmacode)
        self.ean13 = ean


    '''Ridefinisco la funzione name_search'''
    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        if not args:
            args = []
        args = args[:]
        records = self.search(['|',('name', operator, name),('pharmacode', operator, name)] + args,
                              limit=limit)
        #Se è presente il pharmacode ricercato, richiamo la mia name_get
        if records:
           return records.name_get()
        else:
           #Altrimenti se non è presente il pharmacode ricercato, richiamo la name_search di base
           return super(product_pharmacode_info,self).name_search(name=name, args=args, operator=operator, limit=limit)
