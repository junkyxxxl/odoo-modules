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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError, Warning

class account_invoice_commission(models.Model):

    _inherit = 'account.invoice'

    ''' {FORZA RICALCOLO DELLE PROVVIGIONI}
    Questa funzione, collegata ad un pulsante, forza il ricalcolo delle provvigioni relative alle righe dell'intera fattura.
    Il ricalcolo avviene se e soltanto se la fattura non ha già generato delle righe di provvigione che sono state a loro volta già fatturate o addirittura pagate.
    Il ricalcolo viene effettuato in base ai parametri correnti (ordine di priorità, percentuali di provvigione relative ad agente,prodotto,categoria,etc.).
    Al termine del ricalcolo, qualora la fattura avesse già generato delle righe di provvigione e qualora il ricalcolo abbia restituito dei valori differenti da quelli calcolati
    in precedenza, le righe di provvigione precedenti vengono rimosse ed al loro posto ne vengono create di nuove coerenti col nuovo risultato. 
    '''
    @api.multi
    def force_commission_recompute(self):

        company_obj = self.env['res.company']
        commission_obj = self.env['account.commission.line']
        
        inv_line_ids = self.invoice_line
        invoice = self
        any_change = False

        if commission_obj.search([('invoice_src_id','=',invoice.id),('state','in',['invoiced','paid'])]):
            raise Warning('Some Commission Line for this Invoice are already invoiced or paid')
        
        old_commission_ids = commission_obj.search([('invoice_src_id','=',invoice.id)])
        
        for line_id in inv_line_ids:
            if invoice.type in ['out_invoice','out_refund'] and invoice.partner_id and invoice.user_id and invoice.user_id.partner_id.salesagent:
                comm_perc = 0.0                    
                if line_id.product_id and not line_id.product_id.no_commission and not line_id.product_id.categ_id.no_commission:
                    
                    salesagent_id = invoice.user_id.partner_id
                    partner = invoice.partner_id
                    partner_id = partner.id
                    company = invoice.company_id
                    product = line_id.product_id                                  

                    if salesagent_id.is_overriding:
                        for comm_line in salesagent_id.custom_commission_line_ids:
                            if not comm_line.partner_id or comm_line.partner_id.id == partner_id:
                                if not comm_line.category_id or comm_line.category_id.id == product.categ_id.id:
                                    if not comm_line.template_id or comm_line.template_id.id == product.product_tmpl_id.id:
                                        if not comm_line.product_id or comm_line.product_id.id == product.id:
                                            comm_perc = comm_line.commission_perc
                                            break       
                    
                    if comm_perc == 0.0:                                
                        if company.commission_priority1:
                            comm_perc = company_obj.get_commission_perc(company.commission_priority1, product, partner_id, salesagent_id)
                        if not comm_perc and company.commission_priority2:
                            comm_perc = company_obj.get_commission_perc(company.commission_priority2, product, partner_id, salesagent_id)                
                        if not comm_perc and company.commission_priority3:
                            comm_perc = company_obj.get_commission_perc(company.commission_priority3, product, partner_id, salesagent_id)                
                        if not comm_perc and company.commission_priority4:   
                            comm_perc = company_obj.get_commission_perc(company.commission_priority4, product, partner_id, salesagent_id)  
                            
                if comm_perc != line_id.commission_perc:
                    line_id.write({'commission_perc':comm_perc})
                    any_change = True
                        
            
        if any_change and invoice.state != 'draft':
            for old_commission in old_commission_ids:
                old_commission.unlink()
            invoice.create_commission_line()
            
        return True          

    ''' {ONCHANGE SUL CAMPO 'partner_id'}
    Quando cambia il 'partner_id' della fattura, viene impostato come commerciale ('user_id') di default l'utente legato all'agente impostato sul partner stesso.
    '''
    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice_commission,self).onchange_partner_id(type, partner_id, date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        if res and partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner and partner.salesagent_id:
                if partner.salesagent_id.user_id:
                    user = partner.salesagent_id.user_id.id
                elif partner.salesagent_id.user_ids:
                    user = partner.salesagent_id.user_ids.ids[0]
                else:
                    user = self._uid
                if  user: 
                    if 'value' in res:
                        res['value'].update({'user_id':user})
                    else:
                        res['value'] = {'user_id':partner.salesagent_id.user_id.id}
        return res

    '''
    Quando la fattura viene annullata, vengono rimosse tutte le righe di provvigione ad essa associate. Qualora tali righe di provvigione siano già state fatturate o pagate,
    ovviamente, l'operazione non è possibile (viene restituito un warning direttamente dal metodo unlink della riga di provvigione).
    '''
    @api.cr_uid_ids_context
    def action_cancel(self, cr, uid, ids, context=None):
        res = super(account_invoice_commission, self).action_cancel(cr, uid, ids, context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            commission_obj = self.pool.get('account.commission.line')
            commission_ids = commission_obj.search(cr, uid, [('invoice_src_id','=',invoice.id)], context=context)
            commission_obj.unlink(cr, uid, commission_ids, context=context)
        return res
    
    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.invoice_line:
            return {'warning':{'title': _('Warning!'), 'message': _('This invoice already contains some lines, commission on those lines will not be automatically recomputed!')} }
    
    @api.multi
    def create_commission_line(self):
        for inv in self:
            if inv.user_id and inv.user_id.partner_id:
                for line in inv.invoice_line:
                    if line.commission_perc and line.commission_amount:
                        commission_vals = line.prepare_commission_line()
                        for vals in commission_vals:
                            comm = self.env['account.commission.line'].create(vals)
        return True

class account_invoice_line_commission(models.Model):

    _inherit = 'account.invoice.line'

    commission_perc = fields.Float(string="Commission [%]", digits_compute= dp.get_precision('Account'),)
    commission_amount = fields.Float(compute="_compute_commission_amount", store=True, string="Commission", digits_compute= dp.get_precision('Account'),)    
    
    @api.one
    @api.depends('price_subtotal', 'commission_perc')
    def _compute_commission_amount(self):
        self.commission_amount = self.get_base_amount() * self.commission_perc / 100.0


    '''
    Nella onchange del 'product_id' viene calcolata la provvigione relativa alla riga. Si verifica dapprima se l'agente ha delle regole speciali applicabili alla riga,
    in caso contrario si calcola la provvigione seguendo le regole di priorità definite a livello di azienda.
    
    TO DO: Per migliorare il comportamento di questa funzione e di tutte quelle ad essa collegate, sarebbe opportuno estrapolare la parte che esegue effettivamente il calcolo
    della provvigione, in un metodo separato, facilmente estendibile e richiamabile.
    '''       
    @api.multi
    def product_id_change(self, product_id, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, company_id=None):    
        res = super(account_invoice_line_commission,self).product_id_change(product_id, uom_id, qty=qty, name=name, type=type, partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id, company_id=company_id)
           
        if res and res['value'] and partner_id and product_id and type in ['out_invoice','out_refund'] and 'user_id' in self._context and self._context['user_id'] and self.pool.get('res.users').browse(self._cr, self._uid, self._context['user_id'], context=self._context).partner_id.salesagent:
            salesagent_id = self.pool.get('res.users').browse(self._cr, self._uid, self._context['user_id'], context=self._context).partner_id
            comm_perc = 0.0            
            
            if product_id and not self.env['product.product'].browse(product_id).no_commission and not self.env['product.product'].browse(product_id).categ_id.no_commission:
                cmp_id = company_id or self._context.get('company_id',False) or self.env['res.users'].browse(self._uid).company_id.id
                company_obj = self.env['res.company']
                company = company_obj.browse(cmp_id)
                product = self.pool.get('product.product').browse(self._cr, self._uid, product_id, context=self._context)

                if salesagent_id.is_overriding:
                    for comm_line in salesagent_id.custom_commission_line_ids:
                        if not comm_line.partner_id or comm_line.partner_id.id == partner_id:
                            if not comm_line.category_id or comm_line.category_id.id == product.categ_id.id:
                                if not comm_line.template_id or comm_line.template_id.id == product.product_tmpl_id.id:
                                    if not comm_line.product_id or comm_line.product_id.id == product.id:
                                        comm_perc = comm_line.commission_perc
                                        break

                if comm_perc == 0.0:                                
                    if company.commission_priority1:
                        comm_perc = company_obj.get_commission_perc(company.commission_priority1, product, partner_id, salesagent_id)
                    if not comm_perc and company.commission_priority2:
                        comm_perc = company_obj.get_commission_perc(company.commission_priority2, product, partner_id, salesagent_id)                
                    if not comm_perc and company.commission_priority3:
                        comm_perc = company_obj.get_commission_perc(company.commission_priority3, product, partner_id, salesagent_id)                
                    if not comm_perc and company.commission_priority4:   
                        comm_perc = company_obj.get_commission_perc(company.commission_priority4, product, partner_id, salesagent_id)     
            res['value']['commission_perc'] = comm_perc           
        return res
    
    '''
    Questa funzione restituisce un dizionario da passare come parametro nella creazione delle righe di fattura.
    '''
    @api.model
    def prepare_commission_line(self):
        res = []
        base_amount = self.get_base_amount()
        commission_amount = base_amount * self.commission_perc / 100.0
        if self.invoice_id.type == 'out_refund':
            commission_amount = -commission_amount
        if commission_amount:
            salesagent = self.invoice_id.user_id.partner_id
            dict1 = {'line_src_id':self.id, 'salesagent_id':salesagent.id, 'commission_mode': salesagent.commission_mode, 'base_untaxed':base_amount, 'amount_commission': commission_amount, 'state':'computed'}
            if salesagent.commission_mode == 'invoiced':
                dict1.update({'state':'matured'})

            if salesagent.salesagent_parent_id and salesagent.salesagent_parent_commission_perc:
                parent_commission_amount = base_amount * salesagent.salesagent_parent_commission_perc / 100.0
                if self.invoice_id.type == 'out_refund':
                    parent_commission_amount = -parent_commission_amount                
                dict2 = {'line_src_id':self.id, 'salesagent_id':salesagent.salesagent_parent_id.id, 'commission_mode': salesagent.salesagent_parent_id.commission_mode, 'base_untaxed':base_amount, 'amount_commission': parent_commission_amount, 'state':'computed'}
                if salesagent.salesagent_parent_id.commission_mode == 'invoiced':
                    dict2.update({'state':'matured'})                
                res.append(dict1)
                res.append(dict2)
            else:
                res.append(dict1)                                
        return res        
    
    '''
    Questo metodo get è stato implementato poiché, sebbene in situazioni normali la base su cui viene calcolata la provvigione è proprio l'imponibile totale, potrebbero
    esistere casi in cui ciò non sia vero (ad esempio, qualora fossero presenti omaggi/sconti a piede o altre situazioni che non intervengono direttamente sul campo 
    'price_subtotal' della riga. In tal caso, avendo un metodo selettore esterno, è facilmente possibile estenderlo per prendere in considerazione il nuovo caso.
    '''
    @api.model
    def get_base_amount(self):
        return self.price_subtotal               