# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012-2013:
#        Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
try:
    import json
except ImportError:
    import simplejson as json


from openerp import SUPERUSER_ID, fields
from openerp.addons.web.controllers.main import ExcelExport
from openerp.osv import osv
from datetime import datetime
from openerp.http import request
import openerp.http as http
import time
import openerp
import unicodecsv as csv
import StringIO
import openerp.pooler as pooler
import os
import zipfile


class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)


    @http.route('/isa/export/xls_ddt', type='http', auth='user')
    def export_xls_picking(self, data, token):
        
        #La seguente riga permette di prendere l'user di riferimento con cui si è collegati all'azienda, tramite Superuser
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        #Ora prendo delle informazioni riguardante il cliente destinatario (Da res_users->res_company->res_partner)
        partner_dest = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.name
        partner_dest_street = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.street
        partner_dest_zip = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.zip
        partner_dest_city = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.city
        partner_dest_country_id = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.country_id.code
        if not partner_dest_country_id:
            partner_dest_country_id = 'IT'
        partner_dest_email = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.email
        partner_dest_phone = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.phone
        
        data = json.loads(data)
        
        model = data.get('model', [])

        rows = data.get('rows', [])
        rows = [int(x) for x in rows]
                
        osv_pool = pooler.get_pool(request.db)
        model = osv_pool.get('stock.ddt')
           
        datenow = datetime.now()
        
        #La seguente riga serve per tenere traccia dei Ddt che verranno selezionati
        stock_ddt_ids = model.search(request.cr, request.uid, [('id','in',rows)])
        
        name_file = 'Prebolla_' + datenow.strftime("%Y%m%d_%H:%M:%S") + '.csv' 
           
        for stock_ddt_id in stock_ddt_ids:  
            
            stock_ddt = model.browse(request.cr, request.uid, stock_ddt_id, context=request.context) 
            
            #Se lo stato del Ddt selezionato è confermato,allora scrivo i dati nel file che viene generato
            if stock_ddt.state == 'confirmed':            
                
                #Effettuo un controllo sull'esistenza del default_code relativo al prodotto dhl  
                if stock_ddt.product_code_dhl.default_code:
                    default_code_ddt = stock_ddt.product_code_dhl.default_code[:-3]
                else:
                    default_code_ddt = 0  
                     
                    
                ddtDate = fields.Date.from_string(stock_ddt.delivery_date).strftime("%Y%m%d") if stock_ddt.delivery_date else stock_ddt.ddt_date   
          
                ddtNumber = stock_ddt.name if stock_ddt.name else '0'  
                
                #I seguenti campi: nomeDest,viaDest,capDest,cittaDest,nazioneDest,emailDest e telefonoDest li prendo
                # dallo stock.picking (Viene creato un ordine di vendita->picking->Ddt).
                #Un Ddt ha più picking, e quindi prendo il primo e dal picking risalgo al partner
                picking_id = stock_ddt.picking_ids[0]

                ragioneSoc = stock_ddt.partner_id.name
                nomeDest = picking_id.partner_id.name
                viaDest = picking_id.partner_id.street
                capDest = picking_id.partner_id.zip
                cittaDest = picking_id.partner_id.city
                nazioneDest = picking_id.partner_id.country_id.code
                emailDest = picking_id.partner_id.email
                telefonoDest = picking_id.partner_id.phone

                #capDestSbagliato = stock_ddt.partner_id.zip
                #cittaDestSbagliata = stock_ddt.partner_id.city
                #nazioneDestSbagliata = stock_ddt.partner_id.country_id.code
                #emailDestSbagliata = stock_ddt.partner_id.email
                #telefonoDestSbagliato = stock_ddt.partner_id.phone

                if not nazioneDest:
                    nazioneDest = 'IT'
                    

                if not emailDest:
                    emailDest = ''
                    

                if not telefonoDest:
                    telefonoDest = '0'    
                     
     
                #Costruisco l'array che contiene tutti i campi con i relativi valori
                arrayRow = [['Codice prodotto dhl',default_code_ddt],
                            ['Data spedizione', ddtDate],
                            ['Tipo spedizione',stock_ddt.shipping_type],
                            ['Codice pagante dhl',stock_ddt.user_id.company_id.paying_code_dhl],
                            [';',''],
                            [';',''],
                            [';',''],
                            [';',''],
                            ['Riferimento mitt.',ddtNumber],
                            ['Descrizione contenuto','Integratori/Dispositivi medici'],
                            ['Mitt.',partner_dest],
                            ['Contatto mitt.','.'],
                            ['Indirizzo1 mitt.',partner_dest_street],
                            [';',''],
                            [';',''],
                            ['Cap mitt.',partner_dest_zip],
                            ['Citta mitt.',partner_dest_city],
                            ['Nazione mitt.',partner_dest_country_id],
                            [';',''],
                            ['Mail mitt.',partner_dest_email],
                            ['Telefono mitt.',partner_dest_phone],
                            ['Ragione sociale soc.',ragioneSoc],
                            ['Contatto destino',nomeDest],
                            ['Indirizzo1 destino',viaDest],
                            [';',''],
                            [';',''],
                            ['Cap destino',capDest],
                            ['Citta destino',cittaDest],
                            ['Nazione destino',nazioneDest],
                            ['Email destinatario',emailDest],
                            [';',''],
                            ['Telefono dest.',telefonoDest],
                            ['Peso spedizione totale',stock_ddt.weight],
                            ['Colli totali',stock_ddt.parcels],
                            ['Larghezza collo','1'],
                            ['Altezza collo','1'],
                            ['Lunghezza collo','1'],
                            [';','']
                           ] 
                
                with open(('/var/tmp/' + name_file),"a") as testfile:
                    writer = csv.writer(testfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')
                    writer.writerow([y[1] for y in arrayRow])
                
            else:
                pass    


        #Se invece non esistono Ddt che hanno lo stato confermato e quindi sono solo Ddt in stato bozza o annullato,
        #deve stampare il file.csv con solo una riga in cui dice che non sono presenti DDt in stato confermato
        if not os.path.isfile('/var/tmp/' + name_file): 
            with open(('/var/tmp/' + name_file),"a") as testfile:
                header=['Non esistono Ddt in stato confermato da elaborare']
                writer = csv.writer(testfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')
                writer.writerow(header)
        else:
                pass

        #Devo leggere il file creato e inserirlo in data
        data = open('/var/tmp/' + name_file)
        
        #La riga seguente serve, in base al percorso specificato, ad eliminare il file che è stato generato
        os.remove('/var/tmp/'+name_file) 
          

        return request.make_response(
            data,
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % name_file),
                ('Content-Type', 'application/csv')
            ],
            cookies={'fileToken': token}
        )
        
  
    @http.route('/isa/export/xls_invoice_ddt', type='http', auth='user')
    def export_xls_invoice(self, data, token):
        
        #La seguente riga permette di prendere l'user di riferimento con cui si è collegati all'azienda, tramite Superuser
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        #Ora prendo delle informazioni riguardante il cliente destinatario (Da res_users->res_company->res_partner)
        partner_dest = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.name
        partner_dest_street = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.street
        partner_dest_zip = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.zip
        partner_dest_city = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.city
        partner_dest_country_id = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.country_id.code
        if not partner_dest_country_id:
            partner_dest_country_id = 'IT'
        partner_dest_email = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.email
        partner_dest_phone = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).company_id.partner_id.phone
        
        
        data = json.loads(data)
        
        model = data.get('model', [])

        rows = data.get('rows', [])
        rows = [int(x) for x in rows]
                
        osv_pool = pooler.get_pool(request.db)
        model = osv_pool.get('account.invoice')
           
        datenow = datetime.now()
        
        #La seguente riga serve per tenere traccia delle fatture che verranno selezionate
        account_invoice_ids = model.search(request.cr, request.uid, [('id','in',rows)])
        
        name_file = 'Fattura_' + datenow.strftime("%Y%m%d_%H:%M:%S") + '.csv' 
           
        for account_invoice_id in account_invoice_ids:  
            
            account_invoice = model.browse(request.cr, request.uid, account_invoice_id, context=request.context) 
            
            #Se lo stato della fattura selezionata è confermato, allora scrivo i dati nel file che viene generato
            if account_invoice.is_shipping_invoice:            
            
                #Effettuo un controllo sull'esistenza del default_code relativo al prodotto dhl  
                if account_invoice.product_code_dhl.default_code:
                    default_code_invoice = account_invoice.product_code_dhl.default_code[:-3]
                else:
                    default_code_invoice = 0  
                    
                invoiceDate = fields.Date.from_string(account_invoice.date_invoice).strftime("%Y%m%d") if account_invoice.date_invoice else account_invoice.date_invoice   
          
                invoiceNumber = account_invoice.name if account_invoice.name else '0'  
                
                #I seguenti campi: nomeDest,viaDest,capDest,nazioneDest,emailDest e telefonoDest, li prendo dallo
                #stock.picking.
                #Una fattura ha più picking, e quindi prendo il primo e dal picking risalgo al partner
                picking_id = account_invoice.picking_ids[0]
                ragioneSoc = account_invoice.partner_id.name
                nomeDest = picking_id.partner_id.name
                viaDest = picking_id.partner_id.street

                capDest = picking_id.partner_id.zip
                cittaDest = picking_id.partner_id.city
                nazioneDest = picking_id.partner_id.country_id.code
                emailDest = picking_id.partner_id.email
                telefonoDest = picking_id.partner_id.phone

                #capDestSbagliato = account_invoice.partner_id.zip
                #cittaDestSbagliata = account_invoice.partner_id.city
                #nazioneDestSbagliata = account_invoice.partner_id.country_id.code
                #emailDestSbagliata = account_invoice.partner_id.email
                #telefonoDestSbagliato = account_invoice.partner_id.phone

                if not nazioneDest:
                    nazioneDest = 'IT'

                if not emailDest:
                    emailDest = ''

                if not telefonoDest:
                    telefonoDest = '0'    
                     
                #Costruisco l'array che contiene tutti i campi con i relativi valori
                arrayRow = [['Codice prodotto dhl',default_code_invoice],
                            ['Data spedizione', invoiceDate],
                            ['Tipo spedizione',account_invoice.shipping_type],
                            ['Codice pagante dhl',account_invoice.user_id.company_id.paying_code_dhl],
                            [';',''],
                            [';',''],
                            [';',''],
                            [';',''],
                            ['Riferimento mitt.',invoiceNumber],
                            ['Descrizione contenuto','Integratori/Dispositivi medici'],
                            ['Mitt.',partner_dest],
                            ['Contatto mitt.','.'],
                            ['Indirizzo1 mitt.',partner_dest_street],
                            [';',''],
                            [';',''],
                            ['Cap mitt.',partner_dest_zip],
                            ['Citta mitt.',partner_dest_city],
                            ['Nazione mitt.',partner_dest_country_id],
                            [';',''],
                            ['Mail mitt.',partner_dest_email],
                            ['Telefono mitt.',partner_dest_phone],
                            ['Ragione sociale soc.',ragioneSoc],
                            ['Contatto destino',nomeDest],
                            ['Indirizzo1 destino',viaDest],
                            [';',''],
                            [';',''],
                            ['Cap destino',capDest],
                            ['Citta destino',cittaDest],
                            ['Nazione destino',nazioneDest],
                            ['Email destinatario',emailDest],
                            [';',''],
                            ['Telefono dest.',telefonoDest],
                            ['Peso spedizione totale',account_invoice.shipping_invoice_weight],
                            ['Colli totali',account_invoice.shipping_invoice_number_of_packages],
                            ['Larghezza collo','1'],
                            ['Altezza collo','1'],
                            ['Lunghezza collo','1'],
                            [';','']
                           ] 
                
                with open(('/var/tmp/' + name_file),"a") as testfile:
                    writer = csv.writer(testfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')
                    writer.writerow([y[1] for y in arrayRow])
                
            else:
                pass    


        #Se invece non esistono fatture che hanno lo stato confermato, deve stampare il file.csv con solo una 
        #riga in cui dice che non sono presenti fatture in stato confermato
        if not os.path.isfile('/var/tmp/' + name_file): 
            with open(('/var/tmp/' + name_file),"a") as testfile:
                header=['Non esistono Fatture in stato confermato da elaborare']
                writer = csv.writer(testfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')
                writer.writerow(header)
        else:
                pass

        #Devo leggere il file creato e inserirlo in data
        data = open('/var/tmp/' + name_file)
        
        #La riga seguente serve, in base al percorso specificato, ad eliminare il file che è stato generato
        os.remove('/var/tmp/'+name_file) 
          

        return request.make_response(
            data,
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % name_file),
                ('Content-Type', 'application/csv')
            ],
            cookies={'fileToken': token}
        )
        

