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

from openerp.osv import fields, osv

class sale_advance_payment_inv_omniapart(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    _columns = {
                'journal_id': fields.many2one('account.journal', 'Sale Journal',),
    }    

    def _get_journal_id(self,cr,uid,context=None):
        jour_obj = self.pool.get('account.journal')
        cmp_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        jour_id = cmp_id.sale_journal_default and cmp_id.sale_journal_default.id
        if jour_id:
            return jour_id
        return None

    def _get_advance_payment_method(self,cr,uid,context=None):
        sale_obj = self.pool.get('sale.order')
        sale_ids = context.get('active_ids', [])
        if sale_ids:
            sale_id = sale_ids[0]
            if sale_obj.browse(cr,uid,sale_id).part_payment:
                return 'fixed'
        return 'all'

    def _get_amount(self,cr,uid,context=None):
        sale_obj = self.pool.get('sale.order')
        sale_ids = context.get('active_ids', [])
        if sale_ids:
            sale_id = sale_ids[0]
            if sale_obj.browse(cr,uid,sale_id).part_payment_amount:
                return sale_obj.browse(cr,uid,sale_id).part_payment_amount
        return 0.0
    
    def onchange_method(self, cr, uid, ids, advance_payment_method, product_id, context=None):
        if advance_payment_method == 'fixed' and not product_id:
            return {'value': {'product_id':False }}
        # IN QUESTO MODO STIAMO DISABILITANDO LA PARTE DI ONCHANGE CHE TIRA FUORI IL PREZZO DEL PRODOTTO QUANDO SELEZIONATO
        if advance_payment_method == 'fixed' and product_id:
            return 
        return super(sale_advance_payment_inv_omniapart,self).onchange_method(cr, uid, ids, advance_payment_method, product_id, context=context)            
    
    _defaults = {
        'advance_payment_method': _get_advance_payment_method,
        'amount': _get_amount,
        'journal_id': _get_journal_id,
    }

    def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)        
        res = super(sale_advance_payment_inv_omniapart, self)._prepare_advance_invoice_vals(cr, uid, ids, context=context)
        if res and wizard and wizard.journal_id:
            for i in range(0,len(res)):
                if len(res[i]) == 2 and isinstance(res[i][1],dict):
                    res[i][1].update({'journal_id': wizard.journal_id.id})
        return res

    def create_invoices(self, cr, uid, ids, context=None):
        """ create invoices for the active sales orders """
        wizard = self.browse(cr, uid, ids[0], context)
        context.update({'wiz_journal_id':wizard.journal_id.id})
        return super(sale_advance_payment_inv_omniapart, self).create_invoices(cr, uid, ids, context=context)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
