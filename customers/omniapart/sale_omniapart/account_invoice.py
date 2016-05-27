# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp import models, api, fields


class account_invoice(models.Model):
    _inherit = "account.invoice"

    def onchange_registration_date_customer(self, cr, uid, ids, date_invoice, registration_date, context=None):
        value = {}
        if(registration_date):
            value.update({'date_invoice':registration_date})         
        return {'value': value,}

    @api.multi
    def onchange_company_id(self, company_id, part_id, type, invoice_line, currency_id):
        res = super(account_invoice,self).onchange_company_id(company_id, part_id, type, invoice_line, currency_id)
        if 'value' in res and res['value'] and 'journal_id' in res['value'] and res['value']['journal_id']:
            journal_id = self._default_journal()
            if journal_id:
                res['value'].update({'journal_id':journal_id.id})

    def unlink(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get('sale.order')
        sale_ids = []
        
        for id in ids:
            tmp_sale_ids = sale_obj.search(cr, uid, [('name','=',self.browse(cr,uid,id,context=context).origin)], context=context)
            sale_ids += [sale_id for sale_id in tmp_sale_ids]                
        self.write(cr, uid, ids, {'internal_number':None},context=context)
        res = super(account_invoice, self).unlink(cr, uid, ids, context=context)
        
        for id in sale_ids:
            sale_obj.write(cr, uid, id, {'state':'manual'},context=context)

        return res
    
class account_move(models.Model):
    _inherit = 'account.move'
    
    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context = {}
        if 'invoice' in context and context['invoice']:
            if context['invoice'].supplier_invoice_number:
                vals.update({'ref':context['invoice'].supplier_invoice_number})
        return super(account_move,self).create(cr, uid, vals, context=context)    