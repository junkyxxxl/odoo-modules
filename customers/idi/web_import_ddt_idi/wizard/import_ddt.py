# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import csv
import base64
import os.path
from tempfile import NamedTemporaryFile
from openerp import models, fields, api
from openerp.exceptions import Warning
from docutils.nodes import row
from datetime import datetime


class customImportError(Exception):
    pass

class import_ddt_idi(models.TransientModel):
    """ DDT Import """

    _name = "web.import.ddt.idi.wizard"
    _description = "DDT Import wizard"

    #Colonne DB.
    data = fields.Binary(string='File', required=True, create=False)
    filename = fields.Char(string='Filename')
    delimiter = fields.Char(string="Delimitatore", default=";", size=1, required=True)
    samples_import = fields.Boolean(
        string="Importazione materiali campione",
        help='''La procedura crea ordine di vendita/ ordine di consegna e ddt ma con la clausola di non fatturabilità.
        Tale importazione è eseguita al fine di movimentare correttamente i materiali campione all'interno dei magazzini.
        '''
    )

    @api.multi
    def import_ddt(self):
        #Verifico se si tratta di un file csv
        __ , file_extension = os.path.splitext(self.filename)
        file_extension = file_extension.lower()
        #Deve essere un file con estensione CSV
        if not file_extension or file_extension != ".csv":
            raise Warning("Il file deve avere estensione csv")
        #Reperisco il delimitatore
        delimiter = self.delimiter
        #Creo il file temporaneeo dove appoggio i dati del file forniti dal wizard
        ddtFile = NamedTemporaryFile()
        ddtFile.write(base64.decodestring(self.data))
        ddtFile.seek(0)
        #Leggo il file csv
        reader = csv.reader(ddtFile, quotechar='"', delimiter=str(delimiter))
        #Inizio a leggere il file ed ad eseguire i controlli
        header_ids = []
        for riga, row in enumerate(reader):
            '''
                La prima colonna del file CSV indica se si tratta di un dato di testata o di riga
                TESTA - Dato di testata
                CORPO - Dato di riga
            '''
            #Di dafault non ci sono errori
            status, message = True, None
            tipoRecord = row[0].strip()
            if tipoRecord == 'TESTA':
                # Verifico se si tratta di importazione campioni (se è stato settato correttamente il flag)
                import_campione = row[23].strip().upper()
                if import_campione == 'C' and not self.samples_import:
                    raise Warning("Il file è di tipo importazione campioni ma non è stato impostato il flag per l'importazione.")
                if not import_campione and self.samples_import:
                    raise Warning("Il file è di tipo importazione non campioni ma è stato impostato il flag per l'importazione campioni.")
                status, message, header_id = self._elabora_testata(row)
                header_ids.append(header_id)
            elif tipoRecord == 'CORPO':
                status, message = self._elabora_riga(row, header_id)
            else:
                raise Warning("Errore alla linea " + str(riga+1)+". Il Tipo Record " + tipoRecord + " non è riconosciuto.")
            #Verifico se l'elaborazione ha avuto esito positivo, altrimenti sollevo l'errorre
            if not status:
                raise Warning("Errore alla linea " + str(riga+1)+". "+message)
        #Se non ci sono stati erorri, richiamo l'elaborazione dei movimenti
        self.env['track.import.ddt'].process_track()
        #Fine elaborazione.
        return {
                "type": "ir.actions.act_window",
                "res_model": "track.import.ddt",
                "name": "Risultato elaborazione file CSV",
                "views": [[False, "tree"], [False, "form"]],
                "domain": [["id", "in", header_ids]]
                }


    def _elabora_testata(self, row):
        '''La funzione elabora i dati di testa e riporta l'esito dell'elaborazione. Scrive il record su track
        status -- Esito dell'elaborazione
        message -- Messaggio di erorre in caso di elaborazione errata.
        '''
        status, message, header_id = True, None, None
        try:
            #Numero del DDT è un dato obbligatorio e deve essere numerico
            ddtNumber = row[4].strip()
            if not ddtNumber:
                raise customImportError("Il numero di DDT è obbligatorio e non è stato passato.")
            #Codice deposito è obbligatorio
            store_code = row[15].strip()
            if not store_code:
                raise customImportError("Codice deposito è obbligatorio e non è stato passato.")
            store_code = store_code.zfill(2)
            # Verifico se per Magazzino/DDT esiste già la riga. Se è in stato di eccezzione o pronta aggiorno i dati
            # altrimenti sollevo un errore.
            track_ddt = self.env['track.import.ddt'].search([('ddt_number', '=', ddtNumber), ('store_code', '=', store_code)])
            if track_ddt and track_ddt.state in ('done','inprocess'):
                raise customImportError("Il movimento di importazione DDT è già presente nel sistema con id "+str(track_ddt.id)+" ed è già stato elaborato oppure è in elaborazione.")
            #Reperisco il codice del partner e verifico che esista in anagrafica e che al partner code sia collegato un
            #solo cliente
            partnerCode = row[5].strip()
            if not partnerCode:
                raise customImportError("Il codice del cliente è obbligatorio e non è stato passato.")
            #Codice di spedizione. Deve esistere per il partner specificato ed è obbligatorio
            deliveryCode = str(int(row[22]))
            if not deliveryCode:
                raise customImportError("Il codice di spedizione è obbligatorio e non è stato passato.")
            #Reperisco dal file csv, il codice del pagamento e verifico se esiste in anagrafica
            paymentCode = row[14].strip()
            if not paymentCode:
                raise customImportError("Il codice pagamento è obbligatorio e non è stato passato.")
            #dal codice del magazzino, reperisco il deposito ed il partner(se presenti)
            contractor = None
            warehouse = self.env['stock.warehouse'].search([('code','=',store_code)])
            if not warehouse:
                raise customImportError("Non è stato possibile trovare un magazzino con codice %s" %(store_code))
            #Se si tratta di un elaborazione per campioni è obbligatorio sul magazzino il tipo documento per campioni
            document_type_sample = None
            if self.samples_import:
                document_type_sample = warehouse.document_type_sample_id
                if not document_type_sample:
                    raise customImportError("Sul magazzino " +str(warehouse.name)+" non è stato impostato il Tipo documento materiale campione.")
            #Dal magazzino reperisco, se presente, il partner associato
            #dal magazzino provo a reperire il partner
            if warehouse.partner_id:
                res_partner = warehouse.partner_id
                #verifico se il partner è un contatto
                if res_partner.parent_id:
                    contractor = res_partner.parent_id
                elif res_partner:
                    contractor = res_partner
            #Data Bolla è obbligatoria e deve essere valida
            dateDdt = row[16].strip()
            if not dateDdt:
                raise customImportError("La data del DDT è obbligatoria e non è stata passata")
            try:
                dateDdt = datetime.strptime(dateDdt, "%y%m%d")
            except ValueError:
                raise customImportError("La data è formalmente errata.")
            #Se l'elborazione ha avuto esito positivo, Scrivo/aggiorno la tabella temporaneea
            track_vals = {
                    'ddt_number': ddtNumber,
                    'delivery_code': deliveryCode,
                    'date': dateDdt,
                    'partner_code': partnerCode,
                    'store_code': store_code,
                    'payment_code': paymentCode,
                    'state': 'ready',
                    'sample_movement': self.samples_import,
            }
            if document_type_sample:
                track_vals.update({'document_type_sample': document_type_sample.id})
            if warehouse:
                track_vals.update({'warehouse': warehouse.id})
            if contractor:
                track_vals.update({'contractor': contractor.id})
            #Creazione
            if not track_ddt:
                track_id = self.env['track.import.ddt'].create(track_vals)
                header_id = track_id.id
            else:
                #Modifica, devo cancellare le eventuali linee.
                header_id = track_ddt.id
                track_ddt.ddt_line.unlink()
                processing_log = track_ddt.processing_log + "\nMovimento aggiornato il :"+datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
                track_vals.update({'processing_log':processing_log})
                track_ddt.write(track_vals)
            status, message = True, None
            return status, message, header_id
        #Intercetto soltanto gli errori definiti come customImportError. Eventuali errori di sistema
        #vengono comunque segnalati
        except customImportError as txt:
            status = False
            message = str(txt)
            return status, message, header_id
        except IndexError:
            status = False
            message = "%s" %("Il file non è nel formato atteso.")
            return status, message, header_id
        except:
            raise



    def _elabora_riga(self, row, header_id):
        '''La funzione elabora i dati di riga e riporta l'esito dell'elaborazione. Scrive il record su track
        status -- Esito dell'elaborazione
        message -- Messaggio di erorre in caso di elaborazione errata.
        '''
        status, message = True, None
        try:
            #Numero del DDT è un dato obbligatorio e deve essere numerico
            ddtNumber = row[4].strip()
            if not ddtNumber:
                raise customImportError("Il numero di DDT è obbligatorio e non è stato passato.")
            #Deve esistere la testata. Verifico che esisti la testata.
            ddt_head = self.env['track.import.ddt'].browse(header_id)
            if not ddt_head:
                raise customImportError("Impossibile trovare una testata in riferimento al ddt "+str(ddtNumber))
            ddt_head.ensure_one()
            #Se la testata è in stato di completato o in elaborazione
            if ddt_head and ddt_head.state in ('done','inprocess'):
                raise customImportError("Il movimento di importazione DDT è già presente nel sistema con id "+str(ddt_head.id)+" ed è già stato elaborato oppure è in elaborazione.")
            #Reperisco il prodotto che è obbligatorio
            product = row[5].strip()
            if not product:
                raise customImportError("Il codice prodotto è obbligatorio e non è stato passato.")
            #Quantità obbligatoria
            qty = row[8].strip()
            qty = str(int(row[8])/1000)
            if not qty:
                raise customImportError("La quantità è obbligatoria e non è stata passata.")
            #Omaggio
            free = row[9].strip()
            # In caso di importazione campioni setto tutti gli articoli come omaggi
            if self.samples_import:
                free = 'gift'
            elif free:
                if free == '2':
                    free = 'gift'
                elif free == '1':
                    free = 'base_gift'
                else:
                    free = None
            else:
                free = None
            #Prezzo non è obbligatorio. Se non passato prende quello del prodotto
            tax_code = row[10].strip()
            '''Deposito dal quale reperisco il terzista, non obbligatorio. Ogni file riguarda solo un magazzino'''
            store_code = row[11].strip()
            #Il codice del magazzino deve essere sempre considerato lungo 2.
            if store_code:
                store_code = store_code.zfill(2)
            #Lotto e data di scadenza obbligatori
            lot = row[12].strip()
            expirationDate = row[13].strip()
            if not lot:
                raise customImportError("Il lotto è obbligatorio e non è stato passato.")
            if not expirationDate:
                raise customImportError("La data di scadenza lotto è obbligatoria e non è stata passata")
            try:
                expirationDate = datetime.strptime(expirationDate, "%d%m%Y")
            except ValueError:
                raise customImportError("La data scadenza lotto è formalmente errata.")
            #Se l'elaborazione ha avuto esito positivo, scrivo la riga
            track_line = self.env['track.import.ddt.line'].create({
                                                                   'product': product,
                                                                   'qty': qty,
                                                                   'tax': tax_code,
                                                                   'store_code': store_code,
                                                                   'lot': lot,
                                                                   'expiration_date': expirationDate,
                                                                   'ddt_id': ddt_head.id,
                                                                   'free': free
                                                                   })
            status, message = True, None
            return status, message
        except customImportError as txt:
            status = False
            message = str(txt)
            return status, message
        except IndexError:
            raise
            status = False
            message = "%s" %("Il file non è nel formato atteso.")
            return status, message
        except:
            raise
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
