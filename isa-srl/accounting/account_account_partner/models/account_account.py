# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError

class account_account_auto_code(models.Model):
    _inherit = ['account.account']
    
    
    
    
    
    @api.onchange('parent_id', 'type')
    def change_account_code(self):
        self.code = self.get_next_account_code(self.parent_id.id, self.type)
    
    
    
    def get_next_account_code(self, parent_id, type, partner_type="customer"):
        if not parent_id or not type:
            return None
        account_account = self.env['account.account'].browse(parent_id)
        parent_code = account_account.code
        if type == 'view':
            return parent_code
        max_code = None
        if parent_code:
            try:
                # Reperisco la lunghezza del codice padre (mi serve per
                # fare poi la substring)
                parent_length = str(len(parent_code)+1)
                # Reperisco il numero dal quale iniziare la ricerca in base al tipo di
                # partner passato
                start_from = 1
                if partner_type == 'customer':
                    start_from = self.env.user.company_id.start_new_partner_code_from
                elif partner_type == 'supplier':
                    start_from = self.env.user.company_id.start_new_supplier_code_from
                else:
                    start_from = self.env.user.company_id.start_new_partner_code_from
                if not start_from or (start_from and start_from == 0):
                    start_from = 1
                #Verifico se esiste il primo
                sql = '''SELECT code 
                         FROM   account_account a
                         WHERE  1=1
                         AND    parent_id = %d 
                         AND    type <> 'view'
                         AND    CAST(SUBSTRING(a.code FROM %s) AS BIGINT) = %d
                      ''' % (account_account.id,parent_length, start_from)
                self.env.cr.execute(sql)
                list = self.env.cr.fetchall()
                
                if False and list:
                    sql = '''SELECT MIN(a.code) 
                             FROM   account_account a 
                             
                             WHERE  1=1 
                             AND    a.parent_id = %(parent_id)d
                             AND    a.type <> 'view'
                             AND    CAST(SUBSTRING(a.code FROM %(length)s) AS BIGINT) > %(start_from)d
                             AND    CAST(SUBSTRING(a.code FROM %(length)s) AS BIGINT) +1  
                             NOT IN (
                                SELECT CAST(SUBSTRING(b.code FROM %(length)s) AS BIGINT)
                                FROM   account_account b 
                                WHERE  1=1 
                                AND    b.parent_id = %(parent_id)d
                                AND    b.type <> 'view'
                             )
                          ''' % {'parent_id': account_account.id, 'length' : parent_length, 'start_from': start_from}
                    self.env.cr.execute(sql)
                    max_code = self.env.cr.fetchall()[0][0]
                #formatto il max_code per riportarlo a video
                max_code = self._format_max_code_account(max_code, parent_code, start_from)
                #se il max_code è ritornato con -1 vuol dire che è finita la 
                #numerazione
                if max_code >= 0 :
                    return max_code 
                #se è -1 vuol dire che non è stato possibile numerare
                elif max_code == -1:
                    return None
                else:
                    return None
            except ValueError:
                #non fare niente, il max_code rimane a zero
                pass
            
            
    #metodo per formattare il max code in base alla lunghezza impostata in configurazione
    #il max_code deve essere di tipo stringa
    def _format_max_code_account(self, max_code, parent_code, start_from=0):
        #se non è presente il max_code, parto da 1
        #devo dividere il prefisso dal codice da ricercare, altrimenti
        #posso incorrere in errore.
        if max_code == None:
            max_prefix = parent_code
            max_code = str(start_from)
        else:
            max_prefix = parent_code
            max_code = max_code[len(parent_code):]

        #reperisco la lunghezza del code    
        str_pad = self._get_code_account_digits()
        if  str_pad:
            
            i = 0
            not_found = True
            while not_found: 
            
                r_max_code = str(int(max_code) + i)
                r_max_code = r_max_code.zfill(str_pad-len(max_prefix))
                r_max_code = max_prefix+r_max_code
                
                if self.search([('code','=',r_max_code)]):
                    i += 1
                    continue
                not_found = False
                max_code = r_max_code
                
            #verifico se la numerazione è finita
            #la numerazione è finita se la lunghezza del max_code è 
            #maggiore di quella consentita in configurazione 
            if len(max_code) > str_pad :
                #riporto -1 per indicare che è finita la numerazione
                return -1
            #riporto il max_code formattato
            return max_code
       
    def _get_code_account_digits(self, company_id=None):
        """Returns the default code size for the accounts.
        To figure out the number of digits of the accounts it look at the
        code size of the default receivable account of the company
        (or user's company if any company is given).
        """
        property_obj = self.env['ir.property']
        if not company_id:
            company_id = self.env.user.company_id.id
        properties = property_obj.search(
            [('name', '=', 'property_account_receivable'),
             ('company_id', '=', company_id),
             ('res_id', '=', False),
             ('value_reference', '!=', False)])
        number_digits = 6
        if not properties:
            # Try to get a generic (no-company) property
            properties = property_obj.search(
                [('name', '=', 'property_account_receivable'),
                 ('res_id', '=', False),
                 ('value_reference', '!=', False)])
        if properties:
            account = property_obj.get_by_record(properties[0])
            if account:
                number_digits = len(account.code)
        return number_digits
