# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    All Rights Reserved
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

import openerp.exceptions
from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_invoice_cancel_management(orm.Model):
    _inherit = "account.invoice"

    def onchange_internal_number(self, cr, uid, ids, internal_number_id, context=None):
        values = {}
        if internal_number_id:
            account_cancel_obj = self.pool.get('account.invoice.cancel.isa')
            account_cancel_data = account_cancel_obj.browse(cr, uid, internal_number_id, context)
            if account_cancel_data and account_cancel_data.protocol_number:
                values.update({'force_protocol_number': int(account_cancel_data.protocol_number), })
        return {'value': values}

    _columns = {
        'internal_number': fields.char('Invoice Number',
                                    size=32,
                                    readonly=True,
                                    copy=False,
                                    states={'draft':[('readonly', False)]}),
        'internal_number_isa':fields.many2one('account.invoice.cancel.isa',
                                    'Invoice number',
                                    readonly=True,
                                    copy=False,
                                    states={'draft':[('readonly', False)]}),
        'internal_number_isa_visible':fields.related('journal_id',
                                    'update_force_number_isa',
                                    type="boolean",
                                    relation="account.journal",
                                    store=False),
        'internal_number_visible':fields.related('journal_id',
                                    'update_force_number',
                                    type="boolean",
                                    relation="account.journal",
                                    store=False),
        }  

    # salvataggio in tabella isa_cancel dal metodo chiamato dal tasto annulla
    def action_cancel(self, cr, uid, ids, context=None):
        account_cancel_obj = self.pool.get('account.invoice.cancel.isa')
        invoice_data = self.browse(cr, uid, ids)
        for invoice in invoice_data:
            if invoice.number:
                isset_invoice = account_cancel_obj.search(cr, uid,
                                        [('number', '=', invoice.number)])
                if not isset_invoice:
                    account_cancel_obj.create(cr, uid,
                                    {'number': str(invoice.number),
                                     'journal_id': invoice.journal_id.id,
                                     'protocol_number': invoice.f_protocol_number,
                                     })            
        
                self.write(cr, uid, ids, {'force_protocol_number': invoice.f_protocol_number})
        
        return super(account_invoice_cancel_management,
                                    self).action_cancel(cr, uid, ids, context=context)

    # copia valore internal_number_isa(che potrebbe essere store = false)
    # in internal number
    # salvataggio ed eventuale cancellazione record da tabella cancel_isa
    # pulsante invoice_open che agisce sul workflow.
    def invoice_open(self, cr, uid, ids, context):
        values = self.read(cr, uid, ids,['internal_number_isa','internal_number'],context=context)
        invoice_cancel_isa = False
        t_internal_num_isa = values[0]['internal_number_isa']
        account_cancel_obj = self.pool.get('account.invoice.cancel.isa')
        account_cancel_ids = []
        if t_internal_num_isa:
            t_number = t_internal_num_isa[1]
            invoice_cancel_isa = self.write(cr, uid, ids,
                                        {'internal_number':str(t_number),
                                         })
            if invoice_cancel_isa :
                account_cancel_ids = account_cancel_obj.search(cr, uid,
                                        [('number', '=', str(t_number))])
        else :
            t_internal_num = values[0]['internal_number']
            if t_internal_num:
                account_cancel_ids = account_cancel_obj.search(cr, uid,
                                        [('number', '=', str(t_internal_num))])
        if account_cancel_ids:
            account_cancel_obj.unlink(cr, uid, account_cancel_ids)

        return super(account_invoice_cancel_management,
                     self).invoice_open(cr, uid, ids, context)

    # removed control over the internal_number
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        invoices = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t_invoice in invoices:
            if t_invoice['state'] in ('draft', 'cancel'):
                unlink_ids.append(t_invoice['id'])
            else:
                raise openerp.exceptions.Warning(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))

        self.write(cr, uid, unlink_ids, {'internal_number':None},context=context)
        return super(account_invoice_cancel_management, self).unlink(cr, uid, unlink_ids, context=context)

    def action_number(self, cr, uid, ids, context=None):
        results=self.read(cr,uid,ids,['journal_id','company_id','internal_number'])
        journal_id = results[0]['journal_id'][0]
        company_id = results[0]['company_id'][0]
        internal_number = results[0]['internal_number']
        if internal_number:
            cr.execute('''
                    SELECT COUNT(inv.id)
                    FROM 
                        (
                            SELECT id
                            FROM account_invoice
                            WHERE journal_id = %s AND company_id = %s AND internal_number = %s
                        ) AS subquery, account_invoice AS inv
                    WHERE inv.id = subquery.id AND inv.id != %s
                    ''',
                (journal_id,company_id,internal_number,ids[0]))

            tmp = cr.fetchall()[0][0]
            if tmp > 0:
                raise orm.except_orm(_('Warning!'),
                                     _('Another invoice with this number already exists.\nPlease, delete this invoice.'))
        return super(account_invoice_cancel_management,
                     self).action_number(cr, uid, ids, context)
