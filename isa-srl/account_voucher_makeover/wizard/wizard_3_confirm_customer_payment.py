# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ISA s.r.l. (<http://www.isa.it>).
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


class wizard_confirm_customer_payment(orm.TransientModel):
    
    _name = 'wizard.confirm.customer.payment'
    _description = 'Wizard Confirm Customer Payment'

    _columns = {
        'period_id': fields.many2one('account.period',
                                     'Period'),
        'operation_date': fields.date('Operation Date',
                                      required=True),
        'currency_date': fields.date('Currency Date'),
        'document_date': fields.date('Document Date',
                                     required=True,
                                     states={'draft':[('readonly', False)]},
                                     select=True),
        'partner_id': fields.many2one('res.partner',
                                   'Customer'),
        'maturity': fields.date('Maturity Maximum'),
        
        'journal_id':fields.many2one('account.journal', 'Journal'),
        
        'line_ids': fields.one2many('wizard.confirm.customer.payment.line',
                                    'confirm_payment_id'),
                
        'bank_id': fields.many2one('res.partner.bank',
                                   'bank'),
        'all_customer': fields.boolean('All customers'),
        'it_customer': fields.boolean('Italian customers'),
        'ext_customer': fields.boolean('Foreign customers'),
        'riba': fields.boolean('Exclude riba')
    }

    def create_voucher(self, cr, uid, ids, context=None):
        account_voucher_obj = self.pool.get('account.voucher')
        t_res = account_voucher_obj.create_validate_customer_voucher(cr, uid, ids, context)
        return t_res

    def set_confirm_values(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_values_customer_confirm_view')
        
        t_cp = self.browse(cr, uid, ids[0])
        context.update({
            'default_partner_id': t_cp.partner_id.id,
            'default_all_customer': t_cp.all_customer,
            'default_it_customer': t_cp.it_customer,
            'default_ext_customer': t_cp.ext_customer,
            'default_riba': t_cp.riba,
            'default_maturity': t_cp.maturity,
            'default_operation_date': t_cp.operation_date,
            'default_currency_date': t_cp.currency_date,
        })
        view_id = result and result[1] or False

        return {
              'name': _("Conferma Impostazione Valori"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.values.customer.confirm',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'target': 'new',
              }
    
    _defaults = {
                 'operation_date': fields.date.context_today,
                 'document_date': fields.date.context_today,
                 'currency_date': fields.date.context_today,
                 }
