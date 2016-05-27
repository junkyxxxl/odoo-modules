# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from openerp import SUPERUSER_ID

class res_partner(models.Model):
    _inherit = ['res.partner']
    
    customer_code = fields.Char(
            string="Customer Code", 
            track_visibility='always', 
            help="Customer code",
            required=False,
    )
    supplier_code = fields.Char(
            string="Supplier Code", 
            track_visibility='always', 
            help="Supplier code",
            required=False,
    )
    property_account_receivable = fields.Many2one(
            relation='account.account',
            string="Account Receivable",
            company_dependent=True,
            track_visibility='always')
    
            
    @api.model
    def create(self, vals):
        '''
            La funzione "create" è stata riscritta per prevedere la creazione automatica del conto cliente/fornitore
            sul piano dei conti. 
            In automatico viene creato il codice conto (e associato al partner) se è stato specificato il flag cliente/fornitore nel tab "Vendite e Acquisti".
            Questa funzionalità è valida solo se si sta inserendo un cliente (parent_id non specificato)
        '''

        #Se sono vuoti sia il cliente che il property_account_receivable, e di conseguenza il fornitore,
        # allora richiamo la super in modo che vengono settati questi valori
        if(not vals.get('customer') and not vals.get('property_account_receivable')) and (not vals.get('supplier') and not vals.get('property_account_payable')):
            partner = super(res_partner, self).create(vals)
            #A questo punto, se sono stati settati, ridefinisco la write
            if(partner.customer and partner.property_account_receivable.id):
                    vals.update({'customer': partner.customer})
                    partner.write(vals)

            if(partner.supplier and partner.property_account_payable):
                    vals.update({'supplier': partner.supplier})
                    partner.write(vals)
            return partner

        #Se si stà inserendo un contatto non devo eseguire la funzione ma devo direttamente creare il partner
        if vals.get('parent_id'):
            partner = super(res_partner, self).create(vals)
            return partner
        
        #Reperisco i codici cliente/fornitore associati di default dalle property
        default_account_receivable = self.get_parent_account('customer')
        default_account_payable = self.get_parent_account('supplier')

        #Repersico il conto di default per il cliente
        account_receivable_id = vals.get('property_account_receivable') if vals.get('property_account_receivable') else False
        #Repersico il conto di default per il fornitore
        account_payable_id = vals.get('property_account_payable') if vals.get('property_account_payable') else False 

        '''
           CLIENTE
           Creo il conto cliente se non è stato settato nessun dato nella form (quindi è stato lasciato quello di 
           default)
         '''
        if (not account_receivable_id) or (not default_account_receivable) or (account_receivable_id == default_account_receivable.id):
            #Controllo che sia impostato il conto di dafult per il cliente
            if vals.get('customer') and not default_account_receivable:
                raise Warning("Impossibile salvare. Non è stato possibile trovare il conto di default da assegnare al cliente")
            #Se è cliente e: o ha il valore di default relativo al conto oppure il valore del conto è vuoto  
            if vals.get('customer') and ((account_receivable_id == default_account_receivable.id) or (not account_receivable_id)):
                #Tipo conto
                user_type = self.env['account.account.type'].search([('code', '=', 'receivable')])[0]
                #Creo il conto utilizzando la funzione già esistente
                #Come conto padre passo quello impostato nel conto di default e come tipo regolare (other)
                code = vals.get('customer_code') if vals.get('customer_code') else None
                account_receivable_code, customer_form_code = self._retrieve_account_code(code, default_account_receivable.parent_id.id, 'customer')
                account_receivable_id = self._create_account_account(account_receivable_code, default_account_receivable, vals['name'], 'receivable')
                vals.update({'property_account_receivable':account_receivable_id,
                             'customer_code': customer_form_code})
                self.env.user.company_id.write({'start_new_partner_code_from':customer_form_code})                

        '''
           FORNITORE
           Creo il conto fornitore se non è stato settato nessun dato nella form (quindi è stato lasciato quello di 
           default)
        '''
        if (not account_payable_id) or (not default_account_payable) or (account_payable_id == default_account_payable.id):
            #Controllo che sia impostato il conto di dafult per il fornitore
            if vals.get('supplier') and not default_account_payable:
                raise Warning("Impossibile salvare. Non è stato possibile trovare il conto di default da assegnare al fornitore")
            if vals.get('supplier') and ((account_payable_id == default_account_payable.id) or (not account_payable_id)):
                #Tipo conto
                user_type = self.env['account.account.type'].search([('code', '=', 'payable')])[0]
                #Creo il conto utilizzando la funzione già esistente
                #Come conto padre passo quello impostato nel conto di default e come tipo regolare (other)
                code = vals.get('supplier_code') if vals.get('supplier_code') else None
                account_payable_code, supplier_form_code = self._retrieve_account_code(code, default_account_payable.parent_id.id, 'supplier')
                account_payable_id = self._create_account_account(account_payable_code, default_account_payable, vals['name'], 'payable')
                vals.update({'property_account_payable':account_payable_id,
                             'supplier_code': supplier_form_code})
                self.env.user.company_id.write({'start_new_supplier_code_from':supplier_form_code})

        #Creo il partner
        partner = super(res_partner, self).create(vals)
        return partner


    @api.one
    def write(self, vals):
        '''
           La funzione crea il conto cliente/fornitore solo se è stato modificato il flag di
           cliente fornitore ed è presente il conto di default e se l'utente non è amministratore
        '''
        # Se è utente amministratore non eseguo la creazione del conto
        if SUPERUSER_ID == self.env.user.id:
            return super(res_partner, self).write(vals)
        customer = vals.get('customer') if vals.get('customer') else self.customer
        #Modifica il property_account_receivable, mettendo un property_account_receivable già esistente
        if vals.get('property_account_receivable'):
            property_account_receivable = self.env['account.account'].browse(vals.get('property_account_receivable'))
        else:
            #Altrimenti lo cancello, me lo mette di default
            property_account_receivable = self.property_account_receivable
        
        default_account_receivable = self.get_parent_account('customer')
        
        supplier = vals.get('supplier') if vals.get('supplier') else self.supplier
        if vals.get('property_account_payable'):
            property_account_payable = self.env['account.account'].browse(vals.get('property_account_payable'))
        else:
            property_account_payable = self.property_account_payable
        default_account_payable = self.get_parent_account('supplier')
        
        name = vals.get('name') if vals.get('name') else self.name
        
        parent_id = vals.get('parent_id') if vals.get('parent_id') else self.parent_id
        
        #------CLIENTI------#
        if customer and property_account_receivable == default_account_receivable:
            code = vals.get('customer_code') if vals.get('customer_code') else self.customer_code
            account_code_receivable, customer_form_code = self._retrieve_account_code(code,property_account_receivable.parent_id.id, 'customer')
            account_account_receivable_id = self._create_account_account(account_code_receivable, property_account_receivable, name, type='receivable')
            vals.update({'property_account_receivable':account_account_receivable_id,
                         'customer_code': customer_form_code})
        
    
 
        #------FORNITORI------#
        if supplier and property_account_payable == default_account_payable:
            code = vals.get('supplier_code') if vals.get('supplier_code') else self.supplier_code
            account_code_payable, supplier_form_code = self._retrieve_account_code(code,property_account_payable.parent_id.id, 'supplier')
            account_account_payable_id = self._create_account_account(account_code_payable, property_account_payable, name, type='payable')
            vals.update({'property_account_payable':account_account_payable_id,
                         'supplier_code': supplier_form_code})
        
        #Salvo il partner
        partner = super(res_partner, self).write(vals)
        return partner

    def get_parent_account(self, type, company_id=None):
        '''Ritorna il conto contabile genitore associato al cliente/fornitore.'''
        account = None
        property_obj = self.env['ir.property']
        if not company_id:
            company_id = self.env.user.company_id.id
        if type == 'supplier':
            properties = property_obj.search(
                [('name', '=', 'property_account_payable'),
                 ('company_id', '=', company_id),
                 ('res_id', '=', False),
                 ('value_reference', '!=', False)])
        if type == 'customer':
            properties = property_obj.search(
                [('name', '=', 'property_account_receivable'),
                 ('company_id', '=', company_id),
                 ('res_id', '=', False),
                 ('value_reference', '!=', False)])
        if properties:
            account = property_obj.get_by_record(properties[0])
        return account
    
    
    def _retrieve_account_code(self, code, parent_id, customer_supplier, type_account='other'):
        """
            Reperisce il codice del conto.
            
            :type code: str
            :param code: codice del partner

            :type parent_id: int
            :param parent_id: L'ID del conto padre di riferimento

            :type type_account: str
            :param type_account: Il tipo conto da generare (view, other, ecc...)
            :default type_account: 'other'

            :rtype: str
            :return: codice del conto
        """
        #Creo il conto utilizzando la funzione già esistente nel modulo account_makeover di isaSrl
        #Vado a prendere tramite il parent_id, il codice del conto
        #account_root è il codice del conto mastro
        account_root = self.env['account.account'].browse(parent_id).code
        account_account_obj = self.env['account.account']
        #Creazione codice conto
        account_code = account_account_obj.get_next_account_code(parent_id, type_account, customer_supplier)
        
        if customer_supplier == 'customer' and code:
            account_code_modified_length = len(account_code)-len(account_root)
            if len(code)<=account_code_modified_length:
                code = code.rjust(account_code_modified_length,'0')
                account_code = str(account_root) + str(code)
            else:
                if len(code) > account_code_modified_length:
                    raise Warning("Lunghezza del codice supera quella del piano dei conti")
            
        elif customer_supplier == 'supplier' and code:
            account_code_modified_length = len(account_code)-len(account_root)
            if len(code)<=account_code_modified_length:
                code = code.rjust(account_code_modified_length,'0')
                account_code = str(account_root) + str(code)
            else:
                if len(code) > account_code_modified_length:
                    raise Warning("Lunghezza del codice supera quella del piano dei conti")
        
        # Riporto anche il codice da impostare su customer_code / supplier_code
        normal_code = account_code[len(account_root):].lstrip('0')

        return account_code, normal_code
 
    
    def _create_account_account(self, account_code, default_account, name, type='receivable'):
        user_type = self.env['account.account.type'].search([('code', '=', type)])[0]
        account_vals = {'code':account_code,
                            'name':name,
                            'user_type':user_type.id,
                            'type':type,
                            'parent_id':default_account.parent_id.id  ,
                            'level':default_account.level + 1,
                            'reconcile':True
                           }
        '''
            Usare questa configurazione per le importazioni massive dei clienti.
            Qusta impostazione non esegue il calcolo del parent_left / right. 
            In questo caso non viene imputato il parent_left / right sul piano dei conti ed il 
            programma da errore se si prova ad accedere ad un conto. Per ricalcolare il parent_left/right 
            devono essere cancellate le colonne e aggiornato il modulo account_accountant            
        '''
        #account_payable_id = self.env['account.account'].with_context({'defer_parent_store_computation': True}).create(account_vals)
        account_payable_id = self.env['account.account'].create(account_vals)
        return account_payable_id

    
