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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.exceptions import ValidationError, Warning

class MappingError(Exception):
    pass

class track_import_ddt(models.Model):

    _name = "track.import.ddt"
    _description = "DDT Import Track"


    def _get_start_processing(self):
        return "Movimento inserito il :"+datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

    @api.one
    @api.depends('order_reference')
    def _get_delivery_order(self):
        self.picking_reference = self.order_reference.picking_ids if self.order_reference.picking_ids else None

    @api.one
    @api.depends('order_reference')
    def _get_ddt(self):
        self.ddt_reference = self.order_reference.ddt_ids if self.order_reference.ddt_ids else None


    #Name
    name = fields.Char(string="Name", compute="_compute_name")
    #Terzista
    contractor = fields.Many2one('res.partner', string="Contractor", required=False, readonly=True, copy=False, select=True)
    #Magazzino
    warehouse = fields.Many2one(comodel_name='stock.warehouse', string="Magazzino", required=False, readonly=True, copy=False, select=True)
    #Numero DDT
    ddt_number = fields.Char(string="DDT Number", required=True, readonly=True, copy=False, select=True)
    #Codice di spedizione
    delivery_code = fields.Char(string="Delivery code", required=True, copy=False, select=True)
    date = fields.Datetime(string="DDT date", readonly=True, copy=False, select=True)
    #Partner_code come campo numerico.
    partner_code = fields.Char(string="Partner code", required=True, copy=False, select=True)
    #Codice deposito
    store_code = fields.Char(string="Store code", required=True, copy=False, select=True)
    #Log di elaborazione
    processing_log = fields.Text(string="Processing log", default=_get_start_processing, copy=False, readonly=True)
    #Stato (pronto, errore, elaborato)
    state = fields.Selection(selection=[('ready', 'Ready to be Processed'),
                                         ('except', 'Exception'),
                                         ('inprocess', 'In Process'),
                                         ('done', 'Done')],
                                         default="ready", string="Status", readonly=True, copy=False, select=True)
    #Log di errore
    status_log = fields.Text(string="Status log", copy=False, readonly=True)
    ddt_line = fields.One2many(comodel_name="track.import.ddt.line", inverse_name="ddt_id", string="DDT Lines", copy=False)

    order_reference = fields.Many2one('sale.order', string="Order Reference", readonly=True, copy=False)
    picking_reference = fields.One2many('stock.picking', string="Delivery order", compute="_get_delivery_order", copy=False, readonly=True)
    ddt_reference = fields.One2many('stock.ddt', string="DDT", compute="_get_ddt", copy=False, readonly=True)
    payment_code = fields.Char(string="Payment code", required=False)
    # Importazione per campioni
    sample_movement = fields.Boolean(string="Elaborazione per materiali campione", readonly=True)
    document_type_sample = fields.Many2one(comodel_name='sale.document.type', string="Tipo documento per importazione materiali campioni",
                                           required=False
                                           )

    @api.multi
    def action_ready(self):
        self.state = 'ready'

    #Controllo univocità record per magazzino/numero ddt
    @api.one
    @api.constrains('ddt_number','store_code')
    def _check_unique(self):
        occurence = self.env['track.import.ddt'].search_count([('ddt_number','=',self.ddt_number),('store_code', '=', self.store_code)])
        if occurence > 1:
            raise ValidationError("Esiste già un ddt con numero "+str(self.ddt_number))

    @api.one
    @api.depends('ddt_number','warehouse')
    def _compute_name(self):
        if self.warehouse:
            self.name = "%s/%s" %(self.warehouse.name, self.ddt_number)
        else:
            self.name = "%s/%s" %('Non definito', self.ddt_number)

    #Eseguo un controllo sulla cancellazione.
    @api.one
    def unlink(self):
        raise Warning("Non è possibile cancellare movimenti importati")

    #Non è possibile duplicare i record
    @api.one
    @api.model
    def copy(self):
        raise Warning("Non è possibile duplicare i record.")

    #Elaborazione movimenti di ddt con status pronto o in errore
    @api.model
    def process_track(self, selected_row=None):
        #Se le righe selezionate sono valorizzate vuol dire che sono passato dalla vista selezionando le righe da elaborare
        rows_to_process = [self.browse(int(row)) for row in selected_row] if selected_row else self.search([('state','=','ready')])
        #Elaboro solo le righe che sono in stato di pronto.
        for track_obj in rows_to_process:
            #Elaboro solo le righe con lo status uguale a pronto.
            if track_obj.state != 'ready': continue
            #Setto lo status come in processo
            track_obj.state = 'inprocess'
            #Setto i dati di inizio elaborazione
            if track_obj.processing_log:
                track_obj.processing_log += "\nInizio elaborazione movimento :"+datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            else:
                track_obj.processing_log = "\nInizio elaborazione movimento :"+datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            #Elaboro il movimento
            status, __ = self._process_movement(track_obj)
            #Setto lo status di fine elaborazione
            if status:
                track_obj.state = 'done'
            track_obj.processing_log += "\nFine elaborazione movimento :"+datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        pass

    def _process_movement(self, track_obj):
    #Eseguo le mappature dei codici, cercandoli sui relativi modelli
        (status, message) = (True, None)
        try:

            '''
                Partner code.
                Cerco tra i clienti, considerando il codice.
            '''
            partner_code = int(track_obj.partner_code)
            partner = self.env['res.partner'].search([('customer','=',True),('customer_code','=',partner_code)])
            if not partner:
                raise MappingError("Non esiste in anagrafica un cliente con codice: '"+str(partner_code)+"'")
            #il codice del partner deve essere univoco
            if len(partner) > 1:
                raise MappingError("In anagrafica sono presenti due cliente con codice :'"+str(partner_code)+"'")

            ''' Delivery code, deve esistere sul cliente ed essere unico '''
            res_delivery = partner.child_ids.filtered(lambda r: r.type == 'delivery' and r.destination_code == track_obj.delivery_code)
            if not res_delivery:
                raise MappingError("Per il cliente '"+str(partner.name)+"' non esiste un contatto di tipo spedizione con codice destinazione uguale a '"+str(track_obj.delivery_code)+"'")
            if len(res_delivery)>1:
                raise MappingError("Il codice destinazione '"+str(track_obj.delivery_code)+"' è presente più di una volta per il cliente '"+str(partner.name)+"'")

            '''Codice magazzino'''
            store_code = self.env['stock.warehouse'].search([('code','=',track_obj.store_code)])
            if not store_code:
                raise MappingError("Non esiste in anagrafica un magazzino con codice '"+str(track_obj.store_code)+"'")
            if len(store_code)>1:
                raise MappingError("Il codice magazzino '"+str(store_code)+"' è presente su più magazzini in anagrafica")

            '''Codice pagamento'''
            payment_code = self.env['account.payment.term'].search([('payment_code','=',track_obj.payment_code)])
            if not payment_code:
                raise MappingError("Il codice pagamento '"+str(track_obj.payment_code)+"' non è presente")


            '''Se la testata non ha dato errore posso iniziare ad impostare i dati dell'ordine di vendita'''
            sale_order_data = {
                                 'partner_id': partner.id,
                                 'partner_shipping_id': res_delivery.id,
                                 'date_order': track_obj.date,
                                 'warehouse_id': store_code.id,
                                 'payment_term': payment_code.id
                                 }
            # Se c'è il tipo documento (ed è un'elaborazione campioni), lo imposto sull'ordine
            if track_obj.document_type_sample and track_obj.sample_movement:
                sale_order_data.update({'document_type_id': track_obj.document_type_sample.id})


            '''Elaborazione delle righe dei prodotti'''
            status, message, sale_order_lines = self._process_product_row(track_obj.ddt_line)
            if not status:
                raise MappingError(message)

            '''Se non ci sono stati errori'''
            track_obj.status_log=None
            #Aggiungo alla testata dell'ordine le righe
            sale_order_data.update({'order_line':sale_order_lines})
            #Scrivo la riga dell'ordine
            sale_order = self.env['sale.order'].create(sale_order_data)
            if not sale_order:
                raise MappingError("Non è stato possibile creare l'ordine di vendita.")
            track_obj.order_reference=sale_order
            '''
            L'ordine, all'inizio, è in stato di preventivo. Devo confermare automaticamente l'ordine.
            E' possibile confermare l'ordine solo se lo status è draft o sent; altrimenti ci deve essere
            stato qualche errore durante la creazione automatica dell'ordine
            '''
            if sale_order.state not in ('draft','sent'):
                raise MappingError("L'ordine si trova in uno stato diverso da bozza o inviato. Impossibile confermare autmaticamente l'ordine.")
            #Confermo automaticamente l'ordine di vendita
            status = sale_order.action_button_confirm()
            if not status:
                raise MappingError("Non è stato possibile confermare l'ordine creato. Annullare l'ordine manualmente e ritentare l'elaborazione.")
            '''
            Accedo all'ordine di consegna (picking) per trasferirli automaticamente. Se non presente disponibilità la
            forzo in ogni caso. Seguo la seguente logica:
             - Se stato in (confirmed, waiting, patially_avaiable) chiamo il metodo force_assign
             - Se stato in (draft, cancel, done) sollevo l'eccezione
             - Se stato uguale a assigned chiamo il metodo do_enter_transfer_details
            '''
            if not sale_order.picking_ids:
                raise MappingError("Impossibile trovare ordini di consegna associati all'ordine.")
            for delivery_picking in sale_order.picking_ids:
                '''Controllo la disponibilità poi eseguo i controlli'''
                delivery_picking.action_assign()
                '''Eseguo i controlli'''
                if delivery_picking.state == 'assigned':
                    pass #Eseguo l'operazione di trasferimento dopo
                elif delivery_picking.state in ('confirmed', 'waiting', 'partially_available'):
                    status = delivery_picking.force_assign()
                    if not status:
                        raise MappingError("Errore durante la forzatura delle disponibilità.")
                else:
                    raise MappingError("Ordine di consegna in status non congruo all'operazione da svolgere")
                #Ora trasferisco tutto
                if delivery_picking.state != 'assigned':
                    raise MappingError("Problemi riscontrati durante l'operazione di forzatura disponibilità")
                # Passo come tipo operazione batch
                status = delivery_picking.with_context({'submit_type': 'batch'}).do_enter_transfer_details()
                if not status:
                    raise MappingError("Errore durante il trasferimento del picking.")

                '''Alla fine creo il DDT'''
                ddt_from_picking = self.env['ddt.from.pickings']
                ddt_context = {'active_ids':[delivery_picking.id]}
                wiz_ddt = ddt_from_picking.with_context(ddt_context).create({})
                ddt_view = wiz_ddt.create_ddt()
                ddt_id = ddt_view['res_id']
                ddt = self.env['stock.ddt'].browse(ddt_id)
                '''Confermo il ddt, settando numero e data'''
                ddt.name = "%s/%s" % (track_obj.store_code, track_obj.ddt_number)
                ddt.ddt_date = track_obj.date
                ddt.delivery_date = track_obj.date
                ddt.date_done = track_obj.date
                ddt.action_confirm()
                status, message = True, None
        except MappingError as txt:
            status = False
            message = str(txt)
            #Salvo l'informazione sul log di errore
            track_obj.status_log = message
            track_obj.state = 'except'
            return status, message
        except:
            raise

        return status, message

    def _process_product_row(self, ddt_line_obj):
        '''Processa le righe controllandone l'esattezza dei dati
           ritorna:
           - lo status
           - un eventule messaggio di errore
           - la lista di dizionari per l'inserimento delle righe
        '''
        sale_order_lines = []
        (status, message) = (True, None)
        try:
            for line_obj in ddt_line_obj:

                '''Codice Prodotto'''
                if not line_obj.product:
                    raise MappingError("Il codice prodotto è obbligatorio e non è stato specificato")
                product = self.env['product.product'].search([('default_code','=',line_obj.product)])
                if not product:
                    raise MappingError("Non esiste in anagrafica un prodotto con codice :'"+str(line_obj.product)+"'")
                if len(product)>1:
                    raise MappingError("Esiste più di un prodotto con lo stesso codice interno :'"+str(line_obj.product)+"'")

                '''quantità è obbligatoria'''
                if not line_obj.qty:
                    raise MappingError("La quantità di prodotto è obbligatoria e non è stata specificata.")

                '''lotto deve esistere in anagrafica'''
                if not line_obj.lot:
                    raise MappingError("Il lotto del prodotto è obbligatorio e non è stato specificato.")
                #Ricerco il lotto in anagrafica
                lot_id = self.env['stock.production.lot'].search([('product_id','=',product.id),('name','=',line_obj.lot)])
                if not lot_id:
                    msg_error = "Non esiste in anagrafica un lotto '%s' collegato al prodotto '%s'" % (line_obj.lot, product.name)
                    raise MappingError(msg_error)

                '''Se non ci sono stati errori'''
                line_obj.error=False
                sale_order_line = {
                                   'product_id':product.id,
                                   'product_uom_qty':line_obj.qty,
                                   'free': line_obj.free,
                                   'lot_id': lot_id.id
                                   }
                sale_order_lines.append((0, 0, sale_order_line))
            (status, message) = (True, None)
        except MappingError as txt:
            line_obj.error = True
            status = False
            message = str(txt)
        except:
            raise
        return status, message, sale_order_lines




class track_import_ddt_line(models.Model):

    _name = "track.import.ddt.line"
    _description = "DDT Line Import Track"

    product = fields.Char(string="Product Code", required=True, copy=False)
    qty = fields.Float(string="Quantity", digits_compute=dp.get_precision('Product UoS'), required=True, readonly=False)
    price = fields.Float('Unit Price', required=False, digits_compute= dp.get_precision('Product Price'), readonly=False)
    gross_price = fields.Float('Gross Price', digits_compute= dp.get_precision('Product Price'), readonly=False)
    tax = fields.Char('Tax code',readonly=False)
    discount =  fields.Float('Discount (%)', digits_compute= dp.get_precision('Discount'), readonly=False)
    discount2 =  fields.Float('Discount 2(%)', digits_compute= dp.get_precision('Discount'), readonly=False)
    discount3 =  fields.Float('Discount 3(%)', digits_compute= dp.get_precision('Discount'), readonly=False)
    discount4 =  fields.Float('Discount 4(%)', digits_compute= dp.get_precision('Discount'), readonly=False)
    discount5 =  fields.Float('Discount 5(%)', digits_compute= dp.get_precision('Discount'), readonly=False)
    discount_total = fields.Float('Global discount', digits_compute= dp.get_precision('Discount'), readonly=False)
    free = fields.Selection(selection=[('gift', 'Gift on Amount Total'),
                                       ('base_gift', 'Gift on Amount Untaxed')],
                                       string='Free')
    store_code = fields.Char(string="Store code", readonly=False, copy=False, select=True)
    lot = fields.Char(string='Serial Number', readonly=False, required=True)
    expiration_date = fields.Date(string="Expiration date", readonly=False, copy=False, select=True, required=True)
    ddt_id = fields.Many2one(comodel_name='track.import.ddt', string='DDT', ondelete='cascade', readonly=True, copy=True)
    error = fields.Boolean(string="In Error",help="Row in error during process", default=False, readonly=True, copy=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
