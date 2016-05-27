# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError

#Rispetto ai modelli normali, quando si crea un Wizard, bisogna specificare invece che (model.Models) -> (models.TransientModel)
#e quando ho a che fare con l'email, bisogna ereditare "mail.thread" che si occupa della gestione di invio delle email.
class invoice_mass(models.TransientModel):

    _name="mass.mail.invoice"
    _inherit = ['mail.thread']
    
    @api.model
    def _get_template_id(self):
        temp_id = self.env['email.template'].search([('name','=','Invoice - Send by Email')])
        if temp_id:
            return temp_id[0]
        return 
    
    
    template_id = fields.Many2one('email.template', string="Usa template", default=_get_template_id, required=True, select=True)


    @api.multi
    def send_button(self):
        #Con self.env.context.get('active_ids') vado a prendere tutti gli id delle fatture selezionate
        invoice_ids = self.env.context.get('active_ids')
        
        #Dagli id, vado a prendere gli oggetti delle fatture
        invoices = self.env['account.invoice'].browse(invoice_ids)
        
        #Ora filto gli oggetti delle fatture che non sono in stato "Bozza":
        invoices_not_draft = invoices.filtered(lambda r: r.state != "draft")
        
        #Una volta presi gli oggetti, devo reperire i partner e per evitare i partner ripetuti, utilizzo 
        #la funzione di odoo chiamata "mapped" che permette di scartare i partner doppi
        partners = invoices_not_draft.mapped('partner_id')
        
        #Ora sui clienti eseguo un controllo in cui verifico se l'email esiste o no
        for partner in partners:
            if not partner.email and partner.notify_email == 'always':
                raise Warning("Per il cliente " +str(partner.name) + " non è stata configurata l’email. Specificare un email e riprovare")

        # Eseguo un ciclo sugli id del invoces_not_draft:
        for invoice_not_draft in invoices_not_draft:
            #L'invio delle mail deve filtrare i partner che hanno notify_email settato ad always
            notify_email = invoice_not_draft.partner_id.notify_email
            if notify_email == 'always':

                #Setto il context con gli ids
                compose_ctx = dict(self.env.context,
                                   active_ids=invoice_not_draft.id)
                #con la "create" scrivo in mail.compose.message, i seguenti parametri che servono per l'email
                #Nota: il body relativo al template è ancora vuoto (viene riempito in base all'onchange del template)
                compose_id = self.env['mail.compose.message'].with_context(compose_ctx).create({
                             'model': 'account.invoice',
                             'composition_mode': 'comment',
                             'template_id': self.template_id.id,
                             'post': False,
                             'notify': False,
                             'mark_so_as_sent': True,
                             'res_id': invoice_not_draft.id
                            })
                #con 'comment' vado a prendere i possibili attachments(allegati) contenuti nella fattura selezionata
                #inoltre in base all'onchange del template, cambia il body che è contenuto in values
                values = compose_id.with_context(compose_ctx).onchange_template_id(
                                                self.template_id.id, 'comment', 'account.invoice', invoice_not_draft.id)['value']
                #Controllo se effettivamente esistono gli allegati alla fattura e i relativi partner_ids
                for key in ['attachment_ids', 'partner_ids', '']:
                        if values.get(key):
                            values[key] = [(6, 0, values[key])]
                #Aggiorno la tabella mail.compose.message con la "Write", aggiornando il body e il partner_id
                compose_id.with_context(compose_ctx).write(values)
                #Richiamo il metodo di invio email
                compose_id.with_context(compose_ctx).send_mail()

        
        
        
        
        
        
     
        
        
        
        
        
