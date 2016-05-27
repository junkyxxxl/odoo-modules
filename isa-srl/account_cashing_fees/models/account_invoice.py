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

from openerp.osv import fields, orm
from openerp import osv
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning


class account_invoice_cashing_fees(orm.Model):

    _inherit = 'account.invoice'

    def _decrease_riba_count(self, cr, uid, ids, payment_term, date_invoice, partner_id, previous_riba_count, context=None):
        mov_line_obj = self.pool.get('account.move.line')
        riba_count = previous_riba_count
        previous_maturities = []
        
        args = [('partner_id','=',partner_id),('state','=','draft')]
        if ids:
            args.append(('id','not in', ids))
        draft_invoices = self.search(cr, uid, args, context=context)
        
        for invoice_id in draft_invoices:
            t_inv = self.browse(cr, uid, invoice_id, context=context)
            t_paym_lines = self.pool.get('account.payment.term').compute(cr, uid, t_inv.payment_term.id, 10000, t_inv.date_invoice, context=context)
            for t_line in t_paym_lines:
                if t_line[2] == 'D' and t_line[0] not in previous_maturities:
                    previous_maturities.append(t_line[0])
        
        payment_lines = self.pool.get('account.payment.term').compute(cr, uid, payment_term, 10000, date_invoice, context=context)
        for line in payment_lines:
            if line[2] == 'D':
                t_ids = mov_line_obj.search(cr, uid, [('partner_id','=',partner_id),('date_maturity','=',line[0]),('payment_type_move_line','=','D')], context=context)
                if t_ids:
                    riba_count -= 1
                elif line[0] in previous_maturities:
                    riba_count -= 1
                    
        return riba_count

    def _get_tax_id(self, cr, uid, product, company_id, fpos, context=None):
        if uid == SUPERUSER_ID:
            taxes = product.taxes_id.filtered(lambda r: r.company_id.id == company_id)
        else:
            taxes = product.taxes_id
        tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes) 
        return tax_id       

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        # Verifico il tipo di fattura    
        invoice_type = context.get('type', False)
        if not invoice_type and 'type' in vals:
            invoice_type = vals['type']

        ''' QUALORA IL TIPO DELLA FATTURA SIA 'out_invoice' (VENDITA) E SIA STATO IMPOSTATO UN TERMINE DI PAGAMENTO, 
            VENGONO CALCOLATE LE SPESE D'INCASSO '''
                
        if invoice_type and invoice_type == 'out_invoice' and 'payment_term' in vals and vals['payment_term']:
            
            partner_id = vals['partner_id']
            partner_data = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)            
            company_id = vals.get('company_id',False)
            if not company_id:
                company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
            payment_term = vals['payment_term']
            
            # Ricavo la data fattura            
            if 'date_invoice' in vals:
                date_invoice = vals['date_invoice'] 
            else:
                date_invoice = False

            # Ricavo la posizione fiscale                
            if 'fiscal_position' in vals and vals['fiscal_position']:
                fpos = self.pool.get('account.fiscal.position').browse(cr, uid, vals['fiscal_position'])
            else:
                fpos = partner_data.property_account_position or False
            
            ''' VERIFICO CHE IL PARTNER DEBBA PAGARE LE SPESE D'INCASSO E RICAVO IL PRODOTTO ASSOCIATO ALLE 
                SPESE D'INCASSO DALLA CONFIGURAZIONE DELL'AZIENDA; QUALORA TALE PRODOTTO ESISTA ED IL PARTNER 
                DEBBA PAGARE LE SPESE D'INCASSO, PROCEDO '''
            
            no_cashing_fees = partner_data.no_cashing_fees
            cashing_fees_default_product = self.pool.get('res.company').browse(cr, uid, company_id, context=context).cashing_fees_default_product
            if not no_cashing_fees and cashing_fees_default_product:
            
                mov_line_obj = self.pool.get('account.move.line')
                riba_count = 0

                # CALCOLO QUANTE SCADENZE CON TIPO DI PAGAMENTO RI.BA. VERREBBERO GENERATE DALLA FATTURA                                
                paym_data = self.pool.get('account.payment.term').browse(cr, uid, payment_term, context=context)
                for line in paym_data.line_ids:
                    if line.payment_type == 'D':
                        riba_count += 1

                ''' SOTTRAGGO IL NUMERO DI SCADENZE, CON TIPO DI PAGAMENTO RI.BA., GIÀ EMESSE PER QUEL CLIENTE 
                    NELLE STESSE DATE DELLE SCADENZE GENERATE DALLA FATTURA IN CORSO.
                    SOLO SE IL CLIENTE PREVEDE IL RAGGRUPPAMENTO DELLE RI.BA.'''
                
                if partner_data.group_riba:                        
                    riba_count = self._decrease_riba_count(cr, uid, False, payment_term, date_invoice, partner_id, riba_count, context=context)

                # SE VANNO EMESSE SPESE D'INCASSO, CREO UNA NUOVA RIGA DI FATTURA E LA AGGIUNGO A VALS                                
                if riba_count > 0:
                    
                    product_id = cashing_fees_default_product.id
                    name = cashing_fees_default_product.name
                    
                    # Calcolo prezzo
                    pricelist = partner_data.property_product_pricelist
                    if pricelist:
                        price_unit = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist.id], cashing_fees_default_product.id, riba_count, partner_data.id, context=context)[pricelist.id]                    
                    else:
                        price_unit = cashing_fees_default_product.lst_price
                    
                    # Calcolo tasse                    
                    tax_id = self._get_tax_id(cr, uid, cashing_fees_default_product, company_id, fpos, context=context)
                    
                    # Calcolo il conto
                    if fpos:
                        account = cashing_fees_default_product.property_account_income or cashing_fees_default_product.categ_id.property_account_income_categ
                        account = fpos.map_account(account)
                    else:
                        raise Warning('Attenzione - impossibile proseguire:\n Specificare la posizione fiscale per il cliente.')
                    if account:
                        account_id = account.id
                    else:
                        account_id = False
                        
                    # Calcolo l'unità di misura
                    uos_id = cashing_fees_default_product.uom_id.id

                    # Creo la riga
                    cashing_fees_line = {
                                          'uos_id': uos_id,
                                          'product_id': product_id,
                                          'price_unit': price_unit,
                                          'account_id': account_id,
                                          'name': name,
                                          'invoice_line_tax_id': [[6,False,tax_id]],
                                          'quantity': riba_count,
                                       }

                    # Aggiungo la riga ai valori da passare alla super                    
                    if 'invoice_line' in vals:
                        vals['invoice_line'].append([0,False,cashing_fees_line])
                    else:
                        vals['invoice_line'] = [[0,False,cashing_fees_line]]
                                    
            
        return super(account_invoice_cashing_fees,self).create(cr, uid, vals, context=context)
        
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids,list) and len(ids) > 1:
            return super(account_invoice_cashing_fees,self).write(cr, uid, ids, vals, context=context)
        curr_inv = self.browse(cr, uid, ids, context=context)
        # Verifico il tipo di fattura        
        invoice_type = context.get('type', False)
        if not invoice_type and 'type' in vals:
            invoice_type = vals['type']
        else:
            invoice_type = curr_inv.type
        
        # Ricavo i termini di pagamento        
        if 'payment_term' in vals and vals['payment_term']:
            payment_term = vals['payment_term']
        elif curr_inv.payment_term:
            payment_term = curr_inv.payment_term.id
        else: payment_term = False             

        ''' QUALORA LA WRITE ABBIA CAMBIATO UNO QUALSIASI TRA: TERMINI DI PAGAMENTO, DATA FATTURA O PARTNER, O QUALORA LA FATTURA NON SIA PIU' DI TIPO
            VENDITA, VENGONO RIMOSSE LE RIGHE RELATIVE ALLE SPESE D'INCASSO (SARANNO, EVENTUALMENTE, RICALCOLATE) '''
            
        if (invoice_type and invoice_type != 'out_invoice') or 'payment_term' in vals or 'date_invoice' in vals or 'partner_id' in vals:            
            if 'invoice_line' in vals:
                line_obj = self.pool.get('account.invoice.line')
                for line in vals['invoice_line']:
                    if line[0] in [1,4]:
                        tmp = line_obj.browse(cr, uid, line[1], context=context)
                        if tmp.product_id and tmp.product_id.is_cashing_fees:
                            line[0] = 2
                            line[2] = False
            
            else:
                new_lines = []
                for line in curr_inv.invoice_line:
                    if line.product_id and line.product_id.is_cashing_fees:
                        new_lines.append([2,line.id,False])
                if new_lines:
                    vals['invoice_line'] = new_lines        

        ''' QUALORA IL TIPO DELLA FATTURA SIA 'out_invoice' (VENDITA) E SIA STATO CAMBIATO UNO QUALSIASI DEI 
            CAMPI TRA TERMINI DI PAGAMENTO, DATA FATTURA O PARTNER, VENGONO RICALCOLATE LE SPESE D'INCASSO '''
            
        if invoice_type and invoice_type == 'out_invoice' and payment_term and ('date_invoice' in vals or 'partner_id' in vals or 'payment_term' in vals):
            
            # Ricavo il partner            
            if 'partner_id' in vals:
                partner_id = vals['partner_id']
            else:
                partner_id = curr_inv.partner_id.id

            partner_data = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)

            # Ricavo l'azienda
            if 'company_id' in vals:
                company_id = vals['company_id']
            else:
                company_id = curr_inv.company_id.id
            
            # Ricavo la data fattura
            if 'date_invoice' in vals:
                date_invoice = vals['date_invoice'] 
            else:
                date_invoice = curr_inv.date_invoice
            
            # Ricavo la posizione fiscale
            if 'fiscal_position' in vals:
                if vals['fiscal_position']:
                    fpos = self.pool.get('account.fiscal.position').browse(cr, uid, vals['fiscal_position'])
                else:
                    fpos = partner_data.property_account_position or False
            else:
                if curr_inv.fiscal_position:
                    fpos = curr_inv.fiscal_position
                else:
                    fpos = partner_data.property_account_position or False                    
            
            ''' VERIFICO CHE IL PARTNER DEBBA PAGARE LE SPESE D'INCASSO E RICAVO IL PRODOTTO ASSOCIATO ALLE 
                SPESE D'INCASSO DALLA CONFIGURAZIONE DELL'AZIENDA; QUALORA TALE PRODOTTO ESISTA ED IL PARTNER 
                DEBBA PAGARE LE SPESE D'INCASSO, PROCEDO '''
            
            no_cashing_fees = partner_data.no_cashing_fees
            cashing_fees_default_product = self.pool.get('res.company').browse(cr, uid, company_id, context=context).cashing_fees_default_product
            if not no_cashing_fees and cashing_fees_default_product:
            
                mov_line_obj = self.pool.get('account.move.line')
                riba_count = 0
                
                # CALCOLO QUANTE SCADENZE CON TIPO DI PAGAMENTO RI.BA. VERREBBERO GENERATE DALLA FATTURA                
                paym_data = self.pool.get('account.payment.term').browse(cr, uid, payment_term, context=context)
                for line in paym_data.line_ids:
                    if line.payment_type == 'D':
                        riba_count += 1
                
                ''' SOTTRAGGO IL NUMERO DI SCADENZE, CON TIPO DI PAGAMENTO RI.BA., GIÀ EMESSE PER QUEL CLIENTE 
                    NELLE STESSE DATE DELLE SCADENZE GENERATE DALLA FATTURA IN CORSO '''
                
                if partner_data.group_riba:
                    riba_count = self._decrease_riba_count(cr, uid, ids, payment_term, date_invoice, partner_id, riba_count, context=context)
                
                # SE VANNO EMESSE SPESE D'INCASSO, CREO UNA NUOVA RIGA DI FATTURA E LA AGGIUNGO A VALS                
                if riba_count > 0:
                    
                    product_id = cashing_fees_default_product.id
                    name = cashing_fees_default_product.name
                    
                    # Calcolo prezzo
                    pricelist = partner_data.property_product_pricelist
                    if pricelist:
                        price_unit = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist.id], cashing_fees_default_product.id, riba_count, partner_data.id, context=context)[pricelist.id]                    
                    else:
                        price_unit = cashing_fees_default_product.lst_price
                    
                    # Calcolo tasse
                    tax_id = self._get_tax_id(cr, uid, cashing_fees_default_product, company_id, fpos, context=context)
                    
                    # Calcolo il conto
                    account = None
                    if fpos:
                        account = cashing_fees_default_product.property_account_income or cashing_fees_default_product.categ_id.property_account_income_categ
                        account = fpos.map_account(account)
                    if account:
                        account_id = account.id
                    else:
                        account_id = False
                        
                    # Calcolo l'unità di misura
                    uos_id = cashing_fees_default_product.uom_id.id
                    
                    # Creo la riga
                    cashing_fees_line = {
                                          'uos_id': uos_id,
                                          'product_id': product_id,
                                          'price_unit': price_unit,
                                          'account_id': account_id,
                                          'name': name,
                                          'invoice_line_tax_id': [[6,False,tax_id]],
                                          'quantity': riba_count,
                                       }
                    
                    # Aggiungo la riga ai valori da passare alla super
                    if 'invoice_line' in vals:
                        vals['invoice_line'].append([0,False,cashing_fees_line])
                    else:
                        vals['invoice_line'] = [[0,False,cashing_fees_line]]
                                    
        return super(account_invoice_cashing_fees,self).write(cr, uid, ids, vals, context=context)