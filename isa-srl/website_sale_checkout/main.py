# -*- coding: utf-8 -*-
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.web.controllers.main import Session
from openerp import http
from openerp.addons.web.http import request


class website_sale(website_sale):

    def __init__(self):
        self.mandatory_billing_fields.extend(["is_company"])
        self.optional_billing_fields.extend(["person_surname", "fiscalcode", "individual"])

    def checkout_form_save(self, checkout):
        if checkout.get('is_company', False) == '2':
            checkout.update({'is_company': False})
            checkout.update({'individual': True})
            checkout.update({'person_name': checkout.get('name', None)})
        elif checkout.get('is_company', False):
            checkout.update({'is_company': True})
            checkout.update({'individual': False})
        return super(website_sale, self).checkout_form_save(checkout)

    def checkout_form_validate(self, data):
        # Reperisco se si tratta di azienda o cliente privato per rendere obbligatori i campi
        # Società
        customer_type = data.get('is_company', False)
        if customer_type and customer_type == '1':
            # Se società, obbligatori street e vat
            self.adding_to_mandatory('vat')
            self.adding_to_mandatory('street')
            # facoltativi fiscalcode, person_surname
            self.adding_to_optional('fiscalcode')
            self.adding_to_optional('person_surname')
        # Cliente privato
        elif customer_type and customer_type == '2':
            # Se privato, obbligatori fiscalcode e person_surname
            self.adding_to_mandatory('fiscalcode')
            self.adding_to_mandatory('person_surname')
            # Facoltativi vat e street
            self.adding_to_optional('vat')
            self.adding_to_optional('street')
        error = super(website_sale, self).checkout_form_validate(data)
        # Controllo sul codice a fiscale
        if customer_type and customer_type == '2':
            fiscalcode = data.get('fiscalcode', False)
            if fiscalcode and len(fiscalcode) != 16:
                error['fiscalcode'] = 'error'
        return error

    def adding_to_mandatory(self, field_name):
        # Aggiungo il campo a quelli obbligatori, se non presente
        if field_name not in self.mandatory_billing_fields:
            self.mandatory_billing_fields.append(field_name)
        # Rimuovo il campo da quelli facoltativi se presente
        if field_name in self.optional_billing_fields:
            self.optional_billing_fields.remove(field_name)
        return None

    def adding_to_optional(self, field_name):
        # Aggiungo il campo a quelli facoltativi, se non presente
        if field_name not in self.optional_billing_fields:
            self.optional_billing_fields.append(field_name)
        # Rimuovo il campo da quelli obbligatori se presente
        if field_name in self.mandatory_billing_fields:
            self.mandatory_billing_fields.remove(field_name)
        return None


# Classe sessione: Cancella l'ordine se in stato draft
class Session(Session):

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        # Al logout dell'utente, cancello l'ordine di vendita creato se in
        # stato di bozza preventivo.
        sale_order_id = request.session.get('sale_order_id')
        if not sale_order_id:
            return super(Session, self).logout(redirect)
        sale_order = request.env['sale.order'].sudo().browse(sale_order_id)
        if sale_order.state == 'draft':
            sale_order.unlink()
        return super(Session, self).logout(redirect)
