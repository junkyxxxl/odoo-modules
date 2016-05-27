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
from openerp.tools.translate import _


class AccountInvoice(orm.Model):

    _inherit = 'account.invoice'

    def make_in_refund(self, cr, uid, ids, context):
        user_obj = self.pool.get('res.users')
        sequence_obj = self.pool.get('ir.sequence')
        journal_obj = self.pool.get('account.journal')

        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        t_invoice_id = ids[0]
        t_invoice = self.browse(cr, uid, t_invoice_id)
        journal_ids = journal_obj.search(cr, uid,
                                         [('type', '=', 'purchase_refund'),
                                          ('company_id', '=', company_id)],
                                         limit=1)
        if not journal_ids:
            raise orm.except_orm(_('Error!'),
                                 _('Non è definito nessun sezionale per le note di credito fornitori'))

        self.check_journal_vat_registry(cr, uid, journal_ids[0])
        t_journal_data = journal_obj.browse(cr, uid, journal_ids[0])
        t_seq_id = t_journal_data.iva_registry_id.sequence_iva_registry_id.id

        t_new_protocol_number = sequence_obj.next_by_id(cr, uid, t_seq_id)

        new_refund = {'journal_id': journal_ids[0],
                      'type': 'in_refund',
                      'date_invoice': t_invoice.date_invoice,
                      'protocol_number': t_new_protocol_number
                      }

        new_invoice_id = self.copy(cr, uid, t_invoice_id, new_refund)

        self.write(cr, uid, [t_invoice_id], {'draft_refund': True
                                             })

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_accredia',
                                              'view_invoice_supplier_makeover_accredia_form')
        view_id = result and result[1] or False

        return {'name': _("New In Refund"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'res_id': int(new_invoice_id),
                'view_id': view_id,
                'context': context,
                'target': 'inlineview',
                }

    _columns = {'request_type': fields.many2one('account.invoice.classification',
                                                'Request Type'),
                'department_id': fields.related('journal_id',
                                                'department_id',
                                                relation='hr.department',
                                                store=True,
                                                readonly=True,
                                                type='many2one',
                                                string='Department',),
                'doc_type_accredia': fields.char('Document Type', size=30),
                'draft_refund': fields.boolean('Draft Refund Created'),
                'invoice_number': fields.char('Invoice Number',
                                              size=32),
                }

    _defaults = {'draft_refund': False,
                 }

    _sql_constraints = [
        ('comment', 'CHECK (length(comment)<=200)', 'Size of the comment can never be more than 200 !'),
    ]

    def check_date_invoice(self, cr, uid, vals, journal_id):
        journal_obj = self.pool.get('account.journal')
        journal_data = journal_obj.browse(cr, uid, journal_id)

        t_registry_id = journal_data.iva_registry_id.id
        t_invoice_ids = self.search(cr, uid,
                                    [('journal_id.iva_registry_id', '=', t_registry_id)],
                                    order='create_date desc',
                                    limit=1,
                                    context=None)
        if t_invoice_ids and 'registration_date' in vals and vals['registration_date']:
            # TODO: da rivedere recupero last invoice
            t_last_invoice = self.browse(cr, uid, t_invoice_ids[0])
            t_new_date = vals['registration_date']
            t_last_date = t_last_invoice.registration_date
            if t_new_date < t_last_date:
                raise orm.except_orm(_('Error!'),
                                     _('Invoice Date can not be less than: %s') % (t_last_date))
        return True

    def check_vat_registry_sequence(self, cr, uid, journal_id):
        journal_obj = self.pool.get('account.journal')
        t_journal = journal_obj.browse(cr, uid, journal_id)

        t_vat_reg = t_journal.iva_registry_id
        t_seq = t_vat_reg.sequence_iva_registry_id
        if not t_seq:
            raise orm.except_orm(_('Error!'),
                                 _('Non è stata definita alcuna sequenza di registro iva per il sezionale %s') % (t_journal.name))

        t_seq_implementation = t_seq.implementation
        if t_seq_implementation == 'standard':
            raise orm.except_orm(_('Error!'),
                                 _('La sequenza di ingresso del registro IVA %s deve avere campo implementation impostato a: Nessun Gap') % (t_vat_reg.name))
        return True

    def check_journal_vat_registry(self, cr, uid, journal_id):
        journal_obj = self.pool.get('account.journal')
        t_journal = journal_obj.browse(cr, uid, journal_id)
        if not t_journal.iva_registry_id:
            raise orm.except_orm(_('Error!'), 
                                 _('You must define a Vat Registry for this journal: %s') % (t_journal.name))
        return True

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        res = super(AccountInvoice, self).create(cr, uid, vals, context)

        t_invoice_ids = []

        t_invoice_data = self.browse(cr, uid, res)
        if t_invoice_data.journal_id:
            t_journal = t_invoice_data.journal_id

            self.check_journal_vat_registry(cr, uid, t_journal.id)
            self.check_date_invoice(cr, uid, vals, t_journal.id)
            self.check_vat_registry_sequence(cr, uid, t_journal.id)
            if 'protocol_number' in vals:
                t_protocol_number = vals['protocol_number']

                if t_journal and t_journal.iva_registry_id:
                    t_vat_reg = t_journal.iva_registry_id.id
                    t_invoice_ids = self.search(cr,
                                                uid,
                                                [('protocol_number', '=', t_protocol_number),
                                                 ('journal_id.iva_registry_id', '=', t_vat_reg)],
                                                limit=1)
                    vals['draft_refund'] = False
            if 'protocol_number' not in vals or not vals['protocol_number'] or t_invoice_ids:

                t_seq = t_journal.iva_registry_id.sequence_iva_registry_id
                if not t_seq:
                    raise orm.except_orm(_('Error!'),
                                         _('Non è stata definita alcuna sequenza di registro iva per il sezionale %s') % (t_journal.name))

                sequence_obj = self.pool.get('ir.sequence')
                t_new_protocol_number = sequence_obj.next_by_id(cr, uid, t_seq.id)
                self.write(cr, uid, [res], {'protocol_number': t_new_protocol_number
                                             })

            # name
            new_name = sequence_obj.next_by_id(cr, uid, t_journal.sequence_id.id, context)
            self.write(cr, uid, [res], {'invoice_number': new_name,
                                         })
        return res

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]

        if len(ids) > 1:
            raise orm.except_orm(_('Error!'),
                                 _('You can only Delete one invoice at a time'))

        seq_obj = self.pool.get('ir.sequence')
        invoice_id = ids[0]
        t_invoice = self.browse(cr, uid, invoice_id)
        t_journal_id = t_invoice.journal_id.id

        self.check_journal_vat_registry(cr, uid, t_journal_id)

        t_registry_id = t_invoice.journal_id.iva_registry_id.id
        t_invoice_ids = self.search(cr, uid, [('journal_id.iva_registry_id', '=', t_registry_id)],
                                    order='create_date desc',
                                    limit=1,
                                    context=None)
        if t_invoice_ids:
            t_last_invoice_id = t_invoice_ids[0]
            t_last_invoice = self.browse(cr, uid, t_last_invoice_id)
            t_max_protocol_number = t_last_invoice.protocol_number
            if invoice_id != t_last_invoice_id:
                raise orm.except_orm(_('Error!'),
                                     _('You can only Delete the Invoice with Protocol Number: %s') % (t_max_protocol_number))

        seq = t_invoice.journal_id.iva_registry_id.sequence_iva_registry_id
        if seq.implementation == 'no_gap':
            seq_obj.write(cr, uid, [seq.id], {'number_next': t_max_protocol_number
                                              })
        res = super(AccountInvoice, self).unlink(cr, uid, ids, context)
        return res

    def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
        if context is None:
            context = {}
        result = super(AccountInvoice, self).onchange_journal_id(cr, uid, ids, journal_id, context)

        result['value']['department_id'] = None

        if journal_id:
            journal_data = self.pool.get('account.journal').browse(cr, uid, journal_id)
            if journal_data.department_id:
                result['value']['department_id'] = journal_data.department_id.id

        return result

    def onchange_department_id(self, cr, uid, ids, invoice_type, partner_id,
                               date_invoice=False, payment_term=False,
                               partner_bank_id=False, company_id=False,
                               department_id=False, context=None):

        result = super(AccountInvoice,
                       self).onchange_partner_id(cr, uid, ids,
                                                 invoice_type, partner_id,
                                                 date_invoice=date_invoice,
                                                 payment_term=payment_term,
                                                 partner_bank_id=partner_bank_id,
                                                 company_id=company_id)
        if 'value' not in result:
            return result
        result['value']['partner_bank_id'] = None
        bank_id = None
        bank_id_dep = None
        bank_id_nodep = None
        if department_id:
            if partner_id:
                p = self.pool.get('res.partner').browse(cr, uid, partner_id)
                if invoice_type in ('in_invoice', 'in_refund'):
                    for t_bank in p.bank_ids:
                        if t_bank.department_id:
                            if department_id == t_bank.department_id.id:
                                bank_id_dep = t_bank.id
                                break
                        else:
                            bank_id_nodep = t_bank.id

            bank_id = bank_id_nodep
            if bank_id_dep:
                bank_id = bank_id_dep

            if bank_id:
                result['value']['partner_bank_id'] = bank_id

            if partner_bank_id != bank_id:
                to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
                result['value'].update(to_update['value'])

            dep_obj = self.pool.get('hr.department')
            dep_data = dep_obj.browse(cr, uid, department_id)
            t_sale_journal = dep_data.sale_journal_id
            t_purchase_journal = dep_data.purchase_journal_id
            if not t_sale_journal or not t_purchase_journal:
                raise orm.except_orm(_('Error!'),
                                     _('Bisogna prima impostare i campi Sezionale in %s') % (dep_data.name))
            result['value']['journal_id'] = t_sale_journal.id
            if invoice_type in ('in_invoice', 'in_refund'):
                result['value']['journal_id'] = t_purchase_journal.id

        return result
