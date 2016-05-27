# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _
from openerp.osv import orm, fields


class account_account(orm.Model):
    _inherit = 'account.account'

    def _default_type_from_partner(self, cr, uid, context=None):
        if 'customer' in context and 'supplier' in context:
            return 'view'
        if 'customer' in context:
            return 'receivable'
        if 'supplier' in context:
            return 'payable'
        return 'view'

    def _default_user_type_from_partner(self, cr, uid, context=None):
        type_obj = self.pool.get('account.account.type')
        isset_account_type = False
        if 'customer' in context:
            isset_account_type = type_obj.search(cr, uid,
                                                 [('code', '=', 'receivable')],
                                                 limit=1)
        else:
            if 'supplier' in context:
                isset_account_type = type_obj.search(cr, uid,
                                                     [('code', '=', 'payable')],
                                                     limit=1)
        
        if isset_account_type:
            return str(isset_account_type[0])
        return ''

    def _default_reconcile_from_partner(self, cr, uid, context=None):
        if 'customer' in context or 'supplier' in context:
            return True
        return False

    def _default_name_from_partner(self, cr, uid, context=None):
        if 'partner_name' in context and context['partner_name']:
            return context['partner_name']
        return ''  

    _columns = {'partner_id': fields.many2one('res.partner',
                                              'Partner')
                }

    _defaults = {
        'code': '',
        'type': _default_type_from_partner,
        'user_type': _default_user_type_from_partner,
        'reconcile': _default_reconcile_from_partner,
        'name': _default_name_from_partner,
     
    }

    def get_max_code_hole(self, cr, uid, parent_id, company_id):
        #leggo dall'oggetto account_account  con parent_id e riporto 
        #il valore code
        reads = self.read(cr, uid, parent_id, ['code'])
        #inizializzo il max_code 
        max_code = None
        #se valorizzato, reperisco il progressivo
        if reads['code']:
            #monitorizzo l'esecuzione della query per evitare di dare errori
            #nel caso in cui sono presenti valori alfanumerici
            try:
                # Reperisco la lunghezza del codice padre (mi serve per
                # fare poi la substring)
                parent_length = str(len(reads['code'])+1)
                
                #Verifico se esiste il primo
                sql = '''SELECT code 
                         FROM   account_account a
                         WHERE  1=1
                         AND    parent_id = %d 
                         AND    type <> 'view'
                         AND    CAST(SUBSTRING(a.code FROM %s) AS BIGINT) = 1
                      ''' % (parent_id,parent_length)
                cr.execute(sql)
                list = cr.fetchall()
                if list :               
                    sql = '''SELECT MIN(a.code) 
                             FROM   account_account a 
                             
                             WHERE  1=1 
                             AND    a.parent_id = %(parent_id)d
                             AND    a.type <> 'view'
                             AND    CAST(SUBSTRING(a.code FROM %(length)s) AS BIGINT) +1  
                             NOT IN (
                                SELECT CAST(SUBSTRING(b.code FROM %(length)s) AS BIGINT)
                                FROM   account_account b 
                                WHERE  1=1 
                                AND    b.parent_id = %(parent_id)d
                                AND    b.type <> 'view'
                             )
                          ''' % {'parent_id': parent_id, 'length' : parent_length }
                    cr.execute(sql)
                    max_code = cr.fetchall()[0][0]
                #formatto il max_code per riportarlo a video
                max_code = self._format_max_code(cr, uid, max_code, reads['code'], company_id)
            except ValueError:
                #non fare niente, il max_code rimane a zero
                pass

        return max_code

    def get_max_code(self, cr, uid, parent_id, company_id):
        max_code = None
        if parent_id:
            reads = self.read(cr, uid, parent_id, ['code'])
            if reads['code']:
                try:
                    #tratto il max code come un intero per sollevare un eccezione nel caso in
                    #cui sono presenti valori alfanumerici per i quali non è possibile reperire 
                    #il progressivo che dovrà essere inserito manualemte.
                    sql = '''SELECT MAX(code), CAST(MAX(code) AS BIGINT)
                             FROM account_account
                             WHERE 1=1
                             AND parent_id = %d
                             AND type <> 'view'
                    ''' % parent_id
                    cr.execute(sql)
                    max_code = cr.fetchall()[0][0]
                    max_code = self._format_max_code(cr, uid, max_code, reads['code'], company_id)
    
                except:
                    #altrimenti non faccio nulla ma riporto l'id a null 
                    pass

        return max_code

#     metodo per formattare il max code in base alla lunghezza impostata in configurazione
#     il max_code deve essere di tipo stringa
    def _format_max_code(self, cr, uid, max_code, parent_code, company_id):
        #se non è presente il max_code, parto da 1
        #devo dividere il prefisso dal codice da ricercare, altrimenti
        #posso incorrere in errore.
        if max_code == None:
            max_prefix = parent_code
            max_code = '0'
        else:
            max_prefix = parent_code
            max_code = max_code[len(parent_code):]

        #reperisco la lunghezza del code    
        str_pad = self._get_code_digits(cr, uid, company_id)
        if  str_pad:
            max_code = str(int(max_code) + 1)
            max_code = max_code.zfill(str_pad-len(max_prefix))
            max_code = max_prefix+max_code
            #verifico se la numerazione è finita
            #la numerazione è finita se la lunghezza del max_code è 
            #maggiore di quella consentita in configurazione 
            if len(max_code) > str_pad :
                #riporto -1 per indicare che è finita la numerazione
                return -1
            #riporto il max_code formattato
            return max_code

    @api.model
    def _get_code_digits(self, company_id=None):
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

    def onchange_parent_id(self, cr, uid, ids, parent_id, type):
        if not parent_id:
            return {'value': {'code':''}}
        if type == 'view' :
            parent_code= self.browse(cr, uid, parent_id).code
            return {'value': {'code':parent_code}}
        max_code = None

        #reperisco dalla configurazione il mtodo per reperire 
        #il conto in maniera progressiva. Per reperire dalla configurazione
        #devo sapere l'azienda di riferimento per la quale stò inserendo il 
        #sottoconto. 
        #l'azienda la reperisco dal padre del sottoconto stesso che stò inserendo
        #Reperisco il record del padre
        parent_data = self.browse(cr, uid, parent_id)
        #dal record del padre accedo alla chiave della company
        company_data=parent_data.company_id
        #dalla compagnia reperisco la configurazione 
        from_last_id = company_data.account_code_generation_last
        #verifico se devo reperire dall'ulimo 
        if from_last_id:
            max_code = self.get_max_code(cr, uid, parent_id, company_data.id)
        else:
            max_code = self.get_max_code_hole(cr, uid, parent_id, company_data.id)
        #se il max_code è ritornato con -1 vuol dire che è finita la 
        #numerazione
        if max_code >= 0 : 
            return {'value': {'code': max_code}}
        #se è -1 vuol dire che non è stato possibile numerare
        elif max_code == -1:
            return {'value': {},
                    'warning': {
                        'title': "Numerazione non possibile",
                        'message': "Non è possibile numerare, nessun codice libero",
                    }
            }
        else:
            return  {'value' : {}}
        return {'value': {}}

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'code', 'company_id'], context=context)
        res = []
        t_company_dict = {}
        for t_data in reads:
            if t_data['company_id']:
                t_company_dict.update({t_data['company_id'][0]: True})
            if len(t_company_dict)>1:
                break
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' ' + name
                if record['company_id'] and len(t_company_dict)>1:
                    name = '[' + record['company_id'][1] + '] ' + name
            res.append((record['id'], name))
        return res
