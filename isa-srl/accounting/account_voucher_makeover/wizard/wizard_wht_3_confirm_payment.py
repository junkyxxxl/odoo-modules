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


class wizard_confirm_payment_wht(orm.TransientModel):
    
    _name = 'wizard.confirm.payment.wht'
    _description = 'Wizard Confirm Payment Wht'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        return company_id

    _columns = {
        'period_id': fields.many2one('account.period',
                                     'Period'),
        'bank_id': fields.many2one('res.partner.bank',
                                   'bank'),
        'journal_id':fields.many2one('account.journal', 'Journal'),
        'maturity': fields.date('Maturity Maximum'),
        'operation_date': fields.date('Operation Date',
                                      required=True),
        'currency_date': fields.date('Currency Date'),
        'document_date': fields.date('Document Date',
                                     required=True,
                                     states={'draft':[('readonly', False)]},
                                     select=True),
        'line_ids': fields.one2many('wizard.confirm.payment.wht.line',
                                    'confirm_payment_wht_id'),

        'company_id': fields.many2one('res.company',
                                      'Company',
                                      required=True),
    }
    
    _defaults = {'company_id': _get_default_company,
                 }
    
    def create_voucher(self, cr, uid, ids, context=None):
        account_voucher_obj = self.pool.get('account.voucher')
        move_obj = self.pool.get('account.move.line')
        payment_id = self.browse(cr, uid, ids[0])
        for line_id in payment_id.line_ids:
            move_id = move_obj.browse(cr, uid, line_id.move_line_id.id)
            if(move_id.partner_id.property_account_payable.id == move_id.partner_id.wht_account_id.account_id.id):
                raise orm.except_orm(_('Error!'), _('Il conto per la ritenuta di acconto è lo stesso di quello del partner'))
        if context.get('wizard_id', None):
            t_wiz = context.get('wizard_id', None)
            context.update({'bank_id':self.browse(cr,uid,t_wiz).bank_id.id})
            context.update({'period_id':self.browse(cr,uid,t_wiz).period_id.id})                
        t_res = account_voucher_obj.create_validate_wht_voucher(cr, uid, ids, context)
        return t_res
    
    def set_confirm_values(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_values_confirm_wht_view')
        t_cp = self.browse(cr, uid, ids[0])
        context.update({
            'default_maturity': t_cp.maturity,
            'default_operation_date': t_cp.operation_date,
            'default_currency_date': t_cp.currency_date,
        })
      
        view_id = result and result[1] or False

        return {
              'name': _("Conferma Impostazione Valori"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.values.confirm',
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
